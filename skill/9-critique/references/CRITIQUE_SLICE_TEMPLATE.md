# 슬라이스 독립 검증 · 클린 아키텍처 감사 · 원인 분석(RCA) 비평서 (`sk/work/critiques/SLICE_N.md`)
> **생성 스킬**: `9-critique`
> **대상 슬라이스**: `Slice N` | **검사 대상 파일**: `app/...` (UI 슬라이스일 경우 웹서버 `0.0.0.0` + `sk/work/ui_screenshot.png` 포함)
> **현재 판정 상태**: `STATUS: NEEDS_REBUILD` 또는 `STATUS: PASS`

## 1. 사전 정의 슬라이스 검증(`scripts/verify_slice.py N`) 및 독립 테스트(`tests/test_slice_N.py`) 결과
- **사전 정의 슬라이스 자동 검증 명령 및 결과**: `python3 scripts/verify_slice.py N` -> `PASS / NEEDS_ATTENTION`
- **도메인 독립 검증 테스트 실행 명령 및 결과**: `pytest tests/test_slice_N.py` -> `X passed, Y failed`
- **3대 독립 검증(Independent Verification) 에이전트 수행 내역**:
  - [x] **1) 소규모 기준 케이스 정답 대조 검증 (Micro-Case Ground-Truth Verification)**: (크리틱 에이전트가 정답을 확정할 수 있는 2~3건의 최소 입력 케이스를 직접 구성하여 함수 반환값과 기대값 일치 확인)
  - [x] **2) 하드 제약 불변 조건 전수 검사 (Invariant Audit)**: (`SPEC.md` 기준 용량/시간/예산 위반 0건, 필수 대상 누락 및 비대상 오배정 0건 전수 확인)
  - [x] **3) 오류 주입 및 변이 검증 (Fault Injection & Mutation Testing)**: (오류 데이터셋 롤백 확인, 핵심 제약 위반 가짜 결과 주입 시 검증 함수가 정확히 실패를 감지하는지 테스트 유효성 확인)
- **에이전트 검증 실행 핵심 수치 및 로그 요약**:
  - `...`

## 2. 클린 코드 · 클린 아키텍처 · 코딩 컨벤션 · 보안/배포 규격 감사 (CLEAN CODE & ARCHITECTURE AUDIT)
- [x] **계층 분리 (`SRP`, 단일 책임 원칙)**: 도메인 알고리즘(`core_engine.py`)이 웹/DB/UI에 직접 결합되지 않고 분리되어 있는가? (API 라우터가 Thin Router를 유지하는가?)
- [x] **Google Style 코딩 컨벤션 준수**: Python(`snake_case`/`PascalCase`/`UPPER_SNAKE_CASE` 상수 분리, 타입 힌트, Docstring, 비특정 `bare except` 금지, `with` 사용), JS(`const`/`let`, `camelCase`, 상태·계산·렌더링 분리), SQL(`?` 파라미터 바인딩) 규칙을 준수했는가?
- [x] **권한 분리 및 개인정보 보호 (`require_admin_role` & `to_user_dto`)**: 운영자 API 권한을 서버에서 확인하며, 구성원 조회 응답에서 타인 정보·민감 필드를 서버 DTO 화이트리스트로 제거했는가?
- [x] **하드코딩 및 미구현 스터브(Stub) 금지**: 설정·비밀값이 환경변수(`.env.example`, `config.py`)로 주입되며, 매직 넘버나 계산 결과·오류 메시지 하드코딩 및 미완성 스터브(`pass`, `TODO`, 더미 반환)가 없는가? (상위 모듈이 완성된 하위 모듈을 정상 호출하는가?)
- [x] **영속성 · 롤백 · 실행 불가 경고**: DB 저장 후 재시작 시 결과가 유지되며, 오류 데이터셋 검증 실패 시 기존 결과가 보존되고, 제약 미충족 대상 발생 시 조용히 빼지 않고 경고(`unassigned_warnings`)하는가?
- [x] **전체화면 이탈 및 외부 CDN 방지**: `<input type="file">`, 파일 열기/저장 창, 브라우저 기본 `alert/confirm/prompt`, 외부 폰트/스크립트 CDN이 없는가?

## 3. [Part 1. 하드 결함 · 아키텍처 위반 · 동작 불량 원인 분석(RCA) (MUST-FIX — 전량 수정 필수)]
| 결함 ID | 파일 및 라인 (`file:line`) | 발생 증상 및 근본 원인 분석 (Root Cause Analysis) | 구체적 수정 지침 | 상태 |
| :---: | :--- | :--- | :--- | :---: |
| `BUG-N1` | `app/core_engine.py:142` | (증상: 특정 조건에서 상한 초과 / 원인: 분할 루프 종료 조건에서 이동시간 비대칭 미반영) | (분할 조건식 및 검증 로직 수정) | `[OPEN -> FIXED]` |

## 4. [Part 2. 설계 완성도 · UX 사용성 · 알고리즘 설득력 비평 (DESIGN & UX REVIEW — 비판적 선별 수용 대상)]
| 비평 ID | 영역 (알고리즘 설득력 / UI 사용성 / 지표 가시성) | 현재 구현의 아쉬운 점 및 고도화 제안 | 비판적 판단 (`ACCEPTED` / `REJECTED: 사유`) |
| :---: | :--- | :--- | :--- |
| `FEEL-N1` | 알고리즘/데이터 설득력 | (예: 제약은 통과했으나 특정 그룹에 배정이 편중되어 보임 -> 가중치 보정 제안) | `[PENDING]` |
| `FEEL-N2` | UX 사용성 및 가시성 | (예: 조건 재계산 시 기존 대비 증감 수치 배지가 없어 변화 체감이 약함) | `[PENDING]` |
