---
name: 13-doc
description: "작업공간 루트에 제공되었거나 README.md에서 지정한 기술 협업·검증 문서(<협업검증_문서>.md)의 질문 양식에 맞춰 프로젝트의 실제 엣지케이스 원인 분석(RCA) 및 해결, 클린 아키텍처·3대 독립 검증 원칙, 점진적 고도화 협업 사례를 작성한다."
---
# 13-doc

## 역할
작업공간 루트에 제공되었거나 `README.md`에서 지정한 기술 협업·검증 문서(`<협업검증_문서>.md`)의 질문 문항을 그대로 유지한 채, 실제 수행한 데이터 분석, 현업 담당자 DM 합의, 클린 아키텍처 기반 슬라이스 구현, 독립 검증 및 원인 분석(RCA) 고도화 기록을 근거로 답변을 작성한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `<협업검증_문서>.md` (루트에 제공된 협업·검증 질문지 문서)
  - `README.md`
  - `sk/work/EDA_REPORT.md`
  - `sk/work/EDA_SUPPLEMENT.md`
  - `sk/work/MATRIX.md`
  - `sk/work/PARADIGM.md`
  - `sk/work/SPEC.md`
  - `sk/work/DM_LOG.md`
  - `sk/work/PLAN.md`
  - `sk/work/BUILD_PROGRESS.md`
  - `sk/work/critiques/SLICE_*.md`
  - `references/TECH_VERIFICATION_TEMPLATE.md`
- 쓰기:
  - `<협업검증_문서>.md` (루트에 지정된 제출용 협업·검증 문서)
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 레퍼런스: `references/TECH_VERIFICATION_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`를 읽어 답변에 꼭 포함하고 싶은 사용자의 문제 해결 경험이나 특별 메모가 있는지 확인한다.
2. 작업공간 루트에 제공된 협업·검증 문서 또는 `README.md`에 안내된 제출 문서의 파일명과 질문 문항을 확인하고 `references/TECH_VERIFICATION_TEMPLATE.md`를 함께 참조한다.
3. 까다로운 엣지케이스/장애 해결 문항에는 `EDA_REPORT.md`, `MATRIX.md`, `BUILD_PROGRESS.md`, `SLICE_*.md`에서 실제로 발견·해결한 데이터 정합성(비대칭 구간, 시계열 특이일 등), 오류 데이터셋 검증 실패 시 원자적 롤백 및 재계산 전 이전 결과 노출 차단(`is_stale`), 제약 충족 불가 대상(`unassigned_warnings`) 명시적 경고 처리 및 알고리즘 경계값 장애의 근본 원인 분석(RCA)과 해결 방식을 실제 파일명·함수명과 함께 기술한다.
4. 코드 검증 항목 문항에는 구현 에이전트가 작성한 테스트에만 의존하지 않고 별도 검증 에이전트(`9`번)를 통해 수행한 **3대 독립 검증(1. 정답이 명확한 소규모 기준 케이스 대조 검증, 2. 용량·시간·누락 0건을 확인하는 하드 불변 조건 전수 검사, 3. 핵심 제약 검사 코드를 임시 제거했을 때 테스트가 실패하는지 확인하는 변이 검증)**, 그리고 클린 아키텍처 계층 분리(`SRP`)와 구성원 응답 화이트리스트(`to_user_dto`) 보안 감사를 구체적 테스트 함수명(`tests/test_slice_N.py`)과 함께 서술한다.
5. 복잡한 문제 해결 및 한계 통제 문항에는 **초기 제안된 과잉 기능이나 비결정론적 방식을 거절(`REJECTED`)한 구체적 사유**, 판단과 계산의 경계를 분리하여 계산·판정은 결정론적 코드(`core_engine.py`)로 고정한 설계 통제, 그리고 담당자 DM 루프와 슬라이스별 작동 원리 점검을 통해 점진적으로 고도화한 사례를 지정된 문서에 작성하고, 완료 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
추상적 일반론을 피하고 실제 작성된 파일명, 함수명, 데이터 수치, 테스트 케이스를 근거로 제시한다.
