# 소비 시그널 정책맵 — 서비스

기획안을 입력하면 소비데이터 근거로 확인할 점을 보여주고, 담당자가 고른 보완 방법을 반영한 보완 기획안을 만드는 서비스.

- 기준 문서: [최종기획서](../최종기획/최종기획서.md) · [개발업무 워크플로우](../최종기획/개발업무_워크플로우.md)
- 합의·진행 기록: [checks.md](./checks.md)

## 개발 환경

uv + Python 3.12, FastAPI + Jinja2.

```powershell
uv sync                                   # 의존성 설치
uv run policy-signal-map                  # 로컬 실행 → http://127.0.0.1:8000
uv run pytest                             # 테스트
uv run python scripts/build_regions.py    # 지역 선택 목록 다시 만들기
```

### 설정 (환경변수)

설정하지 않으면 합성 근거 파일과 LLM 없음으로 실행된다. 바꿀 때는 `.env.example`을 `.env`로 복사해 값을 채우고 `--env-file`로 실행한다. `.env`는 git에 올라가지 않는다.

```powershell
uv run --env-file .env policy-signal-map
```

| 환경변수 | 기본값 | 의미 |
|---|---|---|
| `PSM_EVIDENCE_PATH` | 합성 파일 `resources/evidence/review_evidence_demo_v1.json` | 분석 근거 파일. 실제 파일은 `private/`에만 둔다 |
| `PSM_LLM_PROVIDER` | `none` | AI 참고 의견. `none` / `local`(Ollama 등 로컬 LLM) / `cloud`(설정만 있고 호출 코드 없음) |
| `PSM_LLM_BASE_URL`, `PSM_LLM_MODEL`, `PSM_LLM_API_KEY` | 없음 | LLM 연결 정보 (local은 주소·모델, cloud는 모델·키 필수) |
| `PSM_LLM_MODELS` | 없음 | 담당자가 3단계에서 고를 모델 목록(쉼표 구분). 비우면 `PSM_LLM_MODEL` 하나. `PSM_LLM_MODEL`을 비우면 목록의 첫 모델이 기본 |
| `PSM_LLM_TIMEOUT_S` | `60` | LLM 응답을 기다릴 초. 모델을 바꾼 직후 첫 응답은 모델을 메모리에 올리느라 오래 걸린다 (기본값 위치: `config.py` `DEFAULT_LLM_TIMEOUT_S`) |

실제 근거 파일과 `cloud`를 함께 설정하면 `uv run policy-signal-map`은 시작하지 않는다 (uvicorn을 직접 실행하면 근거 오류 화면).

- 근거 파일은 서버가 처음 필요할 때 한 번 읽어 보관한다. **파일을 바꾸면 서버를 다시 시작한다** (`--reload`는 코드 변경에만 반응).
- 화면 상단 칩에 불러온 파일의 종류와 버전이 표시된다 (`시연용 합성 수치 · demo-001`). 파일에 문제가 있으면 `근거 파일 오류`로 바뀌고, 2단계부터 오류 화면이 나온다.
- 테스트는 `tests/conftest.py`가 `PSM_` 환경변수를 비우고 합성 파일로 고정하므로, 셸 설정과 상관없이 같은 결과가 나온다.

## 구조

순수 로직(plan·evidence·review·choices·document)과 웹 계층(web)을 나눈다. 의존 방향은 한쪽으로만 간다.

```
web → document → choices → review → evidence, plan
llm → review 결과·plan·labels·config만 사용 (evidence·web 직접 사용 금지)
```

**모든 폴더에 `README.md`가 있다.** 폴더의 역할, 만들 파일(있음/예정), 파일별 상세, 지켜야 할 원칙, 테스트를 적어 두었다. 새 파일을 만들기 전에 해당 폴더 README를 먼저 보고, 구현하면 표의 상태를 갱신한다.

| 폴더 | 역할 | 설명 |
|---|---|---|
| `src/policy_signal_map/` | 패키지 루트: app·paths·config | [README](src/policy_signal_map/README.md) |
| `  plan/` | S01 기획 입력 | [README](src/policy_signal_map/plan/README.md) |
| `  evidence/` | 분석 근거 읽기·검증, 비교 A/B 계산 | [README](src/policy_signal_map/evidence/README.md) |
| `  review/` | S02 검토 규칙 실행 | [README](src/policy_signal_map/review/README.md) |
| `  choices/` | S03 보완 선택·실행 조건·재확인 | [README](src/policy_signal_map/choices/README.md) |
| `  document/` | S04·S05 보완 기획안 Markdown | [README](src/policy_signal_map/document/README.md) |
| `  llm/` | AI 참고 의견 (로컬 LLM) | [README](src/policy_signal_map/llm/README.md) |
| `  web/` | 세션·폼·표시 형식 | [README](src/policy_signal_map/web/README.md) |
| `    routes/` | 단계별 라우트 | [README](src/policy_signal_map/web/routes/README.md) |
| `    templates/` (`steps/`, `partials/`) | Jinja2 화면 | [README](src/policy_signal_map/web/templates/README.md) |
| `    static/` (`css/`, `js/`) | 스타일·화면 반응·결과 저장 | [README](src/policy_signal_map/web/static/README.md) |
| `  resources/` (`rules/`, `evidence/`, `documents/`) | 규칙 원본·합성 근거·문서 양식 | [README](src/policy_signal_map/resources/README.md) |
| `tests/` (`fixtures/evidence/`) | pytest, 경계 사례 | [README](tests/README.md) |
| `scripts/` | 지역 목록·합성 근거 생성, 공개 자료 검사 | [README](scripts/README.md) |
| `docs/` (`screenshots/`) | 규칙 설명·대안 비교·사용법·제출 구성 | [README](docs/README.md) |
| `private/` | 실제 분석 근거 (README 외 git 제외) | [README](private/README.md) |

데이터 분석 담당의 작업은 `../Analysis/`에 둔다. 두 폴더 사이에서는 `review_evidence.json`만 오간다.

화면의 모든 수치는 시연용 합성 수치다. 실제 카드 분석 결과는 `private/`에만 둔다.

## 권리 고지

이 저장소는 「제1회 AI금융빅데이터플랫폼 소비데이터 활용 아이디어 공모전」 제출을 위한 작업물이며, 오픈소스 라이선스를 부여하지 않는다.
코드와 문서의 모든 권리는 작성자에게 있고, 사전 허락 없이 사용·복제·수정·배포할 수 없다.
공모전 수상 시 산출물의 권리는 공모전 규정에 따른다.

사용한 외부 라이브러리와 글꼴은 각자의 라이선스를 따른다 (FastAPI·Chart.js: MIT, Jinja2·uvicorn: BSD, Pretendard: SIL OFL).
