# 실무형 AI 과제 14대 표준 스킬 키트 (`sk/README.md` — 에이전트 및 시스템 요약 명세)

> **문서 역할 분리 안내**:
> - 본 파일(`sk/README.md`)과 `sk/harness/AGENTS.md`는 **에이전트(Codex)가 참조하는 핵심 엔지니어링 규칙과 14대 스킬 입출력 명세**만 간결하게 유지한다.
> - **사용자가 실전 작업 중 참고하는 상세 매뉴얼**(기호 사전, 산출물 파일 트리·기능 지도, 현업 담당자 DM 질의응답 전략, 핵심 설계·트레이드오프 복기법, 비상시 대처법)은 **[USER_GUIDE.md](USER_GUIDE.md)**에 분리되어 있다.

## 1. 빠른 시작 및 설치 명령
```bash
python3 sk/install.py      # 루트 AGENTS.md 병합 및 .agents/skills/에 14개 스킬 설치
```

## 2. 핵심 엔지니어링 운영 원칙 요약
1. **최우선 입력(`sk/work/INBOX.md`) 및 출력 브릿지(`sk/work/OUTBOX.md`)**: 모든 스킬은 시작 시 `INBOX.md`를 가장 먼저 읽고, 확인 질문·담당자 DM 초안·구현 명세 요약·수동 검증 체크리스트는 `OUTBOX.md`에 출력한다.
2. **클린 아키텍처 4계층 및 조건부 동시성 제어**: 설정·환경변수(`config.py`, `.env.example`), DB 영속성(`db.py`, 동시 수정 잠금은 현업 담당자 확인 결과 필요한 경우에만 구현), 데이터셋 실제 검증·원자적 롤백(`data_loader.py`), 순수 도메인 최적화 엔진(`core_engine.py`), 서버 권한 분리(`require_admin_role`)·화이트리스트 DTO(`to_user_dto`)·외부 CDN 금지 UI(`simulator_api.py`, `main.py`, `static/*`, `Dockerfile`)를 준수한다.
3. **세션 인계(`BUILD_PROGRESS.md`) 및 6대 엔지니어링 트레이드오프 문서화(`QA_CARD.md`)**: 슬라이스 구현마다 사용한 최적화 라이브러리·수식·임계값·DB/상태 변수를 기록하고, 최종 제출 문서(`12`번 실행·개발 명세서 및 `13`번 기술 협업·검증 문서)에 6대 핵심 설계 의사결정 및 기술적 한계를 명시한 뒤 `app/*` 실제 코드를 역추적하여 3단 구조(250~400자) 기술 설명 카드를 생성한다.
4. **한·영 하이브리드 언어 및 Google Style 코딩 컨벤션**: 사용자 입력과 사용자가 읽을 모든 산출물은 **한국어**로 작성하며(내부 코드 식별자·로그·상태 태그는 영문 가능), 언어·프레임워크별 Google Style 코딩 컨벤션을 준수한다.

## 3. 전 과정 14대 표준 스킬 입출력 명세표
| 순번 | 스킬 폴더명 | 실행 세션 | 읽는 파일 (Read) | 쓰는 파일 (Write) |
| :---: | :--- | :---: | :--- | :--- |
| **1** | `1-eda` | 세션 1 | `INBOX.md`, `README.md`, `data/README.md`, `data/*` (`scripts/run_all.py`) | `EDA_REPORT.md`, `eda_overview.png`, `eda_ml_clusters.png`, `OUTBOX.md` |
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
