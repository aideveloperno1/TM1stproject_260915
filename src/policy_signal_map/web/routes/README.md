# web/routes/ — 단계별 라우트

## 역할

화면 단계마다 라우트 파일 하나를 둔다. 라우트는 요청 해석 → 로직 호출 → 세션 갱신 → 템플릿 렌더링만 한다.

## 만들 파일

| 파일 | 상태 | 경로 | 템플릿 |
|---|---|---|---|
| `__init__.py` | 있음 | — | — |
| `input.py` | 있음 | `GET /`, `GET·POST /step/1`, `POST /reset` | `steps/input.html` |
| `steps.py` | 있음 (임시) | `GET /step/{2~5}` | `steps/placeholder.html` |
| `evidence.py` | 예정 (9/16~17) | `GET /step/2` | `steps/evidence.html` |
| `questions.py` | 예정 (9/17) | `GET /step/3` | `steps/questions.html` |
| `choices.py` | 예정 (9/17) | `GET·POST /step/4`, `POST /step/4/cancel` | `steps/choices.html` |
| `draft.py` | 예정 (9/18) | `GET /step/5`, `GET /step/5/document`, `GET /step/5/download`, `GET /step/5/request` | `steps/draft.html`, `steps/document.html`, `steps/request.html` |

단계를 구현할 때마다 `steps.py`에서 해당 번호를 빼고, 5단계까지 끝나면 `steps.py`와 `placeholder.html`을 삭제한다. `app.py`에 새 라우터를 등록한다.

## 파일별 상세

### `input.py` (있음)

- `POST /step/1`의 `action`: `sample`(예시 채우기) / `clear`(모두 지우기) / `submit`(검토 시작)
- 검증 실패: 422와 오류 표시. 성공: 원안 보관 → `/step/2`
- 확장 예정: 원안 보관 시 `plan/changes.py`로 변경 필드 계산 → `choices/recheck.py` 호출, `review/engine.py` 실행 결과를 세션에 저장

### `evidence.py` — 2단계 근거 확인

- 세션의 원안 지역에 맞는 근거 레코드 조회. 지역 레코드가 없으면 전국 레코드를 **전국 참고로 표시**해 보여준다 (대체 사실을 숨기지 않음)
- 템플릿에 넘길 것
  - 상단 표시: 전국 참고/시도 범위, 기간, `dataset_version`, 합성/실제
  - 월별 표 6행: 금액, 전체 분모 비중, 미상 비중, 미상 제외 비중, 상태
  - 인접 구간 5개: 비교 A 결과, 비교 B 결과(보조), 보류 사유
  - 요약 문장용 숫자: `evidence/summary.py`의 구간 수
  - 차트 데이터 JSON (금액 막대, 비중 선 — 전체/미상 제외 전환)
  - 계산 방법·해석 한계 (`limitations`)
  - 보류 사례 보기: `no_data`·`invalid_denominator`가 있는 레코드
- 근거 파일 로드 오류면 오류 내용과 "데이터 담당에게 확인" 안내

### `questions.py` — 3단계 검토 질문

- `review_result.outcomes`를 kind별로 표시: 질문 / 안내 / 추가 확정 필요 / 보류
- 오른쪽 패널: 검토하지 않은 항목 (R06 분석 예시, R02 향후 기능)
- 각 질문의 근거 ID 칩 → 5단계 근거 추적 또는 2단계로 이동
- C 단계: `llm/opinions.py` 결과를 "AI 참고 의견"으로 분리 표시

### `choices.py` — 4단계 보완 선택

- 질문마다 원안 유지 / 대안 A~D(규칙 JSON 정의) / 수정 / 보류
- 대안 카드: 바뀌는 곳, 필요 자료, 운영 부담
- 옵션 A 선택 시 실행 조건 입력칸: 수집자료, 확보 여부, 담당자, 주기 (빈 값 → "추가 확정 필요" 안내)
- `POST /step/4`: `web/forms.py` → `choices/selection.py` 검증 → 세션 저장
- `POST /step/4/cancel`: 해당 질문 선택 취소
- `needs_recheck` 선택은 상단에 모아 "원안 변경으로 재확인 필요" 표시
- [보완 기획안 만들기]: 미선택·재확인 필요가 남아 있으면 막고 목록 표시

### `draft.py` — 5단계 보완 기획안

- `GET /step/5`: 원안 ↔ 보완안 비교 화면 (변경 N건 · 추가 확정 필요 N건 · 원안 유지 N개), 근거 추적 패널
- `GET /step/5/document`: 전체 문서 보기 (Markdown을 HTML로 보기 좋게, 또는 `<pre>`)
- `GET /step/5/download`: `document/render.py` 결과를 `text/markdown; charset=utf-8`로 응답, `Content-Disposition`에 `document/filename.py` 파일명 (RFC 5987 `filename*=UTF-8''` 인코딩으로 한글 파일명)
  - 화면의 [결과 저장]은 `static/js/save.js`가 이 주소를 받아 저장 위치 선택 창을 연다
- `GET /step/5/request`: 옵션 D 선택 시 정밀 분석 요청서 초안. 선택 안 했으면 404 대신 안내
- 문서 생성 차단 상태면 4단계로 리다이렉트

## 공통 원칙

- 세션·근거 파일은 `web/dependencies.py`로 받는다
- 쿠키: `httponly`, `samesite=lax` (배포 시 `secure` 추가)
- 상태를 바꾸는 요청은 POST만 사용하고 처리 후 303 리다이렉트 (새로고침 시 재제출 방지)

## 테스트

`tests/test_routes.py`에 단계별로 추가
- 단계 잠금 (원안 없이 2~5단계 → 1단계로)
- 2단계에 "전국 참고"와 "시연용 합성" 표시
- 4단계 미선택 상태에서 5단계 차단
- `/step/5/download` 응답 헤더의 한글 파일명과 본문 일치
