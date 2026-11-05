---
name: 11-add
description: "구현 도중 도출된 점진적 고도화 요구사항을 INBOX.md에서 읽어 PARADIGM.md의 핵심 가치·사용자 여정·Cut List와의 정합성을 점검한 뒤, SPEC.md를 갱신하고 PLAN.md 하단 Addendum 섹션과 BUILD_PROGRESS.md에 추가 설계·작동 원리를 기록하여 코드에 반영한다."
---
# 11-add

## 역할
구현 도중 도출된 추가 요구사항이나 기능 고도화 아이디어를 `sk/work/PARADIGM.md`(핵심 가치·타겟 페르소나 여정·`Cut List`)에 비추어 정합성을 검토한 뒤, `sk/work/SPEC.md`에 반영하고 `sk/work/PLAN.md`의 초기 설계 이력은 보존한 채 하단 `Addendum` 섹션에 추가 설계를 기록하여 구현한 다음 `sk/work/BUILD_PROGRESS.md`에 작동 원리를 업데이트한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `app/*`
- 쓰기:
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `app/*`
  - `sk/work/OUTBOX.md`

## 작업 절차
1. `sk/work/INBOX.md`의 추가 고도화 아이디어와 `sk/work/PARADIGM.md`를 함께 읽어, 추가하려는 기능이 서비스의 최우선 가치 제안, 역할별(운영자/구성원) 사용자 여정, 그리고 과잉 구현 제외 목록(`Cut List`)과 충돌하지 않는지 점검한다.
2. 패러다임과 일관성을 유지하는 방향으로 `sk/work/SPEC.md`에 추가 요구사항을 업데이트한다.
3. `sk/work/PLAN.md`의 기존 슬라이스 계획은 수정하지 않고 하단 `Addendum` 섹션에 추가 설계 내역을 덧붙인다.
4. 클린 아키텍처 경계와 무스터브(Zero-Stub) 원칙을 유지하며 관련 코드를 구현하고, 사전 정의 검증기(`verify_slice.py all`) 및 기존 테스트(`pytest`)가 깨지지 않았는지 확인한다.
5. 추가된 기능의 작동 원리(`입력 -> 처리 -> 출력` 및 수정 파일·함수명)를 `sk/work/BUILD_PROGRESS.md`와 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
`PARADIGM.md`의 핵심 가치와 사용자 여정을 해치지 않도록 추가 기능의 범위를 조율하며, `PLAN.md`의 기존 설계 이력은 덮어쓰지 않고 하단 `Addendum`에만 누적 기록한다.
