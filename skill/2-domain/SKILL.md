---
name: 2-domain
description: "과제 README.md, data/README.md, 원본 데이터, EDA_REPORT.md, 차트 이미지를 교차 분석하여 도메인 맥락상의 병목 현상과 차별화 근거를 도출한다. 결정론적 데이터 분석 직후 심화 도메인 분석이 필요할 때 사용한다."
---
# 2-domain

## 역할
과제 지시문(`README.md`), 데이터 명세서(`data/README.md`), 원본 데이터(`data/*`), 정량 리포트(`EDA_REPORT.md`), 차트 이미지(`eda_*.png`)를 종합 분석하여 도메인 특화 인사이트와 핵심 기능 설계 근거를 도출한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `README.md`
  - `data/README.md`
  - `data/*`
  - `sk/work/EDA_REPORT.md`
  - `sk/work/eda_overview.png`
  - `sk/work/eda_ml_clusters.png`
- 쓰기:
  - `sk/work/EDA_SUPPLEMENT.md`
  - `sk/work/OUTBOX.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 사용자가 추가로 분석을 지시한 도메인 관심사나 특별 요청이 있는지 확인한다.
2. `README.md`의 업무 규칙, `data/README.md`의 컬럼/단위 정의, `sk/work/EDA_REPORT.md`, 차트 이미지를 함께 확인한다.
3. 차트에서 분포의 변곡점, 군집 경계, 극단적 소수 구간을 판독한다.
4. 원본 데이터와 업무 규칙을 대조하여 현행 운영의 구조적 문제점과 서비스 차별화 기능의 데이터 근거를 `sk/work/EDA_SUPPLEMENT.md`에 작성하고, 핵심 요약만 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
기초 통계를 반복해서 적지 말고, 비즈니스 규칙과 데이터를 결합했을 때만 알 수 있는 심층 인사이트와 구체적 수치 근거만 기록한다.
