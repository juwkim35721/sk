#!/usr/bin/env python3
"""
[Step 5] 다중 시각화 대시보드 생성기 (`eda_overview.png` & `eda_ml_clusters.png`)
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List


def generate_visual_dashboards(
    tables: List[Dict[str, Any]],
    ts_data: Dict[str, Dict[str, float]],
    ml_res: Dict[str, Any],
    work_dir: Path,
) -> List[str]:
    generated: List[str] = []
    try:
        import warnings
        warnings.filterwarnings('ignore')
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['axes.unicode_minus'] = False
    except Exception:
        return generated

    out_overview = work_dir / "eda_overview.png"
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Automated Data & Anomaly Overview (sk/eda)", fontsize=14, fontweight="bold")

        ax = axes[0, 0]
        sp = ml_res.get("spatial_plot_data", {})
        if sp.get("demand_pts"):
            ex = [p[1] for p in sp["demand_pts"]]
            ey = [p[0] for p in sp["demand_pts"]]
            ax.scatter(ex, ey, s=10, alpha=0.35, c="#3b82f6", label=f"Demand Points ({len(ex)})")
            if sp.get("cand_nodes"):
                cx = [p[1] for p in sp["cand_nodes"]]
                cy = [p[0] for p in sp["cand_nodes"]]
                ax.scatter(cx, cy, s=18, alpha=0.45, c="#9ca3af", marker="^", label=f"Candidate Nodes ({len(cx)})")
            if sp.get("active_nodes"):
                ax_x = [p[1] for p in sp["active_nodes"]]
                ax_y = [p[0] for p in sp["active_nodes"]]
                ax.scatter(ax_x, ax_y, s=42, alpha=0.95, c="#ef4444", marker="o", label=f"Active Nodes ({len(ax_x)})")
            ax.set_title("Spatial Distribution: Demand vs Active/Candidate Nodes")
            ax.set_xlabel("Longitude / X")
            ax.set_ylabel("Latitude / Y")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.25)
        else:
            ax.text(0.5, 0.5, "No Lat/Lon Columns Detected", ha="center", va="center")

        ax = axes[0, 1]
        if ts_data:
            label, series = next(iter(ts_data.items()))
            xs = list(series.keys())
            ys = list(series.values())
            ax.plot(range(len(xs)), ys, marker="o", color="#10b981", linewidth=2)
            ax.set_xticks(range(len(xs)))
            ax.set_xticklabels([x[-5:] for x in xs], rotation=45, fontsize=8)
            ax.set_title(f"Time-Series Trend & Anomaly Date ({label.split()[0]})")
            ax.grid(True, alpha=0.25)
        else:
            ax.text(0.5, 0.5, "No Time-Series Columns Detected", ha="center", va="center")

        ax = axes[1, 0]
        d_act = ml_res.get("nearest_dists_active", [])
        d_all = ml_res.get("nearest_dists_all", [])
        if d_act:
            s_act = sorted(d_act)
            y_act = [(i + 1) / len(s_act) * 100 for i in range(len(s_act))]
            ax.plot(s_act, y_act, color="#ef4444", linewidth=2, label="Active Nodes Only")
            if d_all:
                s_all = sorted(d_all)
                y_all = [(i + 1) / len(s_all) * 100 for i in range(len(s_all))]
                ax.plot(s_all, y_all, color="#2563eb", linewidth=2, linestyle="--", label="With Candidate Nodes Open")
            ax.axvline(1000, color="#f59e0b", linestyle=":", label="1km Threshold")
            ax.set_title("Nearest Node Access Distance CDF (m)")
            ax.set_xlabel("Straight-Line Distance (m)")
            ax.set_ylabel("Cumulative % of Demand")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.25)
        else:
            ax.text(0.5, 0.5, "No Distance Distribution", ha="center", va="center")

        ax = axes[1, 1]
        plotted_cat = False
        for t in tables:
            for col, cinfo in t["categorical_cols"].items():
                if 3 <= cinfo["unique"] <= 25 and not col.endswith("_id"):
                    items = cinfo["_counter"].most_common(12)
                    labels = [str(k).encode("ascii", "ignore").decode("ascii")[:10] or f"Group_{i+1}" for i, (k, _) in enumerate(items)]
                    vals = [v for _, v in items]
                    ax.barh(range(len(labels))[::-1], vals, color="#6366f1")
                    ax.set_yticks(range(len(labels))[::-1])
                    ax.set_yticklabels(labels, fontsize=8)
                    ax.set_title(f"Category Balance: {t['name']}.{col}")
                    ax.grid(True, axis="x", alpha=0.25)
                    plotted_cat = True
                    break
            if plotted_cat:
                break

        plt.tight_layout(rect=[0, 0.02, 1, 0.95])
        fig.savefig(out_overview, dpi=130)
        plt.close(fig)
        generated.append(out_overview.as_posix())
    except Exception:
        pass

    sp = ml_res.get("spatial_plot_data", {})
    if sp.get("demand_pts") and sp.get("labels"):
        out_ml = work_dir / "eda_ml_clusters.png"
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            pts = sp["demand_pts"]
            lbls = sp["labels"]
            centers = sp.get("centers", [])
            palette = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6"]
            for cid in sorted(set(lbls)):
                c_pts = [p for p, l in zip(pts, lbls) if l == cid]
                ax.scatter(
                    [p[1] for p in c_pts],
                    [p[0] for p in c_pts],
                    s=14,
                    alpha=0.6,
                    color=palette[cid % len(palette)],
                    label=f"Cluster #{cid+1} (n={len(c_pts)})",
                )
            if centers:
                ax.scatter(
                    [c[1] for c in centers],
                    [c[0] for c in centers],
                    s=140,
                    c="#111827",
                    marker="X",
                    label="ML Cluster Centroids",
                )
            ax.set_title("ML K-Means++ Demand Clusters & Centroids")
            ax.set_xlabel("Longitude / X")
            ax.set_ylabel("Latitude / Y")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.25)
            plt.tight_layout()
            fig.savefig(out_ml, dpi=130)
            plt.close(fig)
            generated.append(out_ml.as_posix())
        except Exception:
            pass

    return generated
