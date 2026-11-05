#!/usr/bin/env python3
"""
[Step 6] 비정형 텍스트 · 로그 · 문서 파일 패턴 및 에러/키워드 빈도 분석기
"""
from __future__ import annotations
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


def analyze_texts_and_logs(text_paths: List[Path], root: Path) -> List[str]:
    if not text_paths:
        return []
    insights: List[str] = []
    err_counter = Counter()
    total_lines = 0
    for p in text_paths[:50]:
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            total_lines += len(lines)
            for ln in lines[:20000]:
                if re.search(r"\b(ERROR|WARN|WARNING|FAIL|EXCEPTION|CRITICAL|TIMEOUT)\b", ln, re.I):
                    m = re.search(r"\b(ERROR|WARN|WARNING|FAIL|EXCEPTION|CRITICAL|TIMEOUT)\b", ln, re.I)
                    if m:
                        err_counter[f"{p.name}:{m.group(1).upper()}"] += 1
        except Exception:
            continue
    insights.append(f"**[텍스트/로그 파일 감지]** 총 {len(text_paths)}개 파일 ({total_lines:,}줄)")
    if err_counter:
        top_errs = ", ".join(f"`{k}`({v}건)" for k, v in err_counter.most_common(5))
        insights.append(f"**[로그 에러/경고 키워드 분포]** {top_errs}")
    return insights
