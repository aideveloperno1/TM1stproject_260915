# src/policy_signal_map/ — 서비스 패키지 루트

## 역할

서비스 전체 코드를 담는 Python 패키지다. 루트에는 앱 생성·경로·설정처럼 모든 하위 패키지가 함께 쓰는 파일만 두고, 기능 코드는 하위 폴더에 둔다.

## 하위 폴더

| 폴더 | 역할 | 기획 대응 | 상태 |
|---|---|---|---|
| `plan/` | 기획 입력 형태·검증·지역 | S01 | 있음 |
| `evidence/` | 분석 근거 파일 읽기·검증, 비교 A/B 계산 | 워크플로우 8~9장 | 예정 |
| `review/` | 검토 규칙 실행, 질문·대안 생성 | S02, 11장 | 일부 (규칙 목록) |
| `choices/` | 보완 선택, 실행 조건, 재확인 | S03 | 예정 |
| `document/` | 보완 기획안 생성, Markdown 출력 | S04·S05 | 예정 |
| `llm/` | 로컬/클라우드 LLM 추가 점검 의견 | C 단계 | 예정 |
| `web/` | FastAPI 라우트, 템플릿, 정적 파일, 세션 | 화면 전체 | 있음 |
| `resources/` | 코드가 읽는 공개 자료 (규칙·합성 근거·양식·지역) | — | 일부 |

## 의존 방향

```
web → document → choices → review → evidence, plan
llm → review 결과만 사용
```

- 화살표 반대 방향 import 금지. 예: `evidence/`가 `web/`이나 `review/`를 import하면 안 된다.
- `plan/`·`evidence/`·`review/`·`choices/`·`document/`는 FastAPI·Jinja2 화면 코드를 import하지 않는다 (단, `document/`는 Markdown 양식 렌더링에 Jinja2 라이브러리 자체는 사용 가능).
- `llm/`은 `evidence/`를 import하지 않는다. 카드 수치가 LLM으로 넘어가지 않게 하는 구조적 장치다.
- `tests/test_boundaries.py`(예정)가 이 규칙을 검사한다.

## 루트에 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | `main()`: `uv run policy-signal-map`으로 uvicorn 실행 (127.0.0.1:8000, reload) |
| `app.py` | 있음 | FastAPI 생성, `/static` 마운트, `web/routes/`의 라우터 등록만 한다. 로직을 두지 않는다 |
| `paths.py` | 있음 | `PACKAGE_DIR`, `RESOURCES_DIR`, `WEB_DIR` |
| `formatting.py` | 있음 | 숫자·상태 표시 형식 (억원·%·%p·증감률·방향·상태·기간). 웹 의존 없음. 화면 필터와 5번 문서 생성이 함께 사용 |
| `config.py` | 있음 | 환경변수 읽기(`load_settings`), 실제 자료 + 클라우드 LLM 차단(`check_llm_data_combination`). 아래 표 참고 |
| `.env.example` → 저장소 루트 | 있음 | `config.py` 항목 예시. 실제 `.env`는 git 제외, `uv run --env-file .env`로 사용 |

### `config.py` 항목

| 환경변수 | 기본값 | 의미 |
|---|---|---|
| `PSM_EVIDENCE_PATH` | `resources/evidence/review_evidence_demo_v1.json` | 읽을 분석 근거 파일. 실제 파일 사용 여부는 개발 담당이 추후 결정 |
| `PSM_LLM_PROVIDER` | `none` | `none` / `cloud` / `local` (C 단계) |
| `PSM_LLM_BASE_URL` | 없음 | 로컬 LLM의 OpenAI 호환 주소 (C 단계) |
| `PSM_LLM_MODEL` | 없음 | 모델 이름 (C 단계) |
| `PSM_LLM_API_KEY` | 없음 | 클라우드 API 키. `.env`에만 둔다 (C 단계) |

- 설정은 앱 시작 시 한 번 읽어 불변 객체(dataclass frozen)로 둔다. 빈 문자열은 설정하지 않은 것으로 본다.
- cloud는 모델·키, local은 주소·모델이 없으면 `SettingsError`.
- 실제 근거 파일 + `PSM_LLM_PROVIDER=cloud` 조합이면 오류. 실제 자료 여부는 `data_kind` 표시뿐 아니라 `private/` 경로·`_real_` 이름으로도 판단한다 (`evidence/loader.py`의 `is_real_evidence`). 앱 시작 시 연결은 2-1.

## 지켜야 할 원칙

- 새 기능은 해당 폴더 README의 "만들 파일" 표를 먼저 갱신하고 구현한다.
- 화면 문구는 `web/labels.py`, 규칙 문구·대안은 `resources/rules/`에 둔다. 코드 여러 곳에 같은 문구를 적지 않는다.
