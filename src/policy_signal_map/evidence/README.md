# evidence/ — 분석 근거 파일 읽기·검증, 금액·비중 비교 계산

## 역할

데이터 분석 담당이 만든 `review_evidence.json`을 읽어 형식·상태값·수치 관계를 검증하고, 인접 월의 **비교 A(외국인 금액 vs 전체 분모 비중)**와 **비교 B(전체 분모 비중 vs 미상 제외 비중)**를 계산한다.
화면·규칙·LLM과 무관한 순수 계산 계층이다. 숫자를 보정하거나 새로 만들지 않는다.

## 기준 문서

- 워크플로우 8-1 F·T·U 정의, 8-2 두 종류의 비교, 8-3 작은 차이 표시, 8-4 전국 우선·시도 조건부, 8-5 검증 예시
- 워크플로우 9-1 `calculation_status`, 9-2 `applicability`, 9-3 파일 형식
- 워크플로우 12장 시험 항목 중 서비스 담당분

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 예정 (9/16) | 비어 있음 |
| `schema.py` | 예정 (9/16) | 근거 파일 데이터 형태와 검증 |
| `loader.py` | 예정 (9/16) | 파일 읽기, 버전·종류 확인, 오류 메시지 |
| `compare.py` | 예정 (9/16~17) | 비교 A/B, 방향, opposite, 증감률 |
| `summary.py` | 예정 (9/17) | 기간 합산 비중, 반대 방향 구간 수 등 화면·규칙용 요약 |

## 파일별 상세

### `schema.py`

워크플로우 9-3장 형식을 그대로 옮긴 dataclass. 필드명은 JSON과 같게 둔다 (데이터 담당과 대조하기 쉽게).

```
EvidenceFile
  schema_version: "2.0"          지원 버전 목록에 없으면 오류
  dataset_version: str           합성은 "demo-"로 시작
  records: list[EvidenceRecord]

EvidenceRecord
  evidence_id: str               파일 안에서 중복 금지
  data_kind: "synthetic" | "real"
  scope: Scope
    geographic_scope: "national" | "sido"
    region_key: "ALL" | 시도 고정 키     national이면 반드시 ALL
    population: "foreign_code_3"
    industry_scope: "all_provided"
    age_scope: "all"
    period_start / period_end: "YYYY-MM"
  region_basis: str              예: "unknown"
  applicability: {"R07" | "R06" | "R02": Applicability}
    status: "allowed" | "needs_review" | "blocked"
    reason: str                  빈 문자열 금지
  amount_unit: "KRW"
  months: list[MonthValue]
  limitations: list[str]

MonthValue
  month: "YYYY-MM"
  calculation_status: "ok" | "no_data" | "invalid_input" | "invalid_denominator"
  foreign_amount / total_amount / unknown_amount: int | None     원 단위 정수
  transaction_count: int | None  고객 수가 아니라 거래 건수
  foreign_share_pct / known_only_share_pct / unknown_share_pct: float | None   8% → 8.0
  warnings: list[str]
```

검증 규칙 (위반 시 `EvidenceError`, 조용히 넘어가지 않음)

1. 목록에 없는 상태값 → 파일 검증 오류 (9-2장)
2. `reason` 누락·빈 값 → 오류
3. `ok` 월: F·T·U 모두 정수, `0 ≤ F`, `0 ≤ U`, `F ≤ T`, `U ≤ T`, `F + U ≤ T` (8-1장)
4. `ok` 월: 파일의 `*_share_pct`와 F·T·U로 다시 계산한 값의 차이가 허용 오차(1e-6%p)를 넘으면 경고. 숫자를 고치지 않는다
5. 금액이 소수·문자열·음수 → 오류
6. months는 `period_start`~`period_end`의 모든 월을 순서대로 포함해야 한다. **누락 월을 생략하지 않고 상태·null로 둔다** (9-3장)
7. `no_data` 월의 금액은 null이어야 한다. 0을 넣으면 오류 ("관측 0"과 "자료 없음" 구분, 8-1장)
8. `amount_unit != "KRW"` → 오류

### `loader.py`

- `load_evidence(path) -> EvidenceFile` : JSON 읽기 → `schema.py` 검증
- `EvidenceError(messages: list[str])` : 사용자에게 보여줄 한국어 메시지 목록. 어느 레코드·월·필드인지 포함
- 확인 사항
  - `schema_version` 지원 여부 → 다르면 "데이터 담당에게 버전 확인" 메시지로 멈춤
  - 한 파일 안에 `synthetic`과 `real`이 섞이면 오류 (8-2장: 합성과 실제를 섞지 않음)
  - `find_record(file, geographic_scope, region_key)` : 요청한 범위가 없으면 None. **자동으로 전국 자료를 지역 자료처럼 대체하지 않는다** (9-3장)
- 파일 경로는 `config.py`에서 받는다. 이 모듈이 경로를 정하지 않는다
- 로드 결과는 앱 시작 시 한 번 읽어 캐시한다 (파일 교체 시 서버 재시작)

### `compare.py`

인접 월 0 → 1 쌍마다 계산한다. **정수 연산과 `fractions.Fraction`만 사용**하고 float는 표시 직전에만 쓴다.

```
MonthPair
  month_0, month_1
  status: "ok" | "skipped"
  skip_reason: str | None            예: "2026-04 no_data", "월 누락"

  foreign_amount_diff: int | None           F1 - F0
  foreign_amount_growth: Fraction | None    (F1-F0)/F0, F0 == 0 이면 None
  total_amount_growth: Fraction | None      (T1-T0)/T0, T0 == 0 이면 None
  share_change_pp: Fraction | None          (F1/T1 - F0/T0) × 100
  known_only_share_change_pp: Fraction | None   (F1/(T1-U1) - F0/(T0-U0)) × 100

  comparison_a: DirectionComparison   외국인 금액 방향 vs 전체 분모 비중 방향
  comparison_b: DirectionComparison   전체 분모 비중 방향 vs 미상 제외 비중 방향

DirectionComparison
  left: "up" | "down" | "flat" | None
  right: "up" | "down" | "flat" | None
  opposite: bool | None
```

계산 규칙

| 규칙 | 근거 |
|---|---|
| 두 달 중 하나라도 `calculation_status != "ok"` → 파생 비중 비교 안 함, `skipped`와 사유 | 8-2 예외, 9-2 |
| 월이 연속되지 않으면 비교 안 함 (누락 월 건너뛰어 연결 금지) | 8-2 예외 |
| 금액 방향: `F1 - F0`의 부호 | 8-2 |
| 전체 분모 비중 방향: `F1×T0 - F0×T1`의 부호 (T0, T1 > 0일 때만) | 8-2 |
| 미상 제외 비중 방향: `F1×(T0-U0) - F0×(T1-U1)`의 부호 (두 분모 > 0일 때만) | 8-2 |
| 분모 ≤ 0 → 해당 방향 None | 8-1 |
| `opposite`: 양쪽 모두 up/down이고 서로 다를 때만 True, flat 포함 시 False, None 포함 시 None | 8-2 |
| 이전 F = 0 → 증감률 None, 금액 차이 방향은 유효 | 8-2 예외 |
| 비교 A와 B를 합쳐 점수를 만들지 않는다 | 8-2 |
| 반올림한 퍼센트로 방향을 판단하지 않는다 | 8-2 |
| 자료 범위·버전이 다른 레코드끼리 비교하지 않는다 | 8-2 |

### `summary.py`

- `period_totals(record) -> PeriodTotals` : `ok` 월의 F·T·U를 **각각 합산한 뒤** 기간 비중 계산 (8-1장). 제외한 월 목록 포함
- `pair_summary(pairs) -> PairSummary` : 전체 구간 수, 비교 가능 구간 수, 비교 A 반대 방향 구간 수, 같은 방향 구간 수, 보류 구간 수
- 규칙·화면·문서가 "5개 구간 중 N개" 같은 문장을 만들 때 이 결과만 사용한다. 문장을 만들지는 않는다 (문장은 `review/`·`web/`)
- 반대 방향 구간만 골라 반환하는 함수는 만들지 않는다 (8-3장: 반대 방향 구간만 골라 보여주지 않음)

## 의존 관계

- 가져다 쓰는 곳: 표준 라이브러리만 (`json`, `dataclasses`, `fractions`)
- 이 폴더를 쓰는 곳: `review/`, `document/`, `web/`, `scripts/build_demo_evidence.py`
- 쓰면 안 되는 곳: `llm/` (카드 수치 차단), `web/`·FastAPI import 금지

## 테스트

| 테스트 파일 | 확인 내용 | 워크플로우 |
|---|---|---|
| `tests/test_evidence_loader.py` | 상태값 오류, reason 누락, F+U>T, 금액 소수·음수, no_data에 0, 월 누락 생략, schema_version 불일치, synthetic/real 혼합, 전국 자동 대체 없음 | 9-1, 9-2, 12장 "숫자·코드 오류", "미상 0 또는 관측 행 없음" |
| `tests/test_evidence_compare.py` | `tests/fixtures/evidence/` 시나리오 전부, 큰 금액 교차곱 정확성, 0.01%p 미만 변화의 방향 유지 | 8-5 전체, 12장 "분모 0·자료 없음", "비교 A/B", "이전 F=0·변화 없음·월 누락", "아주 작은 방향 차이" |
| `tests/test_evidence_summary.py` | 기간 합산 비중이 월 비중 평균이 아님, 보류 구간 수 | 8-1 |

12장의 "GENDER_CD=x와 AGE_CD=x가 섞임"은 원본 CSV 집계 단계 시험이라 데이터 담당(`../Analysis/`) 소관이다.
