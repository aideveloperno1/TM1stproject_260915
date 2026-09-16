# tests/ — pytest 테스트

## 역할

기획 문서의 시험 항목(워크플로우 12장, 8-5장)을 코드로 확인한다. 실행: `uv run pytest`.
완료 기준은 "화면이 있다"가 아니라 입력·근거·선택·출력이 일치하는 것이다 (최종기획서 11장).

## 만들 파일

| 파일 | 상태 | 대상 폴더 | 시점 |
|---|---|---|---|
| `helpers.py` | 있음 | 공통: `VALID_FORM`, `parse()` | — |
| `evidence_helpers.py` | 있음 | 공통: 경계 사례 경로·목록, `base_data()` | — |
| `test_plan_validation.py` | 있음 (9개) | `plan/` | — |
| `test_routes.py` | 있음 (9개, 단계별 확장) | `web/routes/` | 계속 |
| `test_config.py` | 있음 (10개) | `config.py` | — |
| `test_evidence_loader.py` | 있음 (44개) | `evidence/schema.py`, `loader.py`, 경계 사례 생성 일치 | — |
| `test_evidence_compare.py` | 있음 (24개) | `evidence/compare.py` | — |
| `test_evidence_summary.py` | 있음 (6개) | `evidence/summary.py` | — |
| `test_demo_evidence.py` | 있음 (6개) | 합성 근거 파일 | — |
| `test_public_bundle.py` | 있음 (8개) | `scripts/check_public_bundle.py` | — |
| `test_boundaries.py` | 있음 (3개) | 패키지 의존 방향 (직접 import) | — |
| `test_review_rules.py` | 있음 (28개) | `review/` | — |
| `test_formatters.py` | 있음 (31개) | `formatting.py` | — |
| `test_plan_changes.py` | 있음 (9개) | `plan/changes.py` | — |
| `test_choices.py` | 있음 (20개) | `choices/` | — |
| `test_evidence_view.py`, `test_evidence_state.py`, `test_top_badge.py` | 있음 | `web/` 표시 | — |
| `test_evidence_routes.py`, `test_question_routes.py`, `test_choice_routes.py`, `test_draft_routes.py` | 있음 | 2~5단계 화면 | — |
| `document_helpers.py` | 있음 | 공통: 원안·선택·문서 생성 준비 | — |
| `test_document_describe.py` (8), `test_document_builder.py` (19), `test_document_render.py` (10), `test_document_filename.py` (5) | 있음 | `document/` | — |
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

`ast`로 각 패키지의 import 문을 읽어 검사한다 (상대 import 포함).
- `plan`, `evidence`, `review`, `choices`, `document` → `fastapi`, `starlette`, `policy_signal_map.web`·`app` 직접 import 금지
- `evidence` → `review`, `choices`, `document`, `llm`, `plan` 직접 import 금지
- `llm` → `evidence` 직접 import 금지
- 한계: 거쳐서 불러오는 import(`llm → review → evidence`)는 막지 못한다. LLM 수치 차단의 실제 장치는 C 단계 요약 함수·출력 검사다

### `test_public_bundle.py`

`scripts/check_public_bundle.py`의 검사 함수를 호출해 추적 파일에 실제 자료·`.env`·`private/`·원자료(csv 등) 파일이 없는지 확인한다. 임시 git 저장소에 한글 이름 파일을 넣어 이스케이프 문제 없이 검사되는지도 확인한다. git이 없는 환경에서는 건너뛴다.

## 원칙

- 실제 LLM·외부 네트워크를 호출하지 않는다
- 실제 카드 분석 파일을 읽지 않는다. 경계 사례는 `fixtures/`의 합성 파일로 만든다
- 테스트 이름은 확인하는 기획 규칙을 문장으로 적는다 (예: `test_reference_indicator_has_no_error_message`)
