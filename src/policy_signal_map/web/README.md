# web/ — 화면 계층 (FastAPI + Jinja2)

## 역할

HTTP 요청을 받아 하위 로직(`plan/`·`evidence/`·`review/`·`choices/`·`document/`)을 호출하고 HTML을 돌려준다.
작업 상태 보관, 폼 해석, 화면 문구·숫자 표시 형식을 담당한다. **계산·규칙 판단을 여기서 하지 않는다.**

## 기준 문서

- 최종기획서 3장 사용자 흐름, 6장 제공할 화면
- checks.md: 시안 5단계, 시안 디자인, 서버 메모리 세션, [결과 저장] 저장 위치 선택
- 참고 시안: `../../../../기획서 보완 서비스 랜딩페이지/정책맵 워크스페이스.dc.html`

## 하위 폴더

| 폴더 | 내용 |
|---|---|
| `routes/` | 단계별 라우트 |
| `templates/` | Jinja2 HTML |
| `static/` | CSS·JS |

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | 비어 있음 |
| `session.py` | 있음 | 세션별 작업 상태, AI 의견 캐시 |
| `forms.py` | 있음 | 폼 값 해석 (기획 입력, 보완 선택) |
| ~~`labels.py`~~ | 루트 `labels.py`로 이동 | 보완 기획안 문서도 쓰도록 웹 의존 없는 위치에 둠 |
| `templating.py` | 있음 | 템플릿 객체, 표시 형식 필터 등록, **`render()`**(모든 화면 공통), 쿠키·리다이렉트 |
| `evidence_state.py` | 있음 | 근거 파일 상태를 한 번 읽어 보관 (`get_evidence_state`), 상단 칩 문구, 실제 자료 + 클라우드 차단 |
| `dependencies.py` | 있음 | 라우트 공통 의존성: `session_dep`, `evidence_state_dep` |
| `evidence_view.py` | 있음 | 2단계 화면용 데이터: 레코드 선택(전국), 금액 단위, 적용 상태별 표시 여부, 요약 문장, 차트 데이터(JSON 형식만), 보류 사례(합성 파일만) |
| ~~`formatters.py`~~ | 루트 `formatting.py`로 이동 | 5번 문서 생성도 쓰도록 웹 의존 없는 위치에 둠 |

## 파일별 상세

### `session.py` (있음)

- `WorkState`: `plan`, `original`, `changed_fields`(`plan/changes.py` 결과), `choices`(`ChoiceSet`), `opinions`·`opinions_for`(AI 의견과 그것을 만든 원안 스냅샷), `review_restarted`(= 바뀐 항목이 있는지)
- `start_review()`: 원안 보관, 바뀐 항목 계산, AI 의견 캐시 비움. `cached_opinions()`·`remember_opinions()`: 원안이 같을 때만 캐시 사용
- 쿠키 `psm_session` (httponly, samesite=lax). 여러 프로세스로 띄우면 세션이 공유되지 않는다
- 검토 결과는 저장하지 않고 요청마다 다시 계산한다 (같은 입력이면 같은 결과)
- `SessionStore`: 메모리 dict + 락. 서버 재시작 시 초기화
- 공개 배포 호스팅 결정(checks.md 미정)에 따라 이 파일만 교체할 수 있게 `get_or_create`·`reset` 인터페이스를 유지한다
- 오래된 세션 정리: **아직 구현하지 않았다.** 공개 배포를 하게 되면 필요하다 (`작업진행.md` 7-2)

### `forms.py` (있음)

- `parse_plan_form(single, multi) -> PlanInput`
- `parse_choice_form(form) -> (단일 값 dict, 수집 자료 목록)` — 수집 자료는 줄바꿈·쉼표로 나눈다. 검증은 `choices/selection.py`
- 원칙: 목록에 없는 값은 버리고, 숫자로 읽지 못한 값은 원문을 남겨 오류로 보여준다

### 라벨 (`../labels.py`)

입력 선택지 문구·단계 이름·문서용 결정 표기. 규칙 질문·대안 문구는 여기 두지 않는다 (`resources/rules/`).

### 표시 형식 필터 (`../formatting.py`)

`templating.py`가 `formatting.FILTERS`를 Jinja2 필터로 등록한다. 규칙은 워크플로우 8-3장, 상세는 [2근거확인화면계획.md 5-1](../../../2근거확인화면계획.md#5-1-policy_signal_mapformattingpy-b-3).

| 필터 | 출력 예 |
|---|---|
| `amount(value, unit)` | `2,106.18억원`, `820원`, `0.01억원 미만`, None → `자료 없음` |
| `pct` | `8.40%`, `0.01% 미만`, None → `계산 불가` |
| `growth` | `+8.86%`, `0.01% 미만 (증가)`, None → `계산 불가` |
| `pp_change` | `+0.20%p`, `0.01%p 미만 (증가)`, `0.00%p` |
| `direction`, `comparison`, `calc_status` | `증가`, `방향 다름`, `분모 0 · 계산 불가` |
| `month_label`, `pair_label`, `period_label` | `4월`, `1→2월`, `2026년 1~6월` |

- 반올림은 Fraction → Decimal 사사오입. None은 절대 0으로 표시하지 않는다
- 방향 차이에 빨간색·경고 아이콘 클래스를 붙이지 않는다

### `evidence_state.py`

- `load_evidence_state(environ)`: 설정 → 근거 파일 로드 → 실제 자료 판단 → 클라우드 조합 차단. 예외를 던지지 않고 `EvidenceState(errors, blocked, …)`로 담는다
- `get_evidence_state()`: 프로세스에서 한 번만 읽는다. 근거 파일을 바꾸면 서버 재시작
- 화면용 오류 문구에는 서버 전체 경로 대신 파일 이름만 넣고, 원래 문구는 서버 로그에 남긴다
- `badge`: `시연용 합성 수치 · demo-001` / `실제 분석 자료 · {버전} · 내부 검증용` / `근거 파일 오류`

### `templating.render()`

모든 화면은 `render(request, template, context, step=, session_id=, state=, evidence=)`로 그린다. `base.html`이 쓰는 `step`·`state`·`evidence`를 빠뜨리면 페이지 전체가 템플릿 오류(500)가 나기 때문이다.

### `dependencies.py`

- `session_dep` : 쿠키 → `(session_id, WorkState)`
- `evidence_state_dep` : `get_evidence_state()`. 테스트는 `app.dependency_overrides`로 교체 (`tests/conftest.py`)
- 단계 잠금은 각 라우트에서 명시적으로 확인한다
  - 2~5단계: `original` 있음 (없으면 `/step/1`), 근거 파일 정상 (아니면 `error.html` 503)
  - 5단계: 고르지 않은 질문·재확인 필요가 없음 → 아니면 `/step/4`로 (이유는 4단계 화면에 표시)

## 의존 관계

- 가져다 쓰는 곳: 모든 로직 폴더, `llm/` (`routes/opinions.py`, `session.py`)
- 이 폴더를 쓰는 곳: `app.py`만
- 원칙: 템플릿에 넘기기 전 계산은 로직 폴더 함수로 끝내고, 템플릿은 표시만 한다

## 테스트

- 화면: `test_routes.py`(1단계), `test_evidence_routes.py`, `test_question_routes.py`, `test_opinion_routes.py`, `test_choice_routes.py`, `test_draft_routes.py`
- 표시·상태: `test_formatters.py`(0.01 미만, None 표시, 억원 변환), `test_evidence_view.py`, `test_evidence_state.py`, `test_top_badge.py`
