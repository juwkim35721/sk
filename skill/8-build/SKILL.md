---
name: 8-build
description: "확정된 PLAN.md의 첫 슬라이스부터 마지막 슬라이스까지 순서대로 연속 구현하고, 슬라이스 완료 시마다 스모크 테스트와 세션 인계(Handoff) 및 구현 로직 명세(수식·임계값·DB 테이블·상태 플래그)를 BUILD_PROGRESS.md와 OUTBOX.md에 기록한다 ($build)."
---
# 8-build

## 역할
`sk/work/PLAN.md`에 정의된 전체 슬라이스를 클린 아키텍처 원칙에 맞춰 순서대로 끝까지 구현하며, 각 슬라이스 완료 시 즉석 스모크 테스트 후 `references/HANDOFF_TEMPLATE.md` 양식에 맞춰 멀티세션 인계(Handoff) 상태와 슬라이스별 **구현 로직 명세(`입력 -> 실제 수식/임계값/조건문 -> DB 테이블/상태 플래그 -> 출력`)**를 `sk/work/BUILD_PROGRESS.md` 및 `sk/work/OUTBOX.md`에 기록한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `sk/work/SPEC.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `data/README.md` 및 부속 출력 스키마 문서
  - `references/HANDOFF_TEMPLATE.md`
- 쓰기:
  - `app/*`, `data/*`, `Dockerfile`, `.env.example`
  - `sk/work/BUILD_PROGRESS.md`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 레퍼런스: `references/HANDOFF_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 구현 착수 전 사용자가 지시한 특별 코딩 원칙이나 제약이 있는지 확인한다.
2. `sk/work/PLAN.md`의 `Slice 1`부터 마지막 슬라이스까지 **상향식(Bottom-Up) 무스터브(Zero-Stub) 구현 원칙**(의존성이 없는 하위 모듈·기초 헬퍼 함수부터 먼저 100% 실제 로직으로 완성하고, 상위 모듈은 이미 완성된 하위 모듈을 호출; `pass`·`TODO`·더미 반환 스터브 생성 금지), 클린 아키텍처 원칙(계층 간 단일 책임 분리, 설정값 환경변수 주입, DB 영속성 및 검증 실패 시 롤백 보장, 결과/오류 하드코딩 금지), **운영·보안 방어 표준**(서버 측 관리자 권한 재확인 `require_admin_role`, 구성원 조회 응답 화이트리스트 `to_user_dto`로 타인/민감 필드 제거, 제약 미충족 대상 `unassigned_warnings` 명시적 경고, 화면 5대 상태 `로딩/결과없음/오류/재계산필요(Stale)/권한없음` 표시, 외부 CDN 금지), 그리고 **언어·프레임워크별 Google Style 코딩 컨벤션**(Python `PEP 8`/타입 힌트/`@dataclass`/`UPPER_SNAKE_CASE` 상수 분리/`with` 컨텍스트 매니저/비특정 `bare except` 금지, API Thin Router, JS `ES6+` `const`/`let` 및 상태·계산·렌더링 분리, SQL `?` 파라미터 바인딩)을 준수하여 연속 구현한다.
3. 각 `Slice K`의 구현이 끝날 때마다 즉석 스모크 테스트로 문법 및 런타임 오류가 없음을 확인한다.
4. 직후 `references/HANDOFF_TEMPLATE.md` 양식에 따라 `sk/work/BUILD_PROGRESS.md`에 `Slice K: DONE`, 담당 파일·핵심 함수 매핑, 그리고 **구현 로직 상세 명세(사용한 최적화 라이브러리/솔버 함수와 전달 인자·목적함수의 의미, 실제 거리·점수·보간 수식, 임계값 상수, DB 테이블·컬럼명, 롤백 및 이전 결과 노출 차단 상태 플래그명, 권한·화이트리스트 DTO 함수명)** 및 세션 인계(Handoff) 메모를 구체적으로 기록한다.
5. 각 슬라이스 완료 상태를 `sk/work/OUTBOX.md`에 갱신한 뒤 멈추지 않고 다음 슬라이스를 이어서 구현한다.
6. 모든 슬라이스 구현이 완료되면 `sk/work/OUTBOX.md`에 1) 전체 구현 작동 원리 및 핵심 수식/변수 요약, 2) 사용자가 브라우저에서 직접 확인할 수동 검증 체크리스트, 3) 추가로 고도화·보완하면 좋은 제안 항목을 적는다.

## 응답 지침
슬라이스 사이에 멈추지 않고 마지막 슬라이스까지 연속 구현하되, 사용자가 대기 시간 동안 `BUILD_PROGRESS.md`만 읽어도 코드 속 세부 수식과 상태 제어 변수를 명확히 숙지할 수 있도록 구현 로직 명세를 남긴다.
