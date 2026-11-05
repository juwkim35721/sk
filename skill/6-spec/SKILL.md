---
name: 6-spec
description: "확정된 MATRIX.md, PARADIGM.md, DM_LOG.md를 하나로 통합하여 공식 요구사항 및 설계 명세서인 SPEC.md를 생성하고, OUTBOX.md의 스펙 요약 및 현업 담당자 5줄 서면 합의 DM 확인까지 완전히 마친 뒤 7번 단계로 넘어가도록 확정한다."
---
# 6-spec

## 역할
확정된 요구·제약 매트릭스(`MATRIX.md`)와 서비스 패러다임(`PARADIGM.md`), 합의 이력(`DM_LOG.md`)을 통합하여 단일 설계 명세서인 `sk/work/SPEC.md`를 작성하고, 사용자 확인 및 현업 담당자 최종 서면 합의 DM 답장까지 반영해 **7번(구현 계획)으로 넘어가기 전에 스펙을 100% 완결**한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/MANAGERS.md`
  - `sk/work/MATRIX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/DM_LOG.md`
  - `sk/work/SPEC.md`
  - `references/SPEC_TEMPLATE.md`
- 쓰기:
  - `sk/work/SPEC.md`
  - `sk/work/OUTBOX.md`
  - `sk/work/DM_LOG.md`

## 번들 리소스
- 레퍼런스: `references/SPEC_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 스펙 통합 전 사용자의 특별 지침이나 현업 담당자의 서면 합의 DM 답장(반대 의견·보완 요청)이 있는지 확인한다.
2. 초기 호출 시 `MANAGERS.md`, `MATRIX.md`, `PARADIGM.md`, `DM_LOG.md`의 확정 사항을 모두 읽고 `references/SPEC_TEMPLATE.md` 양식에 따라 타겟 뷰 구성, 확정 기능 요구사항, 하드 제약 불변식, 데이터셋 검증/상태전이/영속성 규격, 부속 스키마 규격, 시나리오 프리셋 및 제어 스펙을 통합하여 `sk/work/SPEC.md`에 작성한다.
3. 초기 호출 시 `sk/work/OUTBOX.md`에 아래 두 파트를 구분하여 출력한다.
   - **[Part A. 사용자 확인용 확정 스펙 1페이지 요약]**: 통합된 핵심 기능(`ER/IR`), 하드 제약(`EC/IC`), 상태전이·영속성(`STATE`), 제외 범위(`Cut List`)를 한눈에 볼 수 있게 요약한다.
   - **[Part B. 현업 담당자 전송용 5줄 최종 서면 합의 요약 DM 초안]**: `MANAGERS.md`의 담당자 구성(1명 또는 복수 담당자별 역할)에 맞춰 채팅창에 보내 최종 컨펌을 받을 수 있도록 아래 5요소 구조로 작성한다.
     - `정리하면 — 1) 핵심 해결 문제: ... / 2) 구현할 기능: ... / 3) 이번 범위에서 제외할 항목(Cut List): ... / 4) 핵심 판단·성공 기준: ... / 5) 준수할 제약 및 운영 기준: ... 이렇게 정리하여 진행하고자 합니다. 혹시 반대하시거나 수정해야 할 부분이 있을까요?`
4. 담당자 답장과 사용자 확인 결과:
   - 담당자가 동의하고 사용자도 수정 사항이 없으면 `6`번 단계를 완료 처리하고 **`7-plan`로 넘어간다.**
   - 만약 담당자가 반대 의견·보완 조건을 주었거나 사용자가 수정할 항목을 발견하여 재호출한 경우, 변경되지 않은 기존 입력 파일들은 중복해서 다시 읽지 않고 새로 갱신된 `sk/work/INBOX.md`만 읽어 `sk/work/SPEC.md`와 `sk/work/DM_LOG.md`를 최종 개정하고 확정 요약을 `sk/work/OUTBOX.md`에 적은 뒤 `7`번 단계로 넘어간다.

## 응답 지침
7번 구현 계획 단계 도중에 스펙이 흔들려 중단하는 일이 없도록, 6번 단계에서 사용자 확인과 담당자 최종 서면 합의를 완전히 마무리하여 `sk/work/SPEC.md`를 확정한다.
