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
| `session.py` | 있음 (확장 예정) | 세션별 작업 상태 |
| `forms.py` | 있음 (확장 예정) | 폼 값 해석 |
| `labels.py` | 있음 | 입력 선택지 문구 |
| `templating.py` | 있음 | 템플릿 객체, 쿠키·리다이렉트 공통 |
| `formatters.py` | 예정 (9/17) | 숫자·방향·상태 표시 형식 |
| `dependencies.py` | 예정 (9/17) | 라우트 공통 의존성 (세션, 근거 파일, 단계 잠금) |

## 파일별 상세

### `session.py` (있음 → 확장)

- 현재 `WorkState`: `plan`, `original`, `review_restarted`
- 추가 예정 필드
  - `review_result: ReviewResult | None` — 원안 보관 시 계산해 둠
  - `choices: ChoiceSet`
  - `changed_fields: set[str]` — `plan/changes.py` 결과, `review_restarted` 대체
- `SessionStore`: 메모리 dict + 락. 서버 재시작 시 초기화
- 공개 배포 호스팅 결정(checks.md 미정)에 따라 이 파일만 교체할 수 있게 `get_or_create`·`reset` 인터페이스를 유지한다
- 오래된 세션 정리: 마지막 접근 후 2시간 지난 상태 삭제 (공개 배포 메모리 보호)

### `forms.py` (있음 → 확장)

- 현재 `parse_plan_form`
- 추가: `parse_choice_form(form, outcome) -> 입력값` — 결정, 옵션, 수정 문장, 실행 조건. 검증은 `choices/selection.py`
- 원칙: 목록에 없는 값은 버리고, 숫자로 읽지 못한 값은 원문을 남겨 오류로 보여준다

### `labels.py` (있음)

입력 선택지 문구와 단계 이름. 규칙 질문·대안 문구는 여기 두지 않는다 (`resources/rules/`).

### `formatters.py`

Jinja2 필터로 등록한다. 표시 규칙은 워크플로우 8-3장을 따른다.

| 필터 | 입력 → 출력 |
|---|---|
| `krw_eok` | 원 정수 → "2,106.18억원" 형식 (억원 변환은 화면에서, 8-1장) |
| `pct` | Fraction/float → 소수 둘째 자리 "7.45%" |
| `pp_change` | %p 변화 → "+0.13%p", 0이 아니고 절대값 0.01 미만이면 "0.01%p 미만 (증가)" |
| `growth` | 증감률 → "+10.97%", None이면 "계산 불가" |
| `direction` | up/down/flat/None → 증가/감소/변화 없음/계산 불가 |
| `calc_status` | ok/no_data/invalid_input/invalid_denominator → 계산됨/자료 없음/입력 확인 필요/분모 0 · 계산 불가 |
| `scope_label` | national/sido → "전국 참고 — 특정 지역의 진단이 아님" 등 |

- None은 절대 0이나 "0%"로 표시하지 않는다
- 방향 차이에 빨간색·경고 아이콘 클래스를 붙이지 않는다

### `dependencies.py`

- `get_session()` : 쿠키 → `(session_id, WorkState)`
- `get_evidence()` : 앱 시작 시 로드한 근거 파일 (`evidence/loader.py`), 오류면 오류 화면
- `require_step(n)` : 이전 단계 조건 확인 후 아니면 `/step/1` 리다이렉트
  - 2·3단계: `original` 있음
  - 4단계: `review_result` 있음
  - 5단계: 미선택·재확인 필요 질문이 없음 → 아니면 4단계로 돌려보내고 이유 표시

## 의존 관계

- 가져다 쓰는 곳: 모든 로직 폴더, `llm/opinions.py`(C 단계)
- 이 폴더를 쓰는 곳: `app.py`만
- 원칙: 템플릿에 넘기기 전 계산은 로직 폴더 함수로 끝내고, 템플릿은 표시만 한다

## 테스트

- `tests/test_routes.py` (있음, 단계별로 확장)
- `tests/test_formatters.py` (예정): 0.01%p 미만, None 표시, 억원 변환
