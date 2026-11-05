#!/usr/bin/env python3
"""
[Step 3] 머신러닝 군집화(K-Means++) · 공간 커버리지/사각지대 탐색 · 후보 거점 추천 · 상관관계/네트워크 비대칭 분석기
"""
from __future__ import annotations
import math
import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple
from .step1_schema_stats import quantile, to_float


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def kmeans_2d(points: List[Tuple[float, float]], k: int = 6, max_iter: int = 30) -> Tuple[List[int], List[Tuple[float, float]]]:
    if not points or k <= 0:
        return [], []
    k = min(k, len(points))
    rng = random.Random(42)
    centers = [points[rng.randrange(len(points))]]
    while len(centers) < k:
        dists = [min((px - cx) ** 2 + (py - cy) ** 2 for cx, cy in centers) for px, py in points]
        total = sum(dists)
        if total <= 0:
            centers.append(points[rng.randrange(len(points))])
            continue
        thresh = rng.uniform(0, total)
        acc = 0.0
        for pt, d in zip(points, dists):
            acc += d
            if acc >= thresh:
                centers.append(pt)
                break

    labels = [0] * len(points)
    for _ in range(max_iter):
        changed = False
        clusters: List[List[Tuple[float, float]]] = [[] for _ in range(k)]
        for idx, (px, py) in enumerate(points):
            best_c = min(range(k), key=lambda c: (px - centers[c][0]) ** 2 + (py - centers[c][1]) ** 2)
            if labels[idx] != best_c:
                labels[idx] = best_c
                changed = True
            clusters[best_c].append((px, py))
        for c in range(k):
            if clusters[c]:
                centers[c] = (
                    sum(p[0] for p in clusters[c]) / len(clusters[c]),
                    sum(p[1] for p in clusters[c]) / len(clusters[c]),
                )
        if not changed:
            break
    return labels, centers


def _find_coord_cols(cols: List[str]) -> Optional[Tuple[str, str]]:
    lat_c = next((c for c in cols if c.lower().endswith("lat") or c.lower() == "latitude"), None)
    lon_c = next((c for c in cols if c.lower().endswith("lon") or c.lower().endswith("lng") or c.lower() == "longitude"), None)
    if lat_c and lon_c:
        return lat_c, lon_c
    return None


def _find_active_col(cols: List[str]) -> Optional[str]:
    for c in cols:
        cl = c.lower()
        if cl in {"is_active", "active", "enabled", "status", "available"} or cl.endswith("_service") or cl.endswith("_active"):
            return c
    return None


def _find_region_col(cols: List[str]) -> Optional[str]:
    for c in cols:
        cl = c.lower()
        if any(k in cl for k in ("region", "zone", "area", "group", "sigungu", "dong", "district", "sector")):
            return c
    return None


def run_ml_and_spatial_analysis(tables: List[Dict[str, Any]]) -> Dict[str, Any]:
    ml_insights: List[str] = []
    cluster_summary: List[Dict[str, Any]] = []
    nearest_dists_active: List[float] = []
    nearest_dists_all: List[float] = []
    correlations: List[str] = []
    recommended_new_nodes: List[Dict[str, Any]] = []
    spatial_plot_data: Dict[str, Any] = {}

    coord_tables = []
    for t in tables:
        cc = _find_coord_cols(t["columns"])
        if cc and t["row_count"] >= 5:
            coord_tables.append((t, cc[0], cc[1], _find_active_col(t["columns"])))

    demand_entry = None
    node_entry = None
    for entry in sorted(coord_tables, key=lambda x: x[0]["row_count"], reverse=True):
        if entry[3] is not None and node_entry is None:
            node_entry = entry
        elif demand_entry is None:
            demand_entry = entry

    if demand_entry is None and coord_tables:
        demand_entry = coord_tables[0]

    if demand_entry:
        dem_t, d_lat_col, d_lon_col, _ = demand_entry
        dem_reg_col = _find_region_col(dem_t["columns"])
        dem_pts = []
        dem_valid_rows = []
        for r in dem_t["rows"]:
            lat, lon = to_float(r.get(d_lat_col)), to_float(r.get(d_lon_col))
            if lat is not None and lon is not None:
                dem_pts.append((lat, lon))
                dem_valid_rows.append((lat, lon, r))

        if len(dem_pts) >= 6:
            labels, centers = kmeans_2d(dem_pts, k=6)
            c_counts = Counter(labels)
            c_regions = defaultdict(Counter)
            for lbl, (_, _, r) in zip(labels, dem_valid_rows):
                reg = str(r.get(dem_reg_col) if dem_reg_col else "기타")
                c_regions[lbl][reg] += 1
            for cid, cnt in c_counts.most_common():
                clat, clon = centers[cid]
                top_reg = ", ".join(f"{k}({v}건)" for k, v in c_regions[cid].most_common(2))
                cluster_summary.append({
                    "cluster_id": f"Cluster #{cid+1}",
                    "count": cnt,
                    "ratio": f"{cnt/len(dem_pts)*100:.1f}%",
                    "center": f"({clat:.4f}, {clon:.4f})",
                    "top_regions": top_reg,
                })
            ml_insights.append(
                f"**[ML K-Means++ 공간 수요 군집화 완료]** 전체 수요 좌표 {len(dem_pts):,}건을 6개 핵심 권역 클러스터로 군집화했습니다 (최대 군집: {cluster_summary[0]['top_regions']} 중심 {cluster_summary[0]['count']}건)."
            )
            spatial_plot_data["demand_pts"] = dem_pts
            spatial_plot_data["labels"] = labels
            spatial_plot_data["centers"] = centers

        if node_entry and node_entry[0]["name"] != dem_t["name"]:
            node_t, n_lat_col, n_lon_col, act_col = node_entry
            node_id_col = node_t["columns"][0]
            node_reg_col = _find_region_col(node_t["columns"])
            active_nodes = []
            cand_nodes = []
            for s in node_t["rows"]:
                slat, slon = to_float(s.get(n_lat_col)), to_float(s.get(n_lon_col))
                if slat is None or slon is None:
                    continue
                is_act = str(s.get(act_col, "true")).lower() in ("true", "1", "yes", "y", "active") if act_col else True
                item = (slat, slon, s)
                if is_act:
                    active_nodes.append(item)
                else:
                    cand_nodes.append(item)

            spatial_plot_data["active_nodes"] = [(x[0], x[1]) for x in active_nodes]
            spatial_plot_data["cand_nodes"] = [(x[0], x[1]) for x in cand_nodes]

            all_nodes = active_nodes + cand_nodes
            far_demands = []
            for lat, lon, r in dem_valid_rows:
                if active_nodes:
                    d_act = min(haversine_m(lat, lon, s[0], s[1]) for s in active_nodes)
                    nearest_dists_active.append(d_act)
                    if d_act > 1000.0:
                        far_demands.append((lat, lon, d_act, r))
                if all_nodes:
                    d_all = min(haversine_m(lat, lon, s[0], s[1]) for s in all_nodes)
                    nearest_dists_all.append(d_all)

            if nearest_dists_active:
                sv_act = sorted(nearest_dists_active)
                sv_all = sorted(nearest_dists_all) if nearest_dists_all else sv_act
                over_1km = sum(1 for d in sv_act if d > 1000.0)
                over_1_5km = sum(1 for d in sv_act if d > 1500.0)
                ml_insights.append(
                    f"**[최근접 거점 직선 접근거리 분석]** 현행 활성 거점({len(active_nodes)}곳) 기준 평균 **{sum(sv_act)/len(sv_act):.0f}m** (중앙값 {quantile(sv_act, 0.5):.0f}m, P90 {quantile(sv_act, 0.9):.0f}m, 최대 {sv_act[-1]:.0f}m) | **1km 초과 원거리 수요 {over_1km}건({over_1km/len(sv_act)*100:.1f}%)**, 1.5km 초과 **{over_1_5km}건**"
                )
                if cand_nodes:
                    ml_insights.append(
                        f"**[후보 거점 활용 시 잠재 개선 효과]** 비활성 후보 거점({len(cand_nodes)}곳) 풀을 활용하면 평균 접근거리를 **{sum(sv_act)/len(sv_act):.0f}m -> 최저 {sum(sv_all)/len(sv_all):.0f}m**까지 단축할 수 있습니다."
                    )

            if dem_reg_col and node_reg_col:
                dem_sg = Counter(str(r.get(dem_reg_col)) for _, _, r in dem_valid_rows)
                act_sg = Counter(str(s[2].get(node_reg_col)) for s in active_nodes)
                cand_sg = Counter(str(s[2].get(node_reg_col)) for s in cand_nodes)
                for sg, ecnt in dem_sg.items():
                    if act_sg.get(sg, 0) == 0:
                        sg_dems = [(lat, lon, r) for lat, lon, r in dem_valid_rows if str(r.get(dem_reg_col)) == sg]
                        sg_cands = [(clat, clon, c) for clat, clon, c in cand_nodes if str(c.get(node_reg_col)) == sg]
                        best_sg_node_str = ""
                        if sg_dems and sg_cands:
                            best_c = min(
                                sg_cands,
                                key=lambda c: sum(haversine_m(elat, elon, c[0], c[1]) for elat, elon, _ in sg_dems) / len(sg_dems),
                            )
                            avg_d = sum(haversine_m(elat, elon, best_c[0], best_c[1]) for elat, elon, _ in sg_dems) / len(sg_dems)
                            best_sg_node_str = f" -> **최적 후보 거점 추천: `{best_c[2].get(node_id_col)}` ({best_c[2].get('name', '')}, 평균 접근거리 {avg_d:.0f}m)**"
                        ml_insights.append(
                            f"**[사각지대/미커버 권역 확인]** `{sg}` 권역 수요가 **{ecnt}건**인데 현재 활성 거점은 **0곳**입니다 (후보 거점 {cand_sg.get(sg, 0)}곳 존재{best_sg_node_str})"
                        )

            if far_demands and cand_nodes:
                rem_dems = list(far_demands)
                for rank in range(1, 6):
                    best_cand = None
                    best_rescued = []
                    best_gain = 0.0
                    for c_lat, c_lon, c_row in cand_nodes:
                        if any(r["node_id"] == c_row.get(node_id_col) for r in recommended_new_nodes):
                            continue
                        rescued = []
                        gain = 0.0
                        for elat, elon, old_d, erow in rem_dems:
                            new_d = haversine_m(elat, elon, c_lat, c_lon)
                            if new_d <= 800.0 or (old_d - new_d >= 400.0 and new_d <= 1200.0):
                                rescued.append((elat, elon, old_d, erow))
                                gain += (old_d - new_d)
                        if (len(rescued), gain) > (len(best_rescued), best_gain):
                            best_cand = c_row
                            best_rescued = rescued
                            best_gain = gain
                    if best_cand and best_rescued:
                        recommended_new_nodes.append({
                            "rank": rank,
                            "node_id": best_cand.get(node_id_col),
                            "name": best_cand.get("name", "-"),
                            "region": best_cand.get(node_reg_col, "-") if node_reg_col else "-",
                            "type": best_cand.get("type", "-"),
                            "rescued_count": len(best_rescued),
                            "avg_dist_saved_m": round(best_gain / len(best_rescued), 0),
                        })
                        rescued_ids = {id(x) for x in best_rescued}
                        rem_dems = [x for x in rem_dems if id(x) not in rescued_ids]

    edge_t = next((t for t in tables if {"from_id", "to_id"}.issubset(set(t["columns"])) and t["numeric_cols"]), None)
    if edge_t:
        val_col = next(iter(edge_t["numeric_cols"].keys()))
        pair_val = {}
        for r in edge_t["rows"]:
            u, v, m = str(r.get("from_id")), str(r.get("to_id")), to_float(r.get(val_col))
            if u and v and m is not None:
                pair_val[(u, v)] = m
        asym_pairs = []
        for (u, v), m1 in pair_val.items():
            if (v, u) in pair_val:
                m2 = pair_val[(v, u)]
                if abs(m1 - m2) >= 5.0:
                    asym_pairs.append((u, v, m1, m2, abs(m1 - m2)))
        if asym_pairs:
            asym_pairs.sort(key=lambda x: x[4], reverse=True)
            top_a = asym_pairs[0]
            ml_insights.append(
                f"**[네트워크 양방향 수치 비대칭 감지]** `{edge_t['name']}`에서 양방향(`A->B` vs `B->A`) `{val_col}` 차이가 5 이상 나는 구간이 **{len(asym_pairs)//2}쌍** 존재합니다 (최대 차이: `{top_a[0]}<->{top_a[1]}` {top_a[2]} vs {top_a[3]})."
            )
        else:
            ml_insights.append(
                f"**[네트워크 대칭성 확인]** `{edge_t['name']}`의 양방향(`from_id <-> to_id`) `{val_col}` 수치는 대칭적입니다."
            )

    for t in tables:
        ncols = [c for c in t["numeric_cols"].keys() if not c.endswith("lat") and not c.endswith("lon")]
        if len(ncols) >= 2:
            for i in range(len(ncols)):
                for j in range(i + 1, len(ncols)):
                    c1, c2 = ncols[i], ncols[j]
                    pairs = []
                    for r in t["rows"][:20000]:
                        v1, v2 = to_float(r.get(c1)), to_float(r.get(c2))
                        if v1 is not None and v2 is not None:
                            pairs.append((v1, v2))
                    if len(pairs) >= 10:
                        m1 = sum(p[0] for p in pairs) / len(pairs)
                        m2 = sum(p[1] for p in pairs) / len(pairs)
                        num = sum((p[0] - m1) * (p[1] - m2) for p in pairs)
                        d1 = math.sqrt(sum((p[0] - m1) ** 2 for p in pairs))
                        d2 = math.sqrt(sum((p[1] - m2) ** 2 for p in pairs))
                        if d1 > 0 and d2 > 0:
                            r_val = num / (d1 * d2)
                            if abs(r_val) >= 0.35:
                                correlations.append(f"`{t['name']}`: `{c1}` <-> `{c2}` 상관계수 **r = {r_val:+.2f}**")

    return {
        "ml_insights": ml_insights,
        "cluster_summary": cluster_summary,
        "recommended_new_nodes": recommended_new_nodes,
        "correlations": correlations,
        "nearest_dists_active": nearest_dists_active,
        "nearest_dists_all": nearest_dists_all,
        "spatial_plot_data": spatial_plot_data,
    }
