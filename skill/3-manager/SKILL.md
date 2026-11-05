---
name: 3-manager
description: "INBOX.md와 README.md에서 현업 담당자(1명 또는 복수)의 소속과 역할을 확인하여, 거시적 질문(이용 주체·사용 빈도·창출 가치·운영 환경)부터 미시적 질문(데이터 근거 예외·허용 임계값)으로 이어지는 질문 전략을 MANAGERS.md에 매핑한다."
---
# 3-manager

## 역할
과제에 등장하는 현업 담당자(1명 또는 2명 이상)의 소속과 업무 역할을 파악하고, **거시적 맥락 질문(누가·어떻게·얼마나 자주 사용하는지, 어떤 핵심 가치를 창출해야 하는지)에서 미시적 데이터 질문(데이터 특이점 해석 및 허용 임계값)으로 좁혀 들어가는 깔때기(Funnel) 질문 전략**을 `sk/work/MANAGERS.md`에 정의한다.

## 입출력 파일
- 읽기:
  - `sk/work/INBOX.md`
  - `README.md`
  - `sk/work/EDA_REPORT.md`
  - `sk/work/EDA_SUPPLEMENT.md`
  - `references/MANAGERS_TEMPLATE.md`
- 쓰기:
  - `sk/work/MANAGERS.md`
  - `sk/work/OUTBOX.md`

## 번들 리소스
- 레퍼런스: `references/MANAGERS_TEMPLATE.md`

## 작업 절차
1. `sk/work/INBOX.md`와 `README.md`에서 현업 담당자가 1명인지 2명 이상인지, 각자의 이름·소속·역할 및 안내 문구를 확인한다.
2. `EDA_REPORT.md`와 `EDA_SUPPLEMENT.md`를 함께 참고하여, 담당자에게 확인해야 할 거시적 업무/서비스 맥락과 미시적 데이터 특이점·운영 기준 후보를 파악한다.
3. `references/MANAGERS_TEMPLATE.md` 양식에 따라 담당자 구성 형태, 담당자별 핵심 관심사, 그리고 **`[1단계 거시(사용자·빈도·가치·경계) -> 2단계 미시(데이터 수치·임계값) -> 3단계 서면 합의]` 질문 매핑**을 `sk/work/MANAGERS.md`에 작성하고, 매핑 요약을 `sk/work/OUTBOX.md`에 적는다.

## 응답 지침
담당자에게 처음부터 지엽적인 숫자만 묻지 않고, 서비스를 누가·어떻게·얼마나 자주 쓰며 어떤 가치를 가장 중요하게 보는지(거시 질문)부터 시작해 구체적인 데이터 수치·임계값(미시 질문)으로 자연스럽게 이어지도록 설계한다.
