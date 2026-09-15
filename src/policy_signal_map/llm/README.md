# llm/ — AI 추가 점검 의견 (C 단계)

## 상태

**지금은 구현하지 않는다.** A(규칙 기반 흐름) 완성 후 도입한다. 도입 전 데이터 담당 합의와 최종기획서 8장·11장 수정이 필요하다 (checks.md 구현 순서, LLM 전달 자료).

## 역할

규칙 검토 결과를 바탕으로 LLM이 "AI 참고 의견"을 제시한다. 판단·수치·문서 반영은 하지 않는다.
로컬 LLM과 클라우드 API를 설정만 바꿔 쓸 수 있게 공통 연결 계층을 둔다.

## 기준

- checks.md: LLM 연결 구조(로컬/클라우드 교체), LLM 전달 자료(① 공개 시연은 합성 자료만 ② 수치 없이 규칙 결과만), LLM 출력 원칙
- 최종기획서 8장: 카드 원자료와 비공개 파생정보를 외부 LLM에 보내지 않음
- 보안관리 서약서 2항: 제공 데이터를 AI 등을 통해 유출하지 않음

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 예정 (C) | 비어 있음 |
| `base.py` | 예정 (C) | 공통 인터페이스, 설정에 따른 제공자 선택 |
| `cloud.py` | 예정 (C) | 클라우드 API 호출 (API 키는 서버 환경변수) |
| `local.py` | 예정 (C) | OpenAI 호환 로컬 서버 호출 (Ollama, LM Studio 등) |
| `prompt.py` | 예정 (C) | 규칙 결과 요약 → 요청 문장 |
| `guard.py` | 예정 (C) | 출력 검사 |
| `opinions.py` | 예정 (C) | 검사 통과 의견을 화면·선택 흐름에 넘기는 형태 |
| `retrieval.py` | 후속 | 공개 운영 문서 검색(RAG). 검수한 원문만 대상 |

## 파일별 상세

### 호출 전 필수 확인 (2근거확인화면계획 B-5)

- LLM을 부르기 전에 `web/evidence_state.get_evidence_state()`의 **`blocked`가 False이고 `ok`가 True인지** 확인한다. 아니면 호출하지 않는다
- `uv run policy-signal-map`은 시작 시 차단하지만, 배포 환경에서 `uvicorn`을 직접 실행하면 시작 차단이 빠지므로 호출 지점에서 한 번 더 막는다

### `base.py`

```
class LLMProvider(Protocol):
    name: str
    def generate(self, messages: list[Message], *, max_tokens: int, timeout_s: float) -> str

def get_provider(config) -> LLMProvider | None     PSM_LLM_PROVIDER == "none"이면 None
```

- 실패(시간 초과·연결 오류)는 예외로 올리고 화면은 "AI 의견을 불러오지 못함"만 표시. 규칙 기반 흐름은 그대로 동작해야 한다
- 호출 로그에 요청 본문을 남기지 않는다 (규칙 ID·소요 시간·성공 여부만)

### `cloud.py` / `local.py`

- 제공자·모델 이름은 설정값. 코드에 특정 모델을 고정하지 않는다 (checks.md 16번: C 단계에서 결정)
- `local.py`는 `PSM_LLM_BASE_URL`의 `/v1/chat/completions` 형식 사용
- 공개 배포에서 클라우드 호출 횟수 제한 (checks.md 17번: C 단계에서 결정)

### `prompt.py`

- 입력: `ReviewOutcome.to_llm_summary()` 목록 + 사용자 입력 중 목표·지표 용도·대상·기간 유형 (자유 입력 문장은 길이 제한)
- **넘기지 않는 것**: 금액, 비중, 증감률, 구간 수 등 모든 카드 수치, 근거 파일 원문, `observations`
- 지시: 새 수치를 만들지 말 것, 규칙 ID를 근거로 달 것, 결정하지 말고 확인할 점만 제시할 것

### `guard.py`

출력을 화면에 보내기 전 검사한다. 하나라도 걸리면 그 의견은 버린다.

| 검사 | 기준 |
|---|---|
| 숫자 포함 | 규칙 ID(R01 등)·장 번호를 제외한 숫자·퍼센트·금액 표현이 있으면 폐기 |
| 근거 표시 | 의견마다 규칙 ID 또는 문서 출처가 있어야 함 |
| 근거 존재 | 인용한 규칙 ID가 이번 검토 결과에 실제로 있어야 함 |
| 차단 기능 우회 | `blocked`·`not_reviewed` 규칙(R02 등)에 대한 추천 금지 |
| 단정 표현 | "성공할 것", "오류입니다" 등 판정 표현 폐기 |

### `opinions.py`

- `AiOpinion(text, cited_rule_ids, provider_name)`
- 화면에는 "AI 참고 의견" 라벨로 규칙 결과와 분리 표시
- 담당자가 채택하기 전에는 `choices/`·`document/`에 반영하지 않는다

### 설정 조합 차단

| 근거 자료 \ LLM | none | cloud | local |
|---|---|---|---|
| 합성 | 허용 | 허용 | 허용 |
| 실제 | 허용 | **시작 시 오류** | 데이터 담당 합의 후 |

## 의존 관계

- 가져다 쓰는 곳: `review/outcome.py`의 요약 형태, `config.py`
- **쓰면 안 되는 것: `evidence/`** (카드 수치 차단), `document/`, `choices/` 쓰기
- 이 폴더를 쓰는 곳: `web/routes/questions.py` (의견 표시)

## 테스트 (C 단계)

- `tests/test_llm_guard.py`: 숫자 포함 출력 폐기, 없는 규칙 ID 인용 폐기, blocked 규칙 추천 폐기
- `tests/test_llm_prompt.py`: 프롬프트에 근거 수치가 없음
- `tests/test_boundaries.py`: `llm/`이 `evidence/`를 import하지 않음
- 실제 LLM 호출 없이 가짜 제공자(`FakeProvider`)로 테스트한다
