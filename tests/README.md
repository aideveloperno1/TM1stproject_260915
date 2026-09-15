# tests/ — pytest 테스트

## 역할

기획 문서의 시험 항목(워크플로우 12장, 8-5장)을 코드로 확인한다. 실행: `uv run pytest`.
완료 기준은 "화면이 있다"가 아니라 입력·근거·선택·출력이 일치하는 것이다 (최종기획서 11장).

## 만들 파일

| 파일 | 상태 | 대상 폴더 | 시점 |
|---|---|---|---|
| `helpers.py` | 있음 | 공통: `VALID_FORM`, `parse()` | — |
| `test_plan_validation.py` | 있음 (9개) | `plan/` | — |
| `test_routes.py` | 있음 (9개, 단계별 확장) | `web/routes/` | 계속 |
| `test_evidence_loader.py` | 예정 | `evidence/schema.py`, `loader.py` | 9/16 |
| `test_evidence_compare.py` | 예정 | `evidence/compare.py` | 9/16~17 |
| `test_evidence_summary.py` | 예정 | `evidence/summary.py` | 9/17 |
| `test_public_bundle.py` | 예정 | `scripts/check_public_bundle.py` | 9/16~17 |
| `test_boundaries.py` | 예정 | 패키지 의존 방향 | 9/17 |
| `test_review_rules.py` | 예정 | `review/` | 9/17 |
| `test_formatters.py` | 예정 | `web/formatters.py` | 9/17 |
| `test_plan_changes.py` | 예정 | `plan/changes.py` | 9/17~18 |
| `test_choices.py` | 예정 | `choices/` | 9/17~18 |
| `test_document.py` | 예정 | `document/` | 9/18 |
| `test_llm_guard.py`, `test_llm_prompt.py` | C 단계 | `llm/` | 후속 |

## 워크플로우 12장 시험 항목 대응

| 12장 시험 | 테스트 파일 |
|---|---|
| GENDER_CD=x와 AGE_CD=x가 섞임 | 서비스 범위 아님 → `../Analysis/` (원본 집계) |
| 숫자·코드 오류 | test_evidence_loader |
| 분모 0·자료 없음 | test_evidence_loader, test_evidence_compare |
| 미상 0 또는 관측 행 없음 | test_evidence_loader, test_formatters |
| 금액·비중 비교 A / 두 비중 비교 B | test_evidence_compare |
| 이전 F=0·변화 없음·월 누락 | test_evidence_compare |
| 아주 작은 방향 차이 | test_evidence_compare, test_formatters |
| 방향이 같은 두 기간 | test_review_rules |
| 전국 자료 + 특정 지역 기획 | test_review_rules, test_routes |
| 검증 시도 자료 + 시군구 기획 | test_review_rules |
| 참고용 지표 | test_review_rules |
| 자료 수집 미정 | test_review_rules, test_choices, test_document |
| 목표 유지·대안 취소 | test_choices, test_document |
| 목표·지역 변경 | test_plan_changes, test_choices |
| Markdown 내보내기 | test_document, test_routes (다운로드) + 외부 편집기 수동 확인 |
| 공개 배포 | test_public_bundle |

## 파일별 핵심

### `test_boundaries.py`

`ast`로 각 패키지의 import 문을 읽어 검사한다.
- `plan`, `evidence`, `review`, `choices`, `document` → `fastapi`, `policy_signal_map.web` import 금지
- `evidence` → `review`, `choices`, `document`, `llm` import 금지
- `llm` → `evidence` import 금지

### `test_public_bundle.py`

`scripts/check_public_bundle.py`의 검사 함수를 호출해 추적 파일에 실제 자료·`.env`·`private/` 파일이 없는지 확인한다. git이 없는 환경에서는 건너뛴다.

## 원칙

- 실제 LLM·외부 네트워크를 호출하지 않는다
- 실제 카드 분석 파일을 읽지 않는다. 경계 사례는 `fixtures/`의 합성 파일로 만든다
- 테스트 이름은 확인하는 기획 규칙을 문장으로 적는다 (예: `test_reference_indicator_has_no_error_message`)
