# review/ — 검토 규칙 실행 (S02)

## 역할

기획 원안(`plan/`)과 분석 근거(`evidence/`)를 받아 규칙 R01~R07을 실행하고, 화면에 보여줄 **검토 결과(질문·근거·대안)**를 만든다.
판정·점수를 내지 않는다. 관측은 질문으로 전달하고 결정은 담당자가 한다.

## 기준 문서

- 워크플로우 11장 검토 규칙과 문서 반영, S02 조회와 질문
- 최종기획서 4-3 서비스가 묻는 질문, 4-4 선택할 보완 방법, 5장 추가 사례, 11장 구현 범위
- checks.md: R07 검토 구현, R01·R03·R04·R05 기본 검토, R06 분석 예시, R02 향후 기능

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | 비어 있음 |
| `rules.py` | 있음 | 규칙 원본 JSON v1.0 읽기 (문구·대안·merge_group·재확인 필드) |
| `outcome.py` | 있음 | 검토 결과 형태, `no_finding`·`not_reviewed` 구분, `to_llm_summary()` |
| `context.py` | 있음 | 전국 레코드 선택·범위 표시·지역 안내 (2단계 화면과 공용) |
| `r07_indicator.py` | 있음 | R07 금액·비중과 성과지표 |
| `basic_checks.py` | 있음 | R01·R03·R04·R05 기본 검토 |
| `engine.py` | 있음 | 실행 순서, 규칙 ID·함수 일치 검사, 같은 merge_group 질문 연결 |

## 파일별 상세

### `rules.py` (있음 → 확장)

- 현재: `load_rule_catalog()` → `RuleInfo(id, title, scope, summary)`
- 확장: JSON에서 질문 문구, 대안 목록, 대안별 문서 반영 위치·필요 자료·운영 부담·추가 입력 필드를 읽는다
- **문구·대안·문서 반영 위치는 JSON이 원본**, **조건 판단은 코드**(규칙 ID별 함수)가 맡는다
- 시작 시 검사: JSON의 규칙 ID마다 코드 함수가 있는지, `scope`가 implement/basic인데 함수가 없으면 오류

### `outcome.py`

```
ReviewOutcome
  rule_id: str
  question_key: str               4단계 선택이 참조. 규칙 ID와 같아 질문마다 다르다
  merge_group: str | None         같은 값끼리 4단계에서 추가 입력을 공유
  kind: "question" | "notice" | "pending" | "not_reviewed" | "held"
      question      담당자 선택이 필요한 질문
      notice        오류 없이 해석 조건만 안내 (예: 참고용 지표)
      pending       추가 확정 필요 항목 (R05)
      not_reviewed  이번 범위에서 검토하지 않음 (R06 예시, R02 향후) — "문제없음"과 구분
      held          근거 부족으로 결론 보류 (needs_review, no_data 등)
  title: str
  message: str                    화면에 나갈 문장 (JSON 문구 + 값 채움)
  why: str | None                 "왜 묻나요?" 설명
  evidence_ids: list[str]
  scope_label: str | None         "전국 참고 — 특정 지역의 진단이 아님" 등
  observations: dict | None       비교 요약 (구간 수 등). 문장 조립용, LLM에는 넘기지 않음
  options: list[OptionSpec]       choices/가 사용
  related_fields: list[str]       재확인 트리거 필드 (plan/changes.py와 연결)
```

- `llm/`에 넘길 때는 `to_llm_summary()`로 수치 없는 요약만 만든다 (규칙 ID, kind, 방향 라벨, 적용 범위, 사용자 목표·지표 용도)

### `r07_indicator.py`

최종기획서 4장 첫 사례의 핵심 규칙.

실행 판단 순서
1. 성과지표에 외국인 결제 비중 또는 금액이 없음 → R07 대상 아님 (`not_reviewed` 아님, 결과 없음)
2. 근거 레코드 없음 또는 `applicability.R07.status`
   - `blocked` → 실행 안 함, 사유 표시
   - `needs_review` → `held`, 확인할 내용 표시
3. 비교 가능한 구간이 하나도 없음 → `held`
4. 지표 용도
   - `reference`(참고 현황) → `notice`: 직접 평가 오류로 표시하지 않고 해석 조건(분모·미상 처리·전국 참고)만 안내 (워크플로우 S02, 11장)
   - `direct`(직접 평가) → `question`: 목표가 금액 확대인지 비중 확대인지, 참여 실적을 별도로 수집할 수 있는지 질문
   - `unknown`(아직 모름) → `question`: 결론 없이 선택지만 제시
5. 목표와 지표 불일치 (금액 확대 목표 + 비중 지표 등) → 질문 문구에 불일치를 먼저 언급

문구 원칙
- 반대 방향 구간이 0개여도 검토 불필요라고 하지 않고, 반대 방향이 있어도 비중을 삭제하라고 하지 않는다 (8-3장)
- 방향이 같은 기간에 "방향이 달랐다" 예시 문구를 재사용하지 않는다 (12장)
- 작은 차이에 빨간 경고·"오류" 단어를 쓰지 않는다
- 지역 기획 + 전국 근거 → 반드시 "전국 참고" 표시. 시도 근거 + 시군구 기획 → "넓은 범위의 참고자료" (8-4장)
- 비교 B(미상 포함·제외)는 보조 근거로만 쓰고 비교 A와 합치지 않는다

대안 (JSON 원본, 최종기획서 4-4장)
- A 참여 실적 추가: 추가 입력 = 수집자료, 확보 여부, 담당자, 주기
- B 해석 조건 명시
- C 자료 확보 전 (추가 확정 필요로 기록)
- D 정밀 BC 분석 요청서 초안 (계약·제공 확정처럼 표시 금지)
- 공통: 원안 유지, 보류

### `basic_checks.py`

조건은 초안이며 `docs/review_rules.md`에서 데이터 담당과 확정한다.

| 규칙 | 실행 조건 (초안) | 결과 |
|---|---|---|
| R01 목표와 사용처 | 목표에 참여 상점 이용 확대 포함 + 사용처가 비어 있거나 범위가 불명확 | `question`: 사용처 범위 확인 |
| R03 대상과 자료 | 대상 문구에 "관광객" 포함 + 성과지표가 외국인 카드 지표 | `question`: 외국인 전체 자료로 관광객 성과를 볼 수 있는지 (최종기획서 5-2: 외국인 전체와 관광객 구분) |
| R04 기간 | 사업 기간이 한 달 미만이거나 월 단위와 맞지 않음 + 월별 카드 지표를 직접 평가 | `question`: 별도 실적·집계 주기 |
| R05 운영 조건 누락 | `plan.validation`의 pending 항목 존재 | `pending`: 추가 확정 필요 목록 |

- R06 → `not_reviewed` "분석 예시로 제시" (최종기획서 5-1)
- R02 → `not_reviewed` "지역 기준 확인 후 적용". **시도 근거가 allowed여도 자동 활성화하지 않는다** (8-4장)
- 사용자가 입력하지 않은 사실을 추정해 지적하지 않는다

### `engine.py`

- `run_review(plan, evidence) -> ReviewResult(outcomes, not_reviewed, evidence_used)`
- 실행 순서: R07 → R03 → R04 → R01 → R05 → R06·R02 표시
- 중복 질문 묶기: R03·R04·R07이 같은 추가 자료(참여 실적 등)를 요구하면 질문 하나로 묶고 `evidence_ids`와 `rule_id` 목록은 모두 유지 (11장)
- 결과에 "검토한 규칙 / 검토하지 않은 규칙"을 모두 담는다 (시안: '문제없음'과 '검토하지 않음' 구분)
- 같은 입력·같은 근거 파일이면 항상 같은 결과 (난수·시간 의존 금지)

## 의존 관계

- 가져다 쓰는 곳: `plan/`, `evidence/`, `resources/rules/`
- 이 폴더를 쓰는 곳: `choices/`, `document/`, `web/`, `llm/`(요약만)
- 쓰면 안 되는 것: `web/`, FastAPI

## 테스트

`tests/test_review_rules.py` (예정)

| 확인 | 워크플로우 12장 |
|---|---|
| 참고용 지표 → `notice`, 오류 문구 없음 | 참고용 지표 |
| 직접 평가 + 반대 방향 구간 존재 → `question` | — |
| 방향이 같은 기간만 있을 때 반대 방향 문구 없음 | 방향이 같은 두 기간 |
| 전국 근거 + 시군구 기획 → 전국 참고 표시 | 전국 자료 + 특정 지역 기획 |
| 시도 근거 + 시군구 기획 → 넓은 범위 표시, R02 비활성 | 검증 시도 자료 + 시군구 기획 |
| applicability blocked/needs_review → 실행 안 함/보류 | — |
| 자료 확보 미정 → R05 pending | 자료 수집 미정 |
| R03·R07 중복 질문 → 하나로 묶고 근거 ID 둘 다 유지 | — |
| JSON 규칙 ID와 코드 함수 일치 | — |
