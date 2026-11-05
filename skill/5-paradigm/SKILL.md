---
name: 5-paradigm
description: "확정된 MATRIX.md를 바탕으로 서비스의 핵심 가치, 최적화 판단 기준, 역할별 타겟 페르소나, 이중 트레이드오프(시나리오 테마 및 Cut List), 사용자 여정을 PARADIGM.md에 설계하고 현업 담당자 DM으로 확정한다."
---
# 5-paradigm

## 역할
확정된 요구·제약 경계(`MATRIX.md`) 위에서 서비스가 제공할 본질적 가치와 최적화 판단 기준, 역할별 핵심 페르소나, 트레이드오프 시나리오 테마, 구현 제외 범위(Cut List), 핵심 사용자 여정을 `sk/work/PARADIGM.md`에 설계하고 사용자 및 현업 담당자와 조율하여 확정한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `README.md`
  - `sk/work/MATRIX.md`
  - `sk/work/MANAGERS.md`
  - `sk/work/EDA_REPORT.md`
  - `sk/work/EDA_SUPPLEMENT.md`
  - `sk/work/DM_LOG.md`
  - `sk/work/PARADIGM.md`
  - `references/PARADIGM_TEMPLATE.md`
- 쓰기:
  - `sk/work/PARADIGM.md`
  - `sk/work/OUTBOX.md`
  - `sk/work/DM_LOG.md`

## 번들 리소스
- 레퍼런스: `references/PARADIGM_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 사용자가 제시한 서비스 철학, 특별 가치 강조점, 또는 현업 담당자 DM 답장을 확인한다.
2. 초기 호출 시 `references/PARADIGM_TEMPLATE.md` 양식에 맞춰 1) 현행(AS-IS) 대비 핵심 가치와 최적화 판단 기준, 2) 역할별 핵심 페르소나(사각지대 수혜 집단 / 운영자 / 구성원·현장), 3) 도메인 대표 시나리오 테마(추천 기본안 포함) 및 과잉 구현 제외 목록(Cut List — 단, `MATRIX.md`의 필수 요구사항은 제외 금지), 4) 역할별 핵심 사용자 여정을 `sk/work/PARADIGM.md`에 작성한다.
3. 초기 호출 시 `sk/work/OUTBOX.md`에 [Part A. 사용자에게 묻는 최적화 기준·차별화 기능·Cut List 확인 질문]과 [Part B. 현업 담당자에게 보낼 타겟 사용자별 창출 가치, 시나리오 트레이드오프 우선순위 및 화면 표시 핵심 지표 확인용 제안형 DM]을 구분하여 작성한다. (단, 4번 스킬 DM에서 이미 거시·미시 통합 질문을 보내 답변을 받은 항목은 중복 질문하지 않고, 추가로 구체화할 가치·UX 질문만 작성한다.)
4. 반복 호출(동일 세션 내 재호출) 시에는 변경되지 않은 기존 입력 파일들을 중복해서 다시 읽지 않고, 새로 갱신된 `sk/work/INBOX.md`만 읽어 사용자 의견과 담당자 답장(미기재 항목은 추천 기본안 채택)을 반영해 `sk/work/PARADIGM.md`를 확정하고 `sk/work/DM_LOG.md`와 `sk/work/OUTBOX.md`에 확정 내역을 적는다.

## 응답 지침
운영자 역할과 구성원(이용자) 역할로 각각 접속했을 때 요구사항과 최적화 기준의 설득력을 한눈에 체감할 수 있도록 여정과 비교 지표를 설계한다.
