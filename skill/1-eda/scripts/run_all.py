#!/usr/bin/env python3
"""
결정론적 데이터 분석 및 시각화 오케스트레이터 (scripts/run_all.py)
"""
from __future__ import annotations
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from step1_schema_stats import analyze_foreign_keys, analyze_table_schema, discover_files, load_sqlite_tables, load_tabular_file
from step2_outliers_ts import detect_outliers_and_tails
from step3_ml_cluster import run_ml_and_spatial_analysis
from step4_image_media import analyze_images
from step6_text_log import analyze_texts_and_logs
from step5_visualizer import generate_visual_dashboards


def resolve_task_root(arg_str: str | None = None) -> Path:
    if arg_str:
        return Path(arg_str).resolve()
    cwd = Path(".").resolve()
    for p in [cwd] + list(cwd.parents):
        if (p / "data").exists() or (p / "sk" / "work").exists():
            return p
    for p in THIS_DIR.parents:
        if (p / "data").exists() or (p / "sk").is_dir():
            return p
    return cwd


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    target_root = resolve_task_root(args[0] if args else None)
    work_dir = target_root / "sk" / "work"
    work_dir.mkdir(parents=True, exist_ok=True)

    data_readmes = []
    for rp in sorted(target_root.rglob("README.md")):
        if any(part in {"sk", ".git", ".agents", ".codex", "node_modules"} for part in rp.parts):
            continue
        rel_rp = rp.relative_to(target_root).as_posix() if rp.is_relative_to(target_root) else rp.name
        if "data" in rel_rp.lower() or rel_rp != "README.md":
            try:
                txt = rp.read_text(encoding="utf-8", errors="replace").strip()
                if txt:
                    data_readmes.append((rel_rp, txt[:4000]))
            except Exception:
                pass

    discovered = discover_files(target_root)
    tables = []
    for p in discovered["tabular"]:
        rows = load_tabular_file(p)
        if rows:
            rel = p.relative_to(target_root).as_posix() if p.is_relative_to(target_root) else p.name
            tables.append(analyze_table_schema(rel, rows))
    for db_p in discovered["sqlite"]:
        for tname, rows in load_sqlite_tables(db_p).items():
            tables.append(analyze_table_schema(tname, rows))

    fk_insights = analyze_foreign_keys(tables)
    step2_res = detect_outliers_and_tails(tables)
    ml_res = run_ml_and_spatial_analysis(tables)
    img_res = analyze_images(discovered["images"], target_root, work_dir / "eda_image_grid.png")
    txt_insights = analyze_texts_and_logs(discovered["texts"], target_root)
    charts = generate_visual_dashboards(tables, step2_res["timeseries_series"], ml_res, work_dir)

    md = [
        "# 결정론적 데이터 분석 · 군집화 · 사각지대 리포트 (`EDA_REPORT.md`)",
        "",
        f"- **분석 테이블 수**: {len(tables)}개 | **이미지 파일 수**: {img_res['count']}개",
        f"- **생성된 차트 파일**: {', '.join(f'`{c}`' for c in charts) if charts else '없음'}",
        "",
        "## 1. 핵심 인사이트 · 사각지대 · 시계열/외래키 이상치 요약",
    ]
    all_highlights = ml_res["ml_insights"] + step2_res["findings"] + fk_insights + img_res["summary"] + txt_insights
    if all_highlights:
        for h in all_highlights:
            md.append(f"- {h}")
    else:
        md.append("- 특이 이상치가 감지되지 않았습니다.")

    if ml_res["cluster_summary"]:
        md.append("\n## 2. 머신러닝(K-Means++) 수요 권역 클러스터링 결과")
        md.append("| 권역 클러스터 | 소속 건수(비중) | 중심 좌표 (Lat, Lon) | 주요 소속 권역/그룹 |")
        md.append("| :--- | :---: | :---: | :--- |")
        for c in ml_res["cluster_summary"]:
            md.append(f"| **{c['cluster_id']}** | {c['count']:,}건 ({c['ratio']}) | `{c['center']}` | {c['top_regions']} |")

    if ml_res["recommended_new_nodes"]:
        md.append("\n## 3. 사각지대/원거리 수요 해소용 추천 신규 후보 거점 Top 5 (Greedy Set-Cover)")
        md.append("> 비활성 후보 거점 중 활성화했을 때 원거리/사각지대 수요 지점을 가장 많이 커버하는 후보 거점 순위입니다.")
        md.append("")
        md.append("| 추천 순위 | 거점 ID | 거점명 | 권역/그룹 | 유형 | 해소 건수 | 건당 평균 단축 거리 |")
        md.append("| :---: | :---: | :--- | :--- | :---: | :---: | :---: |")
        for r in ml_res["recommended_new_nodes"]:
            md.append(
                f"| **Top {r['rank']}** | `{r['node_id']}` | **{r['name']}** | {r['region']} | `{r['type']}` | **{r['rescued_count']}건** | **-{r['avg_dist_saved_m']:.0f}m** |"
            )

    if ml_res["correlations"]:
        md.append("\n## 4. 주요 수치 변수 간 상관관계 (|r| >= 0.35)")
        for corr in ml_res["correlations"]:
            md.append(f"- {corr}")

    if data_readmes:
        md.append("\n## 0. 데이터 명세서(`data/README.md`) 핵심 스키마 및 규칙 요약")
        for rpath, rtxt in data_readmes:
            md.append(f"### `{rpath}` 원문 핵심 발췌")
            md.append("```markdown")
            md.append(rtxt)
            md.append("```")

    md.append("\n## 5. 테이블별 정밀 스키마 · 7대 분위수 · 범주형 Top/Tail 통계")
    for t in tables:
        md.append(f"\n### `{t['file']}` (총 {t['row_count']:,}행, 중복 {t['dup_rows']}행)")
        md.append(f"- **컬럼 목록 ({len(t['columns'])}개)**: `{', '.join(t['columns'])}`")
        if t["numeric_cols"]:
            md.append("\n| 수치형 컬럼 | 결측 | 최소 | P5 | Q25 | 중앙값 | 평균 | Q75 | P90 | P99 | 최대 | 표준편차 | 왜도(Skew) | 음수/0 |")
            md.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
            for col, m in t["numeric_cols"].items():
                md.append(
                    f"| `{col}` | {m['nulls']} | {m['min']} | {m['p05']} | {m['q25']} | {m['median']} | {m['mean']} | {m['q75']} | {m['p90']} | {m['p99']} | {m['max']} | {m['std']} | {m['skew']} | {m['negatives']}/{m['zeros']} |"
                )
        if t["categorical_cols"]:
            md.append("\n| 범주형 컬럼 | 결측 | 고유값 수 | 최다 빈도 (Top 5) | 최소/소외 빈도 (Bottom/Tail 5) |")
            md.append("| :--- | :---: | :---: | :--- | :--- |")
            for col, m in t["categorical_cols"].items():
                t5 = ", ".join(f"{k}({v})" for k, v in m["top5"])
                b5 = ", ".join(f"{k}({v})" for k, v in m["bottom5"]) if m["bottom5"] else "-"
                md.append(f"| `{col}` | {m['nulls']} | {m['unique']} | {t5} | {b5} |")

    report_text = "\n".join(md) + "\n"
    report_path = work_dir / "EDA_REPORT.md"
    report_path.write_text(report_text, encoding="utf-8")
    print(report_text)
    print(f"\n[분석 완료] 리포트: {report_path} | 차트: {', '.join(charts)}")


if __name__ == "__main__":
    main()
