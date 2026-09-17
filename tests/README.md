# `tests/` — 자동 시험 (pytest)

> 최신화: 2026-09-17

## 이 폴더는 무엇인가

서비스가 기획 문서대로 동작하는지 **자동으로 확인하는 시험 코드**를 모아 둔 곳입니다. `uv run pytest` 한 줄로 전부 실행되며, 코드를 고친 뒤에는 항상 돌려 봅니다.
계산이 맞는지, 규칙 문장에 판정 단어가 없는지, 화면 주소가 제대로 응답하는지, 공개 저장소에 실제 자료가 섞이지 않았는지까지 확인합니다.
실제 AI 모델이나 실제 카드 자료는 쓰지 않고, 가짜 AI와 합성 자료로만 시험합니다.

## 파일 목록

| 파일 | 하는 일 (쉬운 말) | 언제 보거나 고치나 |
|---|---|---|
| `conftest.py` | **모든 시험의 공통 준비.** 내 컴퓨터 설정에 상관없이 합성 자료로 고정하고, 실제 AI 서버에 닿지 않게 막음 | 시험 환경 전체에 적용할 준비가 필요할 때 |
| `helpers.py` | 여러 시험이 쓰는 **올바른 입력 폼 예시**와 폼 읽기 도우미 | 입력 칸이 늘었을 때 |
| `evidence_helpers.py` | 시험용 근거 파일 위치·목록과 기본 근거 데이터 | 시험용 근거 파일을 추가했을 때 |
| `document_helpers.py` | 보완 기획안 시험용 원안·선택 준비 | 문서 시험 준비 방식을 바꿀 때 |
| `test_plan_validation.py`, `test_plan_changes.py` | **기획 입력** 확인: 빠진 칸 검사, 바뀐 칸 찾기 | 입력 규칙을 바꿨을 때 |
| `test_config.py` | **설정 읽기** 확인: 근거 파일 경로, AI 설정, 모델 목록, 대기 시간 | 설정 항목을 바꿨을 때 |
| `test_formatters.py` | **숫자 표시 모양** 확인: 억원·%·%p, 아주 작은 값, 자료 없음 | 표시 형식을 바꿨을 때 |
| `test_evidence_loader.py`, `test_evidence_compare.py`, `test_evidence_summary.py` | **근거 파일 검사와 비교 계산** 확인 (경계 사례 22개 포함) | 근거 파일 형식이나 계산을 바꿨을 때 |
| `test_demo_evidence.py` | **시연용 가짜 근거 파일**이 도구 결과와 같고 가상 규모인지 확인 | 가짜 근거 파일을 다시 만들었을 때 |
| `test_review_rules.py` | **검토 규칙** 확인: 언제 질문이 나오는지, 문장에 판정 단어·숫자가 없는지 | 규칙 조건이나 문장을 바꿨을 때 |
| `test_choices.py` | **보완 선택** 확인: 저장·취소, 다시 확인 표시, 쓰지 않는 실행 조건 정리 | 선택 규칙을 바꿨을 때 |
| `test_document_describe.py`, `test_document_builder.py`, `test_document_render.py`, `test_document_filename.py` | **보완 기획안 문서** 확인: 원안 문장, 선택 반영, Markdown 모양, 파일 이름 | 문서 생성을 바꿨을 때 |
| `test_llm_provider.py`, `test_llm_prompt.py`, `test_llm_guard.py`, `test_llm_catalog.py` | **AI 참고 의견** 확인: 연결·모델 목록, 요청문에 수치 없음, 답 검사, 모델 이름표 파일 | AI 기능을 바꿨을 때 |
| `test_evidence_state.py`, `test_evidence_view.py`, `test_top_badge.py` | **근거 상태와 2단계 화면 데이터**, 상단 자료 표시 확인 | 2단계 화면이나 상단 표시를 바꿨을 때 |
| `test_routes.py`, `test_evidence_routes.py`, `test_question_routes.py`, `test_opinion_routes.py`, `test_choice_routes.py`, `test_draft_routes.py` | **1~5단계 화면 주소** 확인: 단계 잠금, 화면 내용, 저장·내려받기, AI 의견·모델 선택 | 화면 흐름을 바꿨을 때 |
| `test_public_bundle.py` | **공개 저장소 검사 도구**가 실제 자료를 제대로 잡는지 확인 | 공개 저장소 검사 규칙을 바꿨을 때 |
| `test_boundaries.py` | 코드 폴더끼리 **정해진 방향으로만 불러 쓰는지** 확인 (AI 폴더가 근거 계산을 직접 못 부르게) | 폴더 구조를 바꿨을 때 |
| `fixtures/` | 시험에 쓰는 **고정 입력 파일** | [README](fixtures/README.md) |

---

## 자세한 설명 (개발자용)

### 역할 요약

기획 문서의 시험 항목(워크플로우 12장, 8-5장)을 코드로 확인한다. 실행: `uv run pytest`.
완료 기준은 "화면이 있다"가 아니라 입력·근거·선택·출력이 일치하는 것이다 (최종기획서 11장).

### 파일별 테스트 개수

개수는 매개변수화한 경우를 포함한 수집 기준이다(2026-09-17, 전체 437개). 바뀌면 `uv run pytest --collect-only -q`로 다시 센다.

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
| `test_choices.py` | 24 | `choices/` (쓰지 않는 실행 조건 정리 포함) |
| `test_document_describe.py` | 8 | `document/describe.py` |
| `test_document_builder.py` | 19 | `document/builder.py` |
| `test_document_render.py` | 11 | `document/render.py` |
| `test_document_filename.py` | 5 | `document/filename.py` |
| `test_llm_provider.py` | 14 | `llm/base.py`, `llm/local.py`(받아 둔 모델 확인·`reasoning_effort`), `PSM_LLM_TIMEOUT_S` |
| `test_llm_catalog.py` | 4 | `llm/catalog.py`, `resources/llm/models.json` |
| `test_llm_prompt.py` | 11 | `llm/prompt.py` |
| `test_llm_guard.py` | 14 | `llm/guard.py` |
| `test_evidence_state.py` | 9 | `web/evidence_state.py` |
| `test_evidence_view.py` | 32 | `web/evidence_view.py` |
| `test_top_badge.py` | 4 | 상단 자료 표시 |
| `test_routes.py` | 11 | 1단계 입력, 단계 잠금, 정적 파일 |
| `test_evidence_routes.py` | 13 | 2단계 화면 |
| `test_question_routes.py` | 10 | 3단계 화면 |
| `test_opinion_routes.py` | 23 | 3단계 AI 참고 의견 주소·모델별 캐시·모델 선택 |
| `test_choice_routes.py` | 19 | 4단계 화면, 원안 변경 후 재확인이 한 번만 붙고 풀림, 보관 안내는 이번 변경분만 |
| `test_draft_routes.py` | 22 | 5단계 화면·내려받기·PDF 버튼·인쇄 CSS, 8장에 쓰지 않는 실행 조건이 남지 않음, 저장 스크립트 409 처리 |
| `test_public_bundle.py` | 9 | `scripts/check_public_bundle.py` |
| `test_boundaries.py` | 3 | 패키지 의존 방향 (직접 import) |

### 워크플로우 12장 시험 항목 대응

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

### 파일별 핵심

#### `test_boundaries.py`

`ast`로 각 패키지의 import 문을 읽어 검사한다 (상대 import 포함).
- `plan`, `evidence`, `review`, `choices`, `document`, `llm` → `fastapi`, `starlette`, `policy_signal_map.web`·`app` 직접 import 금지
- `evidence` → `review`, `choices`, `document`, `llm`, `plan` 직접 import 금지
- `llm` → `evidence` 직접 import 금지
- 한계: 거쳐서 불러오는 import(`llm → review → evidence`)와 위 세 규칙 밖의 역방향 import(예: `review` → `choices`)는 막지 못한다. LLM 수치 차단의 실제 장치는 `to_llm_summary`·`llm/prompt.py`·`llm/guard.py`다

#### `test_public_bundle.py`

`scripts/check_public_bundle.py`의 검사 함수를 호출해 추적 파일에 실제 자료·`.env`·`private/`·원자료(csv 등) 파일이 없는지 확인한다. 임시 git 저장소에 한글 이름 파일을 넣어 이스케이프 문제 없이 검사되는지도 확인한다. git이 없는 환경에서는 건너뛴다.

### 원칙

- 실제 LLM·외부 네트워크를 호출하지 않는다. LLM은 `llm.base.FakeProvider`와 `monkeypatch`(`urllib.request.urlopen`, `web.routes.opinions.get_provider`)로 시험한다
- 실제 카드 분석 파일을 읽지 않는다. 경계 사례는 `fixtures/`의 합성 파일로 만든다
- 테스트 이름은 확인하는 기획 규칙을 문장으로 적는다 (예: `test_reference_indicator_has_no_error_message`)
