# tests/ — pytest 테스트

## 역할

기획 문서의 시험 항목(워크플로우 12장, 8-5장)을 코드로 확인한다. 실행: `uv run pytest`.
완료 기준은 "화면이 있다"가 아니라 입력·근거·선택·출력이 일치하는 것이다 (최종기획서 11장).

## 만들 파일

개수는 매개변수화한 경우를 포함한 수집 기준이다(2026-09-17, 전체 413개). 바뀌면 `uv run pytest --collect-only -q`로 다시 센다.

| 파일 | 개수 | 대상 |
|---|---:|---|
| `conftest.py` | — | 공통: `PSM_*` 환경변수 제거, 합성 근거 상태로 고정, `use_evidence(path, **env)` 픽스처, 받아 둔 모델 확인이 실제 Ollama에 닿지 않게 막음 |
| `helpers.py` | — | 공통: `VALID_FORM`, `parse()` |
| `evidence_helpers.py` | — | 공통: 경계 사례 경로·목록(`fixture_path`), `base_data()` |
| `document_helpers.py` | — | 공통: 원안·선택·문서 생성 준비 |
| `test_plan_validation.py` | 9 | `plan/validation.py` |
| `test_plan_changes.py` | 7 | `plan/changes.py` |
| `test_config.py` | 15 | `config.py` (모델 목록 `PSM_LLM_MODELS` 포함) |
| `test_formatters.py` | 20 | `formatting.py` |
| `test_evidence_loader.py` | 44 | `evidence/schema.py`, `loader.py`, 경계 사례 생성 일치 |
| `test_evidence_compare.py` | 24 | `evidence/compare.py` |
| `test_evidence_summary.py` | 6 | `evidence/summary.py` |
| `test_demo_evidence.py` | 6 | 합성 근거 파일 |
| `test_review_rules.py` | 41 | `review/` (규칙 로드·실행·문구 검사·`llm_context`) |
| `test_choices.py` | 19 | `choices/` |
| `test_document_describe.py` | 8 | `document/describe.py` |
| `test_document_builder.py` | 19 | `document/builder.py` |
| `test_document_render.py` | 11 | `document/render.py` |
| `test_document_filename.py` | 5 | `document/filename.py` |
| `test_llm_provider.py` | 14 | `llm/base.py`, `llm/local.py`(받아 둔 모델 확인·`reasoning_effort`), `PSM_LLM_TIMEOUT_S` |
| `test_llm_catalog.py` | 4 | `llm/catalog.py`, `resources/llm/models.json` |
| `test_llm_prompt.py` | 11 | `llm/prompt.py` |
| `test_llm_guard.py` | 14 | `llm/guard.py` |
| `test_evidence_state.py` | 7 | `web/evidence_state.py` |
| `test_evidence_view.py` | 31 | `web/evidence_view.py` |
| `test_top_badge.py` | 4 | 상단 자료 표시 |
| `test_routes.py` | 10 | 1단계 입력, 단계 잠금, 정적 파일 |
| `test_evidence_routes.py` | 12 | 2단계 화면 |
| `test_question_routes.py` | 10 | 3단계 화면 |
| `test_opinion_routes.py` | 22 | 3단계 AI 참고 의견 주소·모델별 캐시·모델 선택 |
| `test_choice_routes.py` | 13 | 4단계 화면 |
| `test_draft_routes.py` | 16 | 5단계 화면·내려받기·PDF 버튼·인쇄 CSS |
| `test_public_bundle.py` | 8 | `scripts/check_public_bundle.py` |
| `test_boundaries.py` | 3 | 패키지 의존 방향 (직접 import) |

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
| 자료 수집 미정 | test_review_rules, test_choices, test_document_builder |
| 목표 유지·대안 취소 | test_choices, test_document_builder |
| 목표·지역 변경 | test_plan_changes, test_choices, test_choice_routes |
| Markdown 내보내기 | test_document_render, test_draft_routes (다운로드) + 외부 편집기 수동 확인 (미실시) |
| 공개 배포 | test_public_bundle |

## 파일별 핵심

### `test_boundaries.py`

`ast`로 각 패키지의 import 문을 읽어 검사한다 (상대 import 포함).
- `plan`, `evidence`, `review`, `choices`, `document`, `llm` → `fastapi`, `starlette`, `policy_signal_map.web`·`app` 직접 import 금지
- `evidence` → `review`, `choices`, `document`, `llm`, `plan` 직접 import 금지
- `llm` → `evidence` 직접 import 금지
- 한계: 거쳐서 불러오는 import(`llm → review → evidence`)와 위 세 규칙 밖의 역방향 import(예: `review` → `choices`)는 막지 못한다. LLM 수치 차단의 실제 장치는 `to_llm_summary`·`llm/prompt.py`·`llm/guard.py`다

### `test_public_bundle.py`

`scripts/check_public_bundle.py`의 검사 함수를 호출해 추적 파일에 실제 자료·`.env`·`private/`·원자료(csv 등) 파일이 없는지 확인한다. 임시 git 저장소에 한글 이름 파일을 넣어 이스케이프 문제 없이 검사되는지도 확인한다. git이 없는 환경에서는 건너뛴다.

## 원칙

- 실제 LLM·외부 네트워크를 호출하지 않는다. LLM은 `llm.base.FakeProvider`와 `monkeypatch`(`urllib.request.urlopen`, `web.routes.opinions.get_provider`)로 시험한다
- 실제 카드 분석 파일을 읽지 않는다. 경계 사례는 `fixtures/`의 합성 파일로 만든다
- 테스트 이름은 확인하는 기획 규칙을 문장으로 적는다 (예: `test_reference_indicator_has_no_error_message`)
