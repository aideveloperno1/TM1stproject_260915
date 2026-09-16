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
| `rules.py` | 있음 | 규칙 원본 JSON v1.0 읽기·검증 (문구·대안·대안별 문서 문장·묶음 이름·재확인 필드·AI용 상황 설명) |
| `outcome.py` | 있음 | 검토 결과 형태, `no_finding`·`not_reviewed` 구분, `to_llm_summary()` |
| `context.py` | 있음 | 전국 레코드 선택·범위 표시·지역 안내 (2단계 화면과 공용) |
| `r07_indicator.py` | 있음 | R07 금액·비중과 성과지표 |
| `basic_checks.py` | 있음 | R01·R03·R04·R05 기본 검토 |
| `engine.py` | 있음 | 실행 순서, 규칙 ID·함수 일치 검사, 같은 merge_group 질문 연결 |

## 파일별 상세

### `rules.py` (있음)

- `load_rule_catalog()` → `RuleInfo(id, title, scope, summary, messages, options, related_fields, document_targets, merge_group, llm_context)`, `rules_by_id()`, `get_rule(id)`
- `OptionSpec(id, title, where, need, load, execution_fields, document)`, `OptionDocument(section, mode, lines, replace_key, appendix)`
- `RuleInfo.message(key, **values)`: 문구에 값 채움. `RuleInfo.context(key)`: 수치 없는 상황 설명
- `merge_group_label(key)`: 묶음 키의 한글 이름 (`merge_groups`)
- 불러올 때 검사 항목은 `resources/rules/README.md` 표 참고
- `FORBIDDEN_WORDS`: 문구에 쓰지 않는 판정 단어 (테스트가 `messages`·`llm_context` 전체를 검사)
- **문구·대안·문서 반영 위치는 JSON이 원본**, **조건 판단은 코드**(규칙 ID별 함수)가 맡는다
- 시작 시 검사: `engine.py`를 불러올 때 `check_rule_functions()`가 한 번 실행된다. `scope`가 implement/basic인데 실행 함수가 없으면 **앱이 시작하지 않는다** (화면을 여는 순간 500이 나지 않게). 요청 처리 중에는 다시 검사하지 않는다

### `outcome.py`

```
ReviewOutcome
  rule_id: str
  question_key: str               4단계 선택이 참조. 규칙 ID와 같아 질문마다 다르다
  merge_group: str | None         같은 값끼리 4단계에서 추가 입력을 공유
  kind: "question" | "notice" | "pending" | "held"
      question      담당자 선택이 필요한 질문 (4단계에서 필수)
      notice        오류 없이 해석 조건만 안내 (예: 참고용 지표). 선택은 가능하지만 필수 아님
      pending       추가 확정 필요 항목 (R05). 선택 없이 문서 8장에 기록
      held          근거 부족으로 결론 보류 (레코드 없음, blocked, needs_review, 비교 구간 없음). 선택 없이 문서 8장에 기록
  title: str
  message: str                    화면에 나갈 문장 (JSON 문구 + 값 채움)
  why: str | None                 "왜 묻나요?" 설명
  evidence_ids: list[str]
  scope_label: str | None         "전국 참고 — 특정 지역의 진단이 아님" 등
  region_note: str | None         시도·시군구 기획에 붙는 "전국 참고" 안내
  observations: dict              비교 요약 (구간 수 등). 문장 조립용, LLM에는 넘기지 않음
  options: tuple[OptionSpec]      choices/가 사용
  related_fields: tuple[str]      재확인 트리거 필드 (plan/changes.py 항목 이름과 같음)
  related_rule_ids: tuple[str]    같은 merge_group의 다른 질문 (카드는 합치지 않고 서로 가리킴)
  context_keys: tuple[str]        결과를 만들 때 고른 문구 키 → llm_context를 찾는 데 사용

ReviewResult(outcomes, no_finding, not_reviewed, evidence_id)
  no_finding     조건을 확인했으나 물을 것이 없는 규칙 ("문제없음")
  not_reviewed   NotReviewed(rule_id, title, scope_label, reason) — 이번 범위에서 검토하지 않음 (R06 분석 예시, R02 향후 기능)
```

- `evidence_ids`는 소비데이터를 쓰는 R07 결과에만 붙는다. R01·R03·R04·R05는 입력 항목만으로 판단하므로 비어 있다
- `llm/`에 넘길 때는 `to_llm_summary()`로 수치 없는 요약만 만든다: 규칙 ID, kind, 제목, 근거 유무, 적용 범위 라벨, 관련 규칙, `context`(`context_keys`로 찾은 `llm_context` 문장)

### `r07_indicator.py`

최종기획서 4장 첫 사례의 핵심 규칙.

실행 판단 순서
1. 성과지표에 외국인 결제 비중 또는 금액이 없음 → R07 대상 아님 (`not_reviewed` 아님, 결과 없음)
2. 근거 레코드 없음 → `held` (`held_no_record`). 레코드는 `context.select_main_record()`로 **전국(`national`, `ALL`)만** 고른다 (지역 연결 규칙 C-2 결정 전)
3. `applicability.R07.status`
   - `blocked` → `held`, 사유 표시 (2단계 화면은 수치를 모두 숨김)
   - `needs_review` → `held`, 확인할 내용 표시
4. 비교 가능한 구간이 하나도 없음 → `held`
5. 반대 방향 구간이 1개 이상이면 "왜 묻나요?"에 `why_opposite`, 없으면 `why_same`
6. 지표 용도
   - `reference`(참고 현황) → `notice`: 직접 평가 오류로 표시하지 않고 해석 조건(분모·미상 처리·전국 참고)만 안내 (워크플로우 S02, 11장). 고를 수 있는 대안은 B(해석 조건 명시)뿐
   - `direct`(직접 평가) → `question`: 목표가 금액 확대인지 비중 확대인지, 참여 실적을 별도로 수집할 수 있는지 질문
   - `unknown`(아직 모름) → `question`: 결론 없이 선택지만 제시
7. 목표와 지표 불일치 (금액 확대 목표 + 비중 지표, 또는 반대) → 질문일 때 문구 앞에 `goal_mismatch_prefix`

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
| R01 목표와 사용처 | 목표에 참여 상점 이용 확대 포함 + 쿠폰 사용처가 **비어 있음** | `question`: 사용처 범위 확인 |
| R03 대상과 자료 | 대상 문구에 "관광객·방문객·여행객" 중 하나 포함 + 성과지표가 외국인 카드 지표(비중·금액) | `question`: 외국인 전체 자료로 관광객 성과를 볼 수 있는지 (최종기획서 5-2: 외국인 전체와 관광객 구분) |
| R04 기간 | 사업 기간(시작일~종료일 포함)이 **31일 미만** + 지표 용도가 직접 평가 + 성과지표가 외국인 카드 지표 | `question`: 별도 실적·집계 주기 |
| R05 운영 조건 누락 | `plan.validation`의 pending 항목 존재 | `pending`: 추가 확정 필요 목록 |

- R06 → `not_reviewed` "분석 예시로 제시" (최종기획서 5-1)
- R02 → `not_reviewed` "지역 기준 확인 후 적용". **시도 근거가 allowed여도 자동 활성화하지 않는다** (8-4장)
- 사용자가 입력하지 않은 사실을 추정해 지적하지 않는다

### `engine.py`

- `run_review(plan, evidence) -> ReviewResult(outcomes, no_finding, not_reviewed, evidence_id)`
- 실행 순서: `RUN_ORDER = ("R07", "R03", "R04", "R01", "R05")` → R06·R02는 `not_reviewed`로 표시
- 모듈을 불러올 때 `check_rule_functions()` 실행 (JSON의 implement·basic 규칙마다 실행 함수가 있는지)
- 중복 질문 묶기: 같은 `merge_group` 질문끼리 **카드는 합치지 않고** `related_rule_ids`로 서로 가리킨다. 실제 묶기는 4단계 실행 조건 입력 공유 (`3검토질문계획.md` 결정 ③·④)
- 결과에 "검토한 규칙 / 검토하지 않은 규칙"을 모두 담는다 (시안: '문제없음'과 '검토하지 않음' 구분)
- 같은 입력·같은 근거 파일이면 항상 같은 결과 (난수·시간 의존 금지)

## 의존 관계

- 가져다 쓰는 곳: `plan/`, `evidence/`, `resources/rules/`
- 이 폴더를 쓰는 곳: `choices/`, `document/`, `web/`, `llm/`(요약만)
- 쓰면 안 되는 것: `web/`, FastAPI

## 테스트

`tests/test_review_rules.py` (있음)

| 확인 | 워크플로우 12장 |
|---|---|
| 참고용 지표 → `notice`, 오류 문구 없음 | 참고용 지표 |
| 직접 평가 + 반대 방향 구간 존재 → `question` | — |
| 방향이 같은 기간만 있을 때 반대 방향 문구 없음 | 방향이 같은 두 기간 |
| 전국 근거 + 시군구 기획 → 전국 참고 표시 | 전국 자료 + 특정 지역 기획 |
| 시도 근거 + 시군구 기획 → 넓은 범위 표시, R02 비활성 | 검증 시도 자료 + 시군구 기획 |
| applicability blocked/needs_review → 실행 안 함/보류 | — |
| 자료 확보 미정 → R05 pending | 자료 수집 미정 |
| R03·R04·R07 같은 묶음 → 카드는 따로, 서로 `related_rule_ids`로 가리킴, 질문 키는 규칙 ID로 서로 다름 | — |
| JSON 규칙 ID와 코드 함수 일치 | — |
