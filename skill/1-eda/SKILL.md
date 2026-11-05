---
name: 1-eda
description: "run_all.py 스크립트를 실행하여 데이터의 스키마, 분위수, 외래키 정합성, 이상치, 시계열 패턴, 군집화 결과 및 시각화 차트를 수집한다. 과제 시작 직후 기초 데이터 분석을 수행할 때 사용한다."
---
# 1-eda

## 역할
파이썬 분석 스크립트(`scripts/run_all.py`)를 실행하여 제공된 데이터의 정량 통계, 외래키 무결성, 이상치, 시계열 특이점, 군집화 리포트와 차트를 생성한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `README.md`
  - `data/README.md`
  - `data/*`
- 쓰기:
  - `sk/work/EDA_REPORT.md`
  - `sk/work/eda_overview.png`
  - `sk/work/eda_ml_clusters.png`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 스크립트: `python3 scripts/run_all.py`

## 작업 절차
1. `sk/work/INBOX.md`를 확인하여 사용자의 특별 분석 요청이나 집중 점검 대상 지시가 있는지 확인한다.
2. `python3 scripts/run_all.py`를 실행한다.
3. `sk/work/EDA_REPORT.md`와 차트 이미지 파일들이 생성되었는지 확인한다.
4. 발견된 주요 이상치와 핵심 특징 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
번들된 스크립트의 실행 결과를 바탕으로 핵심 수치와 이상치 유무만 `sk/work/OUTBOX.md`에 간결하게 적는다.
