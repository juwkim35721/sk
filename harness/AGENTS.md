<!-- SK-KIT:BEGIN (python3 sk/install.py가 관리하는 구역입니다.) -->
## 실무형 AI 엔지니어링 표준 하네스 지침 (14대 역할 스킬 워크플로우)

이 구역은 `python3 sk/install.py`가 과제 루트 `AGENTS.md`에 삽입한 핵심 작업 규칙이다. 과제 루트의 `README.md` 지시문이 항상 최우선이다.

### 1. 핵심 엔지니어링 운영 원칙
1. **지정 파일 핀포인트 읽기 및 재호출 중복 읽기 금지**: 전체 디렉터리를 무작위로 스캔하지 않고, 호출된 스킬의 `입출력 파일` 섹션에 명시된 읽기 대상 파일만 읽는다. 동일 세션 내 반복 호출(루프) 시에는 변경되지 않은 기존 입력 파일을 중복해서 다시 읽지 않고 새로 갱신된 `sk/work/INBOX.md`만 읽어 즉시 반영한다.
2. **최우선 입력 창구 (`sk/work/INBOX.md`)**: 모든 스킬(1번~14번)은 실행 시작 시 반드시 `sk/work/INBOX.md`를 가장 먼저 읽고, 사용자의 특별 요청사항, 의사결정, 현업 담당자 정보 및 DM 답장, 화면 수동 검증 피드백, 추가 고도화 아이디어를 최우선으로 반영한다.
3. **출력 브릿지 (`sk/work/OUTBOX.md`)**: 사용자 확인 질문, 현업 담당자 전송용 제안형 DM 초안, 슬라이스 작동 원리 요약 및 수동 검증 체크리스트는 `sk/work/OUTBOX.md`에 기록한다.
4. **스킬 내부 리소스 상대경로 참조**: 각 스킬의 실행 스크립트(`scripts/*`)와 템플릿·레퍼런스(`references/*`)는 해당 스킬 폴더 기준 상대경로로 참조한다.
5. **클린 아키텍처 4계층 · 상향식(Bottom-Up) 무스터브 구현 · 보안 · 운영 리스크 방어**:
   - **상향식(Bottom-Up) 무스터브(Zero-Stub) 구현**: 의존성이 없는 최하위 계층·기초 함수부터 먼저 100% 완성하고 상위 모듈이 이미 완성된 하위 모듈을 호출한다(`Slice 1: config -> db -> data_loader` -> `Slice 2: core_engine` -> `Slice 3: simulator_api -> main` -> `Slice 4~5: UI`). 스터브(`pass`, `TODO`, 더미 반환값)를 먼저 만들고 나중에 채우는 Top-Down 스터브 방식을 금지한다.
   - 설정·비밀값 환경변수 주입(`.env.example`, `app/config.py`, 하드코딩 금지) 및 외부 CDN(`@import` 등) 금지
   - DB 영속성(`app/db.py`, 빈 DB 자동 시딩 및 재시작 후 데이터·결과 유지; 동시 수정 잠금은 현업 담당자 확인 결과 필요한 경우에만 구현)
   - 데이터셋 실제 검증 및 원자적 롤백(`app/data_loader.py`, 업로드 창 없이 준비된 정상/오류 데이터셋 검증, 실패 시 기존 데이터·결과 유지, 적용 후 재계산 전 이전 결과 노출 차단 `is_stale`)
   - 순수 도메인 최적화 엔진(`app/core_engine.py`, 고성능 최적화 라이브러리 또는 3-Step 알고리즘 + 제약 미충족 대상 `unassigned_warnings` 명시적 경고)과 API·역할별 화면(`app/simulator_api.py`, `app/main.py`, `app/static/*`, `Dockerfile`, `/api/health`)의 단일 책임 분리(`SRP`)
   - 서버 측 관리자 권한 재확인(`require_admin_role`), 구성원 조회 응답 화이트리스트(`to_user_dto`로 타인·민감 필드 서버에서 제거), 화면 5대 상태(`로딩 / 결과없음 / 오류 / 재계산필요(Stale) / 권한없음`) 표시
6. **멀티세션 인계(Handoff) · 구현 로직 명세 (`sk/work/BUILD_PROGRESS.md`) 및 6대 엔지니어링 트레이드오프 정리**:
   - 구현(`8`), 재설계(`10`), 기능 고도화(`11`) 시마다 세션 인계(Handoff) 정보와 사용한 최적화 라이브러리/솔버·인자 의미, 수식·임계값, DB 테이블·상태 플래그명을 `sk/work/BUILD_PROGRESS.md`에 기록한다.
   - 검증(`9`) 시 크리틱 에이전트가 직접 3대 독립 검증(소규모 기준 케이스 정답 대조 검증, 하드 불변 조건 전수 검사, 오류 주입 및 변이 검증)을 끝까지 실행하여 확인하고, 최종 제출 문서(`12`번 실행·개발 명세서의 한계점 섹션, `13`번 기술 협업·검증 문서)에 6대 핵심 설계 의사결정 및 트레이드오프 한계를 명시한 뒤 `14`번 `QA_CARD.md`에 3단 구조(`구현 근거·한계 -> 파급 영향 -> 개선 계획`, 250~400자) 기술 복기 카드를 생성한다.
7. **설계 이력 보존 (`PLAN.md` Addendum) 및 원본 `README.md` 절대 보호**:
   - 추가 요구사항 반영 시 `PLAN.md` 초기 설계는 덮어쓰지 않고 하단 `Addendum` 섹션에 누적 기록한다.
   - 과제 루트 `README.md`는 절대 수정하지 않으며, 제출용 실행·개발 명세서와 기술 협업·검증 문서는 `README.md`가 지정한 별도 파일명으로 작성한다.
8. **한·영 하이브리드 언어 규칙**: 스킬 문서가 영문이더라도 사용자는 `INBOX.md`와 추가 요청을 한국어로 작성하며, 사용자가 읽고 확인·전송·숙지·제출할 모든 출력물(채팅 응답, `OUTBOX.md`, `BUILD_PROGRESS.md` 브리핑, `MANAGERS/MATRIX/PARADIGM/SPEC/PLAN/SLICE_N.md`, `QA_CARD.md`, 제출용 실행·개발 명세서 및 협업·검증 문서)은 **무조건 한국어로 작성한다.** (내부 코드 식별자·로그·상태 태그는 영문 가능)
9. **Google Style 코딩 컨벤션**:
   - Python(`PEP 8`, `snake_case`/`PascalCase`/`UPPER_SNAKE_CASE` 상수 분리, 매직 넘버 금지, 타입 힌트, Docstring, `@dataclass`/`Pydantic`, 비특정 `bare except` 금지, `with` 컨텍스트 매니저 사용)
   - API(`Thin Router`, 하위 계층 호출만 수행, 일관된 `200`/`400`/`422` JSON 응답)
   - JS/CSS(`const`/`let`, `camelCase`, `async/await`, 단일 `appState`·계산 함수·DOM/SVG 렌더링 분리, CSS `:root` 변수)
   - SQL(예약어 대문자, `snake_case` 식별자, 100% `?` 파라미터 바인딩)

### 2. 2-세션 분리 협업 및 약어 기호 규칙
- **세션 1 (Builder / Writer)**: 분석(`1`~`2`), 요건·패러다임·스펙 확정(`3`~`6`), 계획(`7`), 연속 구현(`8`), 원인 분석(RCA) 및 재설계(`10`), 점진적 고도화(`11`), 최종 문서 및 기술 복기 카드(`12`~`14`) 전담.
- **세션 2 (Verifier — Read-Only)**: `app/*` 수정 금지. `9`번 스킬로 사전 정의 슬라이스 검증(`scripts/verify_slice.py N`), 도메인 독립 테스트(`tests/test_slice_N.py`), `scripts/ui_verify.py`, 원인 분석(RCA) 수행 -> `sk/work/critiques/SLICE_N.md` 기록.
- **약어 기호**: `ER-#`(명시적 요구), `IR-#`(추론 요구), `EC-#`(명시적 하드 제약), `IC-#`(데이터 방어 제약), `OUT-#`(금지·제외 범위), `STATE-#`(롤백·DB 영속성·배포 규격), `LINKED-#`(부속 스키마), `UG-#`(현업 운영 기준 확인 안건 -> 확정 시 `EC-#`/`ER-#` 승격), `BUG-N#`(전량 수정 필수 하드 결함), `FEEL-N#`(설계 완성도·UX 개선 제안, `ACCEPTED`/`REJECTED` 선별 수용), `STATUS: PASS` / `NEEDS_REBUILD`, `[PENDING]` / `[CONFIRMED]`.

### 3. 전 과정 14대 표준 스킬 입출력 요약표
| 순번 | 스킬 폴더명 | 세션 | 읽는 파일 (Read) | 쓰는 파일 (Write) |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `1-eda` | 세션 1 | `INBOX.md`, `README.md`, `data/README.md`, `data/*` (`scripts/run_all.py` 실행) | `EDA_REPORT.md`, `eda_overview.png`, `eda_ml_clusters.png`, `OUTBOX.md` |
| **2** | `2-domain` | 세션 1 | `INBOX.md`, `README.md`, `data/README.md`, `data/*`, `EDA_REPORT.md`, `eda_*.png` | `EDA_SUPPLEMENT.md`, `OUTBOX.md` |
| **3** | `3-manager` | 세션 1 | `INBOX.md`, `README.md`, `EDA_*.md`, `references/MANAGERS_TEMPLATE.md` | `MANAGERS.md`, `OUTBOX.md` |
| **4** | `4-matrix` | 세션 1 | `INBOX.md`, `README.md` 및 부속 문서, `EDA_*.md`, `MANAGERS.md`, `MATRIX.md`, `DM_LOG.md`, `references/MATRIX_TEMPLATE.md` | `MATRIX.md`, `OUTBOX.md`, `DM_LOG.md` |
| **5** | `5-paradigm` | 세션 1 | `INBOX.md`, `README.md`, `MATRIX.md`, `MANAGERS.md`, `EDA_*.md`, `DM_LOG.md`, `PARADIGM.md`, `references/PARADIGM_TEMPLATE.md` | `PARADIGM.md`, `OUTBOX.md`, `DM_LOG.md` |
| **6** | `6-spec` | 세션 1 | `INBOX.md`, `MANAGERS.md`, `MATRIX.md`, `PARADIGM.md`, `DM_LOG.md`, `SPEC.md`, `references/SPEC_TEMPLATE.md` | `SPEC.md`, `OUTBOX.md`, `DM_LOG.md` |
| **7** | `7-plan` | 세션 1 | `INBOX.md`, `PARADIGM.md`, `SPEC.md`, `PLAN.md`, `references/ARCH_BLUEPRINTS.md`, `references/PLAN_TEMPLATE.md` | `PLAN.md`, `OUTBOX.md` |
| **8** | `8-build` | 세션 1 | `INBOX.md`, `SPEC.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `data/README.md` 및 부속 스키마, `references/HANDOFF_TEMPLATE.md` | `app/*`, `data/*`, `Dockerfile`, `.env.example`, `BUILD_PROGRESS.md`, `OUTBOX.md` |
| **9** | `9-critique` | 세션 2 | `INBOX.md`, `PARADIGM.md`, `SPEC.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `critiques/SLICE_N.md`, `app/*`, `tests/test_slice_N.py`, `references/CRITIQUE_SLICE_TEMPLATE.md` (`scripts/verify_slice.py`, `scripts/ui_verify.py`) | `critiques/SLICE_N.md`, `tests/test_slice_N.py`, `ui_screenshot.png`, `OUTBOX.md` |
| **10** | `10-rebuild` | 세션 1 | `INBOX.md`, `critiques/SLICE_*.md`, `tests/test_slice_*.py`, `PARADIGM.md`, `SPEC.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `app/*` | `app/*`, `critiques/SLICE_*.md`, `BUILD_PROGRESS.md`, `OUTBOX.md` |
| **11** | `11-add` | 세션 1 | `INBOX.md`, `PARADIGM.md`, `SPEC.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `app/*` | `SPEC.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `app/*`, `OUTBOX.md` |
| **12** | `12-guide` | 세션 1 | `INBOX.md`, `README.md`, `EDA_REPORT.md`, `PARADIGM.md`, `SPEC.md`, `DM_LOG.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `SLICE_*.md` | `<실행가이드_문서>.md`, `OUTBOX.md` |
| **13** | `13-doc` | 세션 1 | `INBOX.md`, `<협업검증_문서>.md`, `README.md`, `EDA_*.md`, `MATRIX.md`, `PARADIGM.md`, `SPEC.md`, `DM_LOG.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `SLICE_*.md` | `<협업검증_문서>.md`, `OUTBOX.md` |
| **14** | `14-qa` | 세션 1 | `INBOX.md`, `app/*.py`, `app/static/*.js`, `<실행가이드_문서>.md`, `<협업검증_문서>.md`, `MATRIX.md`, `PARADIGM.md`, `SPEC.md`, `DM_LOG.md`, `PLAN.md`, `BUILD_PROGRESS.md`, `SLICE_*.md`, `references/QA_CARD_TEMPLATE.md` | `QA_CARD.md`, `OUTBOX.md` |
<!-- SK-KIT:END -->
