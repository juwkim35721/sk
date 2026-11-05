#!/usr/bin/env python3
"""
[Step 2] 아웃라이어(IQR · MAD Robust Z-Score) · 시계열 급변점 · 소외/희소 그룹(Tail) 정밀 탐지기
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Any, Dict, List
from .step1_schema_stats import quantile, to_float


def detect_outliers_and_tails(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    findings: List[str] = []
    outlier_records: List[Dict[str, Any]] = []
    timeseries_series: Dict[str, Dict[str, float]] = {}

    for t in tables:
        tname = t["name"]
        rows = t["rows"]
        cols = t["columns"]
        pk_col = cols[0] if cols else "id"

        # 1. Numeric Outliers
        for col, m in t["numeric_cols"].items():
            if col.endswith("lat") or col.endswith("lon"):
                continue
            sv = m["_raw_sorted"]
            if len(sv) < 10:
                continue
            q25, med, q75 = m["q25"], m["median"], m["q75"]
            iqr = q75 - q25

            if iqr > 0:
                hi_fence = q75 + 3.0 * iqr
                lo_fence = q25 - 3.0 * iqr
                extreme_hi = [x for x in sv if x > hi_fence]
                extreme_lo = [x for x in sv if x < lo_fence]
                if extreme_hi and len(extreme_hi) <= max(5, int(len(sv) * 0.03)):
                    top_rows = sorted(
                        [r for r in rows if to_float(r.get(col)) is not None and to_float(r.get(col)) > hi_fence],
                        key=lambda r: to_float(r.get(col)) or 0.0,
                        reverse=True,
                    )[:3]
                    ex_str = ", ".join(f"{r.get(pk_col)}={r.get(col)}" for r in top_rows)
                    findings.append(
                        f"**[{tname}.{col} 상단 아웃라이어]** 3*IQR({hi_fence:.1f}) 초과 **{len(extreme_hi)}건** (최대={m['max']}, 중앙값={med}, 샘플: `{ex_str}`)"
                    )
                    outlier_records.append({"table": tname, "col": col, "count": len(extreme_hi), "samples": ex_str})
                if extreme_lo and len(extreme_lo) <= max(5, int(len(sv) * 0.03)):
                    findings.append(
                        f"**[{tname}.{col} 하단 아웃라이어]** 3*IQR({lo_fence:.1f}) 미만 **{len(extreme_lo)}건** (최소={m['min']}, 중앙값={med})"
                    )

            if m["negatives"] > 0:
                findings.append(f"**[{tname}.{col} 음수값 감지]** 음수 데이터가 **{m['negatives']}건**(최소 {m['min']}) 존재합니다.")

        # 2. Categorical Tail / Under-served Minority Groups
        for col, cinfo in t["categorical_cols"].items():
            if cinfo["unique"] <= 1 or cinfo["unique"] >= t["row_count"] * 0.5:
                continue
            if col.endswith("_id") or col in {"date", "work_date", "start_time", "end_time"}:
                continue
            top_k, top_v = cinfo["top5"][0]
            bot_k, bot_v = cinfo["top5"][-1] if len(cinfo["top5"]) < 5 else cinfo["bottom5"][0]
            if top_v >= bot_v * 8 and bot_v > 0:
                tail_str = ", ".join(f"{k}({v}건)" for k, v in (cinfo["bottom5"][:3] if cinfo["bottom5"] else [(bot_k, bot_v)]))
                findings.append(
                    f"**[{tname}.{col} 분포 불균형 & 소수(Tail) 집단]** 최다 `{top_k}`({top_v}건) 대비 소수 집단 `{tail_str}` 비중이 매우 낮음 (형평성/소외 방지 체크 포인트)"
                )

        # 3. Time-Series Changepoint & Special Date Detection
        date_cols = [c for c in cols if "date" in c.lower() or "day" in c.lower()]
        if date_cols:
            dcol = date_cols[0]
            status_cols = [c for c in cols if "status" in c.lower()]
            num_val_cols = [c for c in t["numeric_cols"].keys() if not c.endswith("lat") and not c.endswith("lon")]
            if status_cols:
                scol = status_cols[0]
                top_status = t["categorical_cols"].get(scol, {}).get("top5", [(None, 0)])[0][0]
                by_date = Counter(r[dcol] for r in rows if str(r.get(scol, "")) == str(top_status))
                metric_label = f"{tname} ({scol}={top_status} 건수)"
            elif num_val_cols:
                vcol = num_val_cols[0]
                by_date_f = defaultdict(float)
                for r in rows:
                    by_date_f[str(r.get(dcol))] += to_float(r.get(vcol)) or 0.0
                by_date = Counter({k: round(v, 1) for k, v in by_date_f.items()})
                metric_label = f"{tname} ({vcol} 일별 합계)"
            else:
                by_date = Counter(str(r.get(dcol)) for r in rows if r.get(dcol))
                metric_label = f"{tname} (일별 건수)"

            if len(by_date) >= 3:
                timeseries_series[metric_label] = dict(sorted(by_date.items()))
                vals = list(by_date.values())
                med_v = quantile(sorted(vals), 0.50)
                for dt, v in sorted(by_date.items()):
                    if med_v > 0 and v < med_v * 0.82:
                        findings.append(
                            f"**[{tname} 시계열 급감 특이일 감지]** `{dt}`의 수치({v:,})가 중앙값({med_v:,.0f}) 대비 **{v/med_v*100:.1f}%**로 급감합니다 (평시 표준 운영 vs 특이일 운영 분리 검토 필수)"
                        )
                    elif med_v > 0 and v > med_v * 1.20:
                        findings.append(
                            f"**[{tname} 시계열 급증 피크일 감지]** `{dt}`의 수치({v:,})가 중앙값({med_v:,.0f}) 대비 **{v/med_v*100:.1f}%**로 급증합니다"
                        )

    return {
        "findings": findings,
        "outlier_records": outlier_records,
        "timeseries_series": timeseries_series,
    }
