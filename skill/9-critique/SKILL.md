---
name: 9-critique
description: "지정된 슬라이스 번호 N(예: $critique 2)의 구현 파일을 3대 독립 검증 테스트, 클린 아키텍처 감사, ui_verify.py로 검증하고, 하드 결함 원인 분석(RCA) 및 설계·UX 개선 비평을 sk/work/critiques/SLICE_N.md에 작성한다 ($critique N)."
---
# 9-critique

## 역할
슬라이스 번호 `N`을 인자로 받아 해당 슬라이스가 만든 파일들을 독립 테스트(`tests/test_slice_N.py`), 클린 코드·클린 아키텍처 기준, 번들 검증 스크립트(`scripts/ui_verify.py`)로 검사하고, 동작 결함의 근본 원인 분석(RCA)과 설계 완성도·UX 개선 비평을 `sk/work/critiques/SLICE_N.md`에 기록한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `sk/work/critiques/SLICE_N.md`
  - `app/*`
  - `tests/test_slice_N.py`
  - `references/CRITIQUE_SLICE_TEMPLATE.md`
- 쓰기:
  - `sk/work/critiques/SLICE_N.md`
  - `tests/test_slice_N.py`
  - `sk/work/ui_screenshot.png`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 스크립트:
  - `python3 scripts/verify_slice.py [1|2|3|4|5|all]` (슬라이스별 사전 정의된 DB·클린 아키텍처·무스터브·결정론·보안·UI 자동 검증기)
  - `python3 scripts/ui_verify.py` (라이브 서버 및 헤드리스 UI 캡처 보조 스크립트)
- 레퍼런스: `references/CRITIQUE_SLICE_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`, `sk/work/PARADIGM.md`(핵심 가치·역할별 사용자 여정·`Cut List`), `sk/work/BUILD_PROGRESS.md`(세션 인계 내역)를 읽어 검증자가 집중 확인해야 할 엣지케이스나 사용자가 수동 검증에서 발견한 이상 증상이 있는지 확인한다.
2. 전달된 슬라이스 번호 `N`을 확인하고(번호가 생략된 경우 `BUILD_PROGRESS.md`에서 완료되었으나 비평 파일이 없거나 재검증이 필요한 슬라이스를 선택), **가장 먼저 번들 스크립트 `python3 scripts/verify_slice.py N`을 실행**한다.
   - `Slice 1`: `.env.example`, `config.py` 환경변수 주입, `db.py` SQLite 영속성·`?` 파라미터 바인딩·`is_stale` 플래그, `data_loader.py` 검증 함수 및 `data/datasets/` 준비 여부, 미구현 스터브(`pass`/`TODO`) 및 `bare except` 0건 자동 검사
   - `Slice 2`: `core_engine.py` 순수 도메인 분리(웹·DB 패키지 import 0건), 비결정적 난수 호출 금지, 제약 미충족 경고(`unassigned_warnings`) 구조, 무스터브 자동 검사
   - `Slice 3`: `simulator_api.py`·`main.py` Thin Router 준수, `require_admin_role` 권한 검증 및 `to_user_dto` 민감정보 화이트리스트 구조, `Dockerfile` 및 `/api/health` 자동 검사
   - `Slice 4~5`: 외부 CDN 미사용, `<input type="file">` 및 기본 `alert/confirm/prompt` 미사용, JS `var` 금지, Native SVG 그래프 렌더링 및 헤드리스 화면 캡처(`sk/work/ui_screenshot.png`) 자동 검사
3. 이어서 크리틱 에이전트가 직접 해당 슬라이스의 도메인 비즈니스 규칙을 검증하는 아래 **3대 독립 검증 기준**의 `tests/test_slice_N.py`를 작성하고 끝까지 실행하여 검증을 완수한다(사용자에게 터미널 테스트 실행을 떠넘기지 않는다).
   - 1) **소규모 기준 케이스 정답 대조 검증 (Micro-Case Ground-Truth Verification)**: 정답이 명확한 2~3건의 최소 입력 케이스를 독립적으로 구성하여 기대값과 실제 함수 반환값이 정확히 일치하는지 검증
   - 2) **하드 불변 조건 전수 검사 (Invariant Audit)**: `SPEC.md`의 모든 하드 제약(용량/시간/예산 초과 0건, 필수 대상 누락 및 비대상 오배정 0건 등)을 별도 검증식으로 전수 확인
   - 3) **오류 주입 및 변이 검증 (Fault Injection & Mutation Testing)**: 잘못된 데이터셋 입력 시 기존 데이터 롤백 유지 확인, 구성원 응답에서 타인/민감 필드 제거(`to_user_dto`) 확인, 핵심 제약 조건을 위반한 가짜 결과를 넣었을 때 검증기가 정확히 실패(`FAIL`)를 감지하는지(테스트 유효성 검증) 확인
4. `references/CRITIQUE_SLICE_TEMPLATE.md` 양식에 따라 판정 상태(`STATUS: PASS` 또는 `STATUS: NEEDS_REBUILD`), `verify_slice.py N` 및 `pytest tests/test_slice_N.py` 실행 결과, `[Part 1. 하드 결함 · 아키텍처 위반 · 동작 불량 원인 분석(RCA) (MUST-FIX)]`, `[Part 2. 설계 완성도 · UX 사용성 · 알고리즘 설득력 비평 (DESIGN & UX REVIEW)]`을 `sk/work/critiques/SLICE_N.md`에 작성하고, 독립 테스트 실행 결과 및 판정 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
읽기 전용 검증 역할이므로 `app/*` 소스 코드는 직접 수정하지 않고, 결함 발생 시 어느 파일·함수의 어떤 조건 때문에 문제가 발생하는지 근본 원인(RCA)을 정확히 짚어 기록한다.
