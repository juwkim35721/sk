---
name: 7-plan
description: "확정된 SPEC.md와 ARCH_BLUEPRINTS.md를 바탕으로 클린 아키텍처 계층 구조, 단계별 알고리즘 작동 원리 및 비교표, 폴더 구조, 파일 경계 기반 슬라이스 계획을 PLAN.md에 수립하고 사용자와 조율한다. 구현 계획 단계에서 반복 사용한다."
---
# 7-plan

## 역할
확정된 `sk/work/SPEC.md`와 아키텍처 레퍼런스(`references/ARCH_BLUEPRINTS.md`)를 바탕으로 클린 아키텍처(Clean Architecture) 4계층 분리 구조, 핵심 알고리즘의 단계별 작동 원리(Step 1~3) 및 대안 비교표, 디렉토리 구조, 파일 경계별로 분리된 슬라이스 구현 계획을 `sk/work/PLAN.md`에 작성하고 사용자와 조율한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `references/ARCH_BLUEPRINTS.md`
  - `references/PLAN_TEMPLATE.md`
- 쓰기:
  - `sk/work/PLAN.md`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 레퍼런스 1: `references/ARCH_BLUEPRINTS.md`
- 레퍼런스 2: `references/PLAN_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 사용자가 선호하는 아키텍처, 특정 모듈 분리 방식, 또는 특별 구현 요청이 있는지 확인한다.
2. 초기 호출 시 `PARADIGM.md`(핵심 가치·역할별 사용자 여정·`Cut List`), `SPEC.md`, `references/ARCH_BLUEPRINTS.md`를 읽고 `references/PLAN_TEMPLATE.md` 양식에 맞춰 아래 4개 항목을 `sk/work/PLAN.md`에 작성한다. (단, `PARADIGM.md`의 `Cut List`에 명시된 과잉 기능은 슬라이스 계획에서 철저히 배제한다.)
   - 1) 클린 아키텍처 4계층(설정·DB 영속성 / 데이터셋 실제 검증·롤백 / 순수 도메인 최적화 엔진 / API·역할별 UI) 설계 및 대안 비교표
   - 2) 핵심 알고리즘의 단계별 작동 원리(`Input -> Step 1 -> Step 2 -> Step 3 -> Output`) 및 대안 알고리즘 비교표
   - 3) `.env.example`, `Dockerfile`, 준비 데이터셋(`data/datasets/`), `app/*`를 포함한 표준 폴더 구조 및 모듈 간 인터페이스 계약
   - 4) 하위 계층·모듈부터 스터브(Stub) 없이 100% 완성하여 상위 모듈이 호출하도록 구성한 **상향식(Bottom-Up) 파일 경계 슬라이스 계획(`Slice 1 ~ N`)**
3. 초기 호출 시 `sk/work/OUTBOX.md`에 아키텍처·알고리즘 핵심 작동 원리 요약과 사용자 조율 질문을 적는다.
4. 반복 호출(동일 세션 내 재호출) 시에는 변경되지 않은 기존 입력 파일들을 중복해서 다시 읽지 않고, 새로 갱신된 `sk/work/INBOX.md`의 사용자 피드백만 읽어 `sk/work/PLAN.md`를 갱신하고 변경 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
스터브(`pass`, `TODO`, 더미 반환)를 두는 Top-Down 방식을 쓰지 않고, 의존성이 없는 최하위 모듈부터 완성한 뒤 상위 모듈이 이미 완성된 하위 모듈을 호출하는 상향식(Bottom-Up) 구조로 슬라이스와 파일 경계를 설계한다.
