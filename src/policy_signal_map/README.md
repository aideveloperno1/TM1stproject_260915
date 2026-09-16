# src/policy_signal_map/ — 서비스 패키지 루트

## 역할

서비스 전체 코드를 담는 Python 패키지다. 루트에는 앱 생성·경로·설정처럼 모든 하위 패키지가 함께 쓰는 파일만 두고, 기능 코드는 하위 폴더에 둔다.

## 하위 폴더

| 폴더 | 역할 | 기획 대응 | 상태 |
|---|---|---|---|
| `plan/` | 기획 입력 형태·검증·지역 | S01 | 있음 |
| `evidence/` | 분석 근거 파일 읽기·검증, 비교 A/B 계산 | 워크플로우 8~9장 | 있음 |
| `review/` | 검토 규칙 실행, 질문·대안 생성 | S02, 11장 | 있음 |
| `choices/` | 보완 선택, 실행 조건, 재확인 | S03 | 있음 |
| `document/` | 보완 기획안 생성, Markdown 출력 | S04·S05 | 있음 |
| `llm/` | AI 참고 의견 (로컬 LLM만 구현, 클라우드는 확장 자리만) | `6LLM참고의견계획.md` | 있음 |
| `web/` | FastAPI 라우트, 템플릿, 정적 파일, 세션 | 화면 전체 | 있음 |
| `resources/` | 코드가 읽는 공개 자료 (규칙·합성 근거·문서 양식·프롬프트·지역) | — | 있음 |

## 의존 방향

```
web → document → choices → review → evidence, plan
llm → review 결과·plan·labels·config만 사용
```

- 화살표 반대 방향 import 금지. 예: `evidence/`가 `web/`이나 `review/`를 import하면 안 된다.
- `plan/`·`evidence/`·`review/`·`choices/`·`document/`는 FastAPI·Jinja2 화면 코드를 import하지 않는다 (단, `document/`는 Markdown 양식 렌더링에 Jinja2 라이브러리 자체는 사용 가능).
- `llm/`은 `evidence/`를 import하지 않는다. 카드 수치가 LLM으로 넘어가지 않게 하는 구조적 장치다.
- `tests/test_boundaries.py`가 검사하는 것은 세 가지다: ① 로직 패키지(`plan·evidence·review·choices·document·llm`)의 `web`·`app`·FastAPI·Starlette import ② `evidence`의 위층 import ③ `llm`의 `evidence` import. 그 밖의 역방향(예: `review` → `choices`)은 검사하지 않으므로 직접 지킨다.

## 루트에 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | `main()`: `uv run policy-signal-map`으로 uvicorn 실행 (127.0.0.1:8000, reload) |
| `app.py` | 있음 | FastAPI 생성, `/static` 마운트, `web/routes/`의 라우터 등록만 한다. 로직을 두지 않는다 |
| `paths.py` | 있음 | `PACKAGE_DIR`, `RESOURCES_DIR`, `WEB_DIR` |
| `formatting.py` | 있음 | 숫자·상태 표시 형식 (억원·%·%p·증감률·방향·상태·기간). 웹 의존 없음. 화면 필터와 5번 문서 생성이 함께 사용 |
| `labels.py` | 있음 | 목표·지표·지표 용도·자료 상태·단계·결정의 한글 라벨. 화면과 보완 기획안 문서가 함께 사용 (`document/`가 `web/`을 부를 수 없어 루트에 둠) |
| `config.py` | 있음 | 환경변수 읽기(`load_settings`), 실제 자료 + 클라우드 LLM 차단(`check_llm_data_combination`). 아래 표 참고 |
| `.env.example` → 저장소 루트 | 있음 | `config.py` 항목 예시. 실제 `.env`는 git 제외, `uv run --env-file .env`로 사용 |

### `config.py` 항목

| 환경변수 | 기본값 | 의미 |
|---|---|---|
| `PSM_EVIDENCE_PATH` | `resources/evidence/review_evidence_demo_v1.json` | 읽을 분석 근거 파일. 실제 파일은 `private/`에 두고 이 값으로 지정. 바꾸면 서버 재시작 |
| `PSM_LLM_PROVIDER` | `none` | `none` / `local` / `cloud`(설정 검증만 있고 호출 코드 없음 — 고르면 AI 의견이 오류) |
| `PSM_LLM_BASE_URL` | 없음 | 로컬 LLM의 OpenAI 호환 주소 (예: `http://127.0.0.1:11434/v1`) |
| `PSM_LLM_MODEL` | 없음 | 모델 이름 |
| `PSM_LLM_API_KEY` | 없음 | 클라우드 API 키. `.env`에만 둔다 |
| `PSM_LLM_TIMEOUT_S` | `20` | LLM 응답을 기다릴 초. 0보다 커야 함 |

- 설정은 앱 시작 시 한 번 읽어 불변 객체(dataclass frozen)로 둔다. 빈 문자열은 설정하지 않은 것으로 본다.
- cloud는 모델·키, local은 주소·모델이 없으면 `SettingsError`.
- 실제 근거 파일 + `PSM_LLM_PROVIDER=cloud` 조합이면 오류. 실제 자료 여부는 `data_kind` 표시뿐 아니라 `private/` 경로·`_real_` 이름으로도 판단한다 (`evidence/loader.py`의 `is_real_evidence`). `uv run policy-signal-map`(`__init__.main`)은 이 조합이면 서버를 켜지 않고, `uvicorn`을 직접 실행하면 `web/evidence_state.py`가 blocked 상태로 두어 2~5단계가 오류 화면이 된다.

## 지켜야 할 원칙

- 새 기능은 해당 폴더 README의 "만들 파일" 표를 먼저 갱신하고 구현한다.
- 선택지 라벨은 루트 `labels.py`, 규칙 문구·대안·문서 문장은 `resources/rules/`, 보완 기획안 양식은 `resources/documents/`, AI 요청 문장은 `resources/prompts/`에 둔다. 코드 여러 곳에 같은 문구를 적지 않는다.
