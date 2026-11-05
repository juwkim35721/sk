---
name: 10-rebuild
description: "INBOX.md에 기록된 사용자의 수동 검증 피드백과 sk/work/critiques/SLICE_*.md의 비평을 읽고, 동작 불량 원인 분석(RCA) 및 하드 결함 전량 수정과 설계 완성도·UX 개선 제안의 비판적 선별 수용을 수행한다 ($rebuild)."
---
# 10-rebuild

## 역할
사용자가 화면 수동 검증을 통해 발견한 문제점(`INBOX.md`)과 `sk/work/critiques/SLICE_*.md`의 비평을 검토하여, 근본 원인 분석(RCA)을 통해 하드 결함 및 아키텍처 위반을 전량 수정하고 설계 완성도·UX 개선 제안을 비판적으로 선별 반영한 뒤 세션 인계 기록(`BUILD_PROGRESS.md`)을 갱신한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/critiques/SLICE_*.md`
  - `tests/test_slice_*.py`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - 수정 대상 슬라이스의 `app/*` 파일
- 쓰기:
  - `app/*`
  - `sk/work/critiques/SLICE_*.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `sk/work/OUTBOX.md`

## 작업 절차
1. `sk/work/INBOX.md`를 가장 먼저 읽어 사용자가 수동 검증하며 발견한 동작 결함, 오류 증상, 또는 재설계 지침이 있는지 확인한다.
2. 사용자가 제보한 증상과 `sk/work/critiques/SLICE_*.md` 중 `STATUS: NEEDS_REBUILD`인 항목에 대해 근본 원인 분석(RCA)을 수행한다.
3. `[Part 1. 하드 결함 · 아키텍처 위반 · 동작 불량 원인 분석(RCA) (MUST-FIX)]` 항목과 사용자 제보 결함을 모두 수정하고, 수정된 슬라이스에 대해 사전 정의 검증기(`verify_slice.py`) 및 `pytest tests/test_slice_N.py` 통과를 확인한다.
4. `[Part 2. 설계 완성도 · UX 사용성 비평 (DESIGN & UX REVIEW)]`은 `sk/work/PARADIGM.md`(핵심 가치·역할별 사용자 여정·`Cut List`) 및 `SPEC.md`에 비추어 비판적으로 검토하여, 핵심 가치를 높이고 안전한 제안은 수용(`ACCEPTED`)해 반영하고, 패러다임에 어긋나거나 `Cut List`(과잉 구현)에 해당하는 제안은 기존 설계를 유지하며 기각 사유(`REJECTED`)를 기록한다.
5. 수정한 원인·해결 원리와 변경된 함수 매핑을 `sk/work/BUILD_PROGRESS.md`에 누적 기록하고, 수정 결과 요약과 재검증 대상 슬라이스 번호를 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
이미 `STATUS: PASS`이고 사용자 수정 요청과 무관한 슬라이스의 코드는 불필요하게 건드리지 않으며, 무엇이 왜 안 되었고 어떻게 고쳤는지 사용자가 명확히 이해할 수 있게 설명한다.
