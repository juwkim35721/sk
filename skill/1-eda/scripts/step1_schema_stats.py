#!/usr/bin/env python3
"""
[Step 1] 다중 포맷 로더 · 스키마 · 정밀 분위수 · 외래키(FK) 조인 무결성 분석기
지원 포맷: CSV, TSV, JSON, JSONL, SQLite (.db, .sqlite)
"""
from __future__ import annotations
import csv
import json
import math
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

IGNORE_DIRS = {".git", ".agents", ".codex", "sk", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}


def discover_files(root: Path) -> Dict[str, List[Path]]:
    found = {"tabular": [], "sqlite": [], "images": [], "texts": []}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        suf = p.suffix.lower()
        if suf in {".csv", ".tsv", ".json", ".jsonl"}:
            if p.name not in {"package.json", "package-lock.json", "tsconfig.json"}:
                found["tabular"].append(p)
        elif suf in {".db", ".sqlite", ".sqlite3"}:
            found["sqlite"].append(p)
        elif suf in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}:
            found["images"].append(p)
        elif suf in {".log", ".txt", ".md"} and p.name.upper() not in {"README.MD", "AGENTS.MD"}:
            found["texts"].append(p)
    return found


def load_tabular_file(path: Path) -> List[Dict[str, Any]]:
    suf = path.suffix.lower()
    rows: List[Dict[str, Any]] = []
    try:
        if suf in {".csv", ".tsv"}:
            delim = "\t" if suf == ".tsv" else ","
            with path.open("r", encoding="utf-8-sig", errors="replace") as f:
                reader = csv.DictReader(f, delimiter=delim)
                for r in reader:
                    rows.append(dict(r))
        elif suf == ".jsonl":
            with path.open("r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            rows.append(obj)
        elif suf == ".json":
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, list) and data and isinstance(data[0], dict):
                rows = data
            elif isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list) and v and isinstance(v[0], dict):
                        rows = v
                        break
    except Exception:
        pass
    return rows


def load_sqlite_tables(db_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    tables: Dict[str, List[Dict[str, Any]]] = {}
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        tnames = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        for t in tnames:
            rows = [dict(r) for r in cur.execute(f"SELECT * FROM `{t}` LIMIT 200000").fetchall()]
            if rows:
                tables[f"{db_path.name}::{t}"] = rows
        conn.close()
    except Exception:
        pass
    return tables


def to_float(val: Any):
    if val is None or val == "" or isinstance(val, bool):
        return None
    try:
        v = float(str(val).replace(",", "").strip())
        return None if (math.isnan(v) or math.isinf(v)) else v
    except Exception:
        return None


def quantile(sorted_vals: List[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = (len(sorted_vals) - 1) * q
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] * (hi - idx) + sorted_vals[hi] * (idx - lo)


def skewness(vals: List[float], mean: float, std: float) -> float:
    if len(vals) < 3 or std <= 1e-12:
        return 0.0
    n = len(vals)
    return sum(((x - mean) / std) ** 3 for x in vals) / n


def analyze_table_schema(rel_name: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    cols = list(rows[0].keys()) if rows else []
    n = len(rows)
    seen_hashes = set()
    dup_count = 0
    for r in rows[:50000]:
        sig = tuple(str(r.get(c, "")) for c in cols)
        if sig in seen_hashes:
            dup_count += 1
        else:
            seen_hashes.add(sig)

    num_stats: Dict[str, Dict[str, Any]] = {}
    cat_stats: Dict[str, Dict[str, Any]] = {}

    for col in cols:
        raw_vals = [r.get(col) for r in rows]
        nulls = sum(1 for v in raw_vals if v is None or str(v).strip() == "")
        non_null = [v for v in raw_vals if v is not None and str(v).strip() != ""]
        fvals = [to_float(v) for v in non_null]
        valid_f = [v for v in fvals if v is not None]

        if non_null and len(valid_f) / len(non_null) >= 0.85:
            sv = sorted(valid_f)
            mean = sum(sv) / len(sv)
            var = sum((x - mean) ** 2 for x in sv) / max(1, len(sv))
            std = math.sqrt(var)
            skew = skewness(sv, mean, std)
            num_stats[col] = {
                "count": len(sv),
                "nulls": nulls,
                "min": round(sv[0], 4),
                "p05": round(quantile(sv, 0.05), 4),
                "q25": round(quantile(sv, 0.25), 4),
                "median": round(quantile(sv, 0.50), 4),
                "mean": round(mean, 4),
                "q75": round(quantile(sv, 0.75), 4),
                "p90": round(quantile(sv, 0.90), 4),
                "p99": round(quantile(sv, 0.99), 4),
                "max": round(sv[-1], 4),
                "std": round(std, 4),
                "skew": round(skew, 2),
                "zeros": sum(1 for x in sv if x == 0),
                "negatives": sum(1 for x in sv if x < 0),
                "_raw_sorted": sv,
            }
        else:
            svals = [str(v).strip() for v in non_null]
            cnt = Counter(svals)
            top5 = cnt.most_common(5)
            bottom5 = cnt.most_common()[:-6:-1] if len(cnt) > 5 else []
            cat_stats[col] = {
                "count": len(svals),
                "nulls": nulls,
                "unique": len(cnt),
                "top5": top5,
                "bottom5": bottom5,
                "_counter": cnt,
            }

    return {
        "file": rel_name,
        "name": Path(rel_name).name,
        "row_count": n,
        "dup_rows": dup_count,
        "columns": cols,
        "numeric_cols": num_stats,
        "categorical_cols": cat_stats,
        "rows": rows,
    }


def analyze_foreign_keys(tables: List[Dict[str, Any]]) -> List[str]:
    insights: List[str] = []
    masters: Dict[str, Tuple[str, set]] = {}
    for t in tables:
        for col, cinfo in t["categorical_cols"].items():
            if (col.endswith("_id") or col.endswith("_code")) and cinfo["unique"] == t["row_count"] and t["row_count"] > 0:
                masters[col] = (t["name"], set(cinfo["_counter"].keys()))

    for t in tables:
        for col, cinfo in t["categorical_cols"].items():
            if col in masters and masters[col][0] != t["name"]:
                master_table, master_set = masters[col]
                used_set = set(cinfo["_counter"].keys())
                orphans = used_set - master_set
                unused = master_set - used_set
                if orphans:
                    sample_o = ", ".join(sorted(list(orphans))[:5])
                    insights.append(
                        f"**[외래키 참조(FK) 주의]** `{t['name']}.{col}` 값 중 마스터(`{master_table}`)에 없는 ID가 **{len(orphans)}개** 존재합니다: `{sample_o}` (별도 마스터 테이블에 분리 정의된 엔티티 ID인지 확인 필수)"
                    )
                if unused:
                    insights.append(
                        f"**[미사용 마스터 엔티티(Cold ID)]** `{master_table}.{col}` 전체 {len(master_set)}개 중 `{t['name']}`에 한 번도 등장하지 않는 항목이 **{len(unused)}개** 있습니다."
                    )
    return insights
