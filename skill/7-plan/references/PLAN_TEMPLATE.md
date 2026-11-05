# 클린 아키텍처 · 알고리즘 선정 근거 및 파일 경계 기반 슬라이스 구현 계획 (`sk/work/PLAN.md`)
> **생성 및 조율 스킬**: `7-plan`
> **역사 보존 원칙 (Immutable History)**: 초기 설계된 `Slice 1 ~ Slice N` 계획은 덮어써서 지우지 않는다. 구현 도중 추가 아이디어(`11-add`)가 들어오면 하단 `## 5. 추가 내용 반영 설계 (Addendum)` 섹션에 누적 기록한다.

## 1. 클린 아키텍처 계층 설계 및 기술 스택 선정 근거 (대안 대비 비교표)
| 비교 항목 | 대안 아키텍처 1 | 대안 아키텍처 2 | 채택 클린 아키텍처 (선정 이유) |
| :--- | :--- | :--- | :--- |
| **계층 분리 (SRP)** | ... | ... | Config/DB 영속성 계층, 데이터 검증 계층, 순수 도메인 알고리즘 계층, API/프론트엔드 계층 분리 |
| **DB 영속성 및 롤백** | ... | ... | 빈 DB 자동 초기화·시딩, 재시작 시 결과 유지, 검증 실패 데이터셋 원자적 롤백 |
| **배포 및 환경변수** | ... | ... | `.env.example` 기반 설정 주입(하드코딩 금지), `/api/health` 헬스체크, `Dockerfile` 컨테이너 실행 |

## 2. 핵심 알고리즘 단계별 작동 원리 및 대안 알고리즘 비교표
- **채택 알고리즘 및 선정 기준(최적화 목적함수)**: ...
- **단계별 작동 원리 (Input -> Step 1 -> Step 2 -> Step 3 -> Output)**:
  1. **Step 1**: ...
  2. **Step 2**: ...
  3. **Step 3**: ...
- **대안 알고리즘(완전탐색/MILP, 확률적 메타휴리스틱 등) 대비 장단점 비교**: ...

## 3. 클린 아키텍처 폴더 구조 및 모듈 간 인터페이스 계약
```text
.env.example                # [Slice 1 전담 파일]
Dockerfile                  # [Slice 3 전담 파일]
data/
└── datasets/               # [Slice 1 전담 생성: 정상 변경 데이터셋 및 오류 주입 데이터셋]
app/
├── config.py               # [Slice 1 전담 파일: 환경변수 설정 주입]
├── db.py                   # [Slice 1 전담 파일: DB 스키마·시딩·영속성·롤백]
├── data_loader.py          # [Slice 1 전담 파일: 데이터셋 실제 검증·파싱]
├── core_engine.py          # [Slice 2 전담 파일: 순수 도메인 최적화·재계산 엔진]
├── simulator_api.py        # [Slice 3 전담 파일: 상태 전이·역할·내보내기 API 라우터]
├── main.py                 # [Slice 3 전담 파일: 0.0.0.0 엔트리 및 /api/health]
└── static/
    ├── admin_view.js       # [Slice 4 전담 파일: 운영자 데이터셋·재계산·전체 그래프·내보내기 UI]
    ├── styles.css          # [Slice 4 전담 파일: 스타일시트]
    ├── user_view.js        # [Slice 5 전담 파일: 구성원/현장 날짜별 조회·노드 그래프·실시간 위치 UI]
    └── index.html          # [Slice 5 전담 파일: 통합 엔트리 HTML]
```

## 4. 상향식(Bottom-Up) 무스터브 및 파일 경계 기반 슬라이스 분할 계획 (Bottom-Up & Strict File-Boundary Slicing)
> **원칙**:
> 1. **상향식(Bottom-Up) 무스터브 구현**: 상위 모듈을 먼저 만들고 하위 함수를 스터브(`pass`, `TODO`, 가짜 반환값)로 비워두는 Top-Down 방식을 금지한다. 반드시 의존성이 없는 최하위 모듈·함수부터 100% 실제 로직으로 완성하고, 상위 모듈은 이미 완성·검증된 하위 모듈을 호출하여 조립한다.
> 2. **파일 경계 분리**: 서로 다른 슬라이스가 동일 파일을 중복 수정하지 않도록 1개 슬라이스당 독립된 생성 파일 세트를 배정한다. 각 슬라이스 완료 즉시 세션 2(`9-critique`)에서 스터브 없이 실제 동작을 독립 검증할 수 있다.

- **Slice 1 (최하위 기반 계층): 환경변수 설정 · DB 영속성 · 데이터셋 검증/롤백 로더 및 테스트 데이터셋 준비**
  - **구현 순서 (Bottom-Up)**: `.env.example` -> `app/config.py`(`load_config()`) -> `app/db.py`(`init_db()`, `save_state()`, `rollback_state()`) -> `app/data_loader.py`(`validate_dataset()`, `apply_dataset()`) -> `data/datasets/*`
  - **핵심 구현 스펙**: 상위 모듈 의존성 없이 설정 로드, DB 시딩/트랜잭션 롤백, 데이터셋 실제 검증 함수를 스터브 없이 100% 완성
  - **스모크 테스트 명령**: `python3 -c "from app.data_loader import validate_dataset, apply_dataset; print('Slice 1 OK')"`
- **Slice 2 (순수 도메인 계층): 도메인 데이터 모델 및 다단계 최적화·재계산 코어 엔진**
  - **구현 순서 (Bottom-Up)**: 거리/점수/제약 검산 하위 헬퍼 함수 -> `Step 1` 함수 -> `Step 2` 함수 -> `Step 3` 함수 -> 최상위 `run_optimization()` (`app/core_engine.py`)
  - **핵심 구현 스펙**: 웹/DB 결합 없이 순수 도메인 입력에 대해 최적화 및 재계산 결과(`unassigned_warnings` 포함)를 스터브 없이 100% 산출
  - **스모크 테스트 명령**: `python3 -c "from app.core_engine import run_optimization; print('Slice 2 OK')"`
- **Slice 3 (상위 API 조립 계층): 애플리케이션 서비스 · REST API 서버 (`0.0.0.0`) · JSON 내보내기 및 `Dockerfile`**
  - **구현 순서 (Bottom-Up)**: 권한/DTO 변환 헬퍼(`require_admin_role()`, `to_user_dto()`) -> 완성된 `Slice 1·2` 모듈을 호출하는 `app/simulator_api.py` -> `app/main.py` -> `Dockerfile`
  - **핵심 구현 스펙**: 이미 완성된 `db.py`, `data_loader.py`, `core_engine.py`의 실제 함수를 호출하여 REST API 및 JSON 내보내기 완성
  - **스모크 테스트 명령**: `python3 -c "import app.main; print('Slice 3 OK')"`
- **Slice 4 (상위 프론트엔드 계층 1): 운영자(Admin) 구역 프론트엔드 모듈 및 스타일시트**
  - **구현 순서 (Bottom-Up)**: `app/static/styles.css` -> 좌표 정규화/보간 계산 함수 -> 완성된 `Slice 3` API를 호출하는 `app/static/admin_view.js`
  - **핵심 구현 스펙**: ...
- **Slice 5 (최상위 통합 UI 계층 2): 구성원/현장(User) 구역 프론트엔드 모듈 및 통합 엔트리 HTML**
  - **구현 순서 (Bottom-Up)**: 완성된 `Slice 3` API를 호출하는 `app/static/user_view.js` -> `admin_view.js`와 `user_view.js`를 통합 연결하는 `app/static/index.html`
  - **핵심 구현 스펙**: ...

## 5. 추가 내용 반영 설계 (Addendum — 구현 중 아이디어 추가 시 하단에 누적 기록)
- (초기 계획 이후 추가된 설계 이력이 이곳에 기록됨)
