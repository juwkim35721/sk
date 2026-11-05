---
name: 14-qa
description: "실제 구현된 app/* 소스 코드와 제출 문서를 역추적하여 사용한 최적화 라이브러리·수식·DB·보안 구현 로직 명세표와 6대 핵심 설계·트레이드오프 검증 포인트별 3단 구조 설명문(250~400자)을 QA_CARD.md에 생성한다."
---
# 14-qa

## 역할
심층 기술 질의 및 코드 리뷰에서 사용자가 설계 의도와 구현 원리를 명확히 설명할 수 있도록, **실제 구현된 `app/*` 소스 코드를 직접 역추적**하여 1) 사용한 최적화 라이브러리/솔버 및 5대 구현 로직 명세표와, 2) 코드·제출 문서에 반영된 **6대 핵심 설계·트레이드오프 검증 포인트별 `구현 근거·한계 지목 -> 파급 영향 -> 향후 개선 계획` 3단 구조 설명문(250~400자)**을 `sk/work/QA_CARD.md`에 작성한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `app/*.py`, `app/static/*.js` (스타일시트 제외 핵심 로직 파일)
  - `<실행가이드_문서>.md`, `<협업검증_문서>.md` (`12`·`13`번 스킬이 생성한 제출 문서)
  - `sk/work/MATRIX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/DM_LOG.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `sk/work/critiques/SLICE_*.md`
  - `references/QA_CARD_TEMPLATE.md`
- 쓰기:
  - `sk/work/QA_CARD.md`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 레퍼런스: `references/QA_CARD_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 복기 카드에 반드시 포함하거나 상세히 풀어써야 할 사용자의 질문·메모가 있는지 확인한다.
2. **실제 구현된 핵심 로직 파일(`app/*.py`, `app/static/*.js` — 디자인용 `styles.css` 제외)**과 `MATRIX.md`, `PARADIGM.md`, `SPEC.md`, `DM_LOG.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `12`·`13`번 제출 문서, `SLICE_*.md`를 읽는다.
3. `references/QA_CARD_TEMPLATE.md` 양식에 맞춰 `[Part 0. 실제 코드(app/*) 기반 구현 로직 및 최적화 라이브러리 명세]`를 작성한다.
   - 특히 최적화 라이브러리(`scipy`, `ortools`, `numpy` 등)나 솔버 함수를 사용한 경우, **어떤 패키지의 어느 함수를 썼는지, 전달한 목적함수·제약 인자가 무엇인지, 내부적으로 어떻게 동작하는지**를 사용자가 완벽히 이해하고 설명할 수 있도록 상세히 풀어쓴다.
   - 아울러 5대 구현 로직(수식·임계값, 검증·롤백·`unassigned_warnings`, 재계산 경로, 그래프 Min-Max 정규화 및 선형 보간 수식, DB 스키마 및 `require_admin_role`/`to_user_dto` 화이트리스트)을 실제 코드에서 그대로 발췌해 기입한다.
4. 이어서 `[Part 1 ~ 6]`에 코드와 제출 문서에 반영된 **6대 핵심 설계·트레이드오프 검증 포인트** 각각에 대해 **`[1. 구현 위치·수식 및 한계 지목] -> [2. 파급 영향/이유] -> [3. 해결 방식 및 향후 개선 계획]` 3단 구조로 구성된 250~400자 기술 설명 문단**을 `sk/work/QA_CARD.md`에 작성하고, 핵심 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
추상적인 일반론을 배제하고 실제 `app/*` 코드의 파일명, 함수명, 라이브러리명, 수식, 상수값을 정확히 넣어 사용자가 `QA_CARD.md`만 읽고도 모든 기술 의사결정과 트레이드오프를 막힘없이 서술할 수 있게 작성한다.
