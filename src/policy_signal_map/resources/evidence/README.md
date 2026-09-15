# resources/evidence/ — 합성 분석 근거 파일 (공개용)

## 역할

서비스가 기본으로 읽는 **시연용 합성** 분석 근거 파일. 공개 저장소·공개 배포·화면 개발에 사용한다.
형식은 실제 파일과 똑같이 워크플로우 9-3장을 따르므로, 실제 파일로 바꿔도 코드는 그대로 동작한다.

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `review_evidence_demo_v1.json` | 있음 | 화면 시연용 합성 근거. `uv run python scripts/build_demo_evidence.py`로 생성, 손으로 고치지 않음 |

## `review_evidence_demo_v1.json` 내용

- `schema_version`: `"2.0"`, `dataset_version`: `"demo-001"`, 설정 기본값(`PSM_EVIDENCE_PATH` 미설정)이 이 파일
- 레코드 `DEMO-R07-NATIONAL` — 전국, 2026-01~06, 6개월 모두 `ok`
  - 인접 5구간: 비교 A **반대 2개**(01→02, 02→03), **같음 3개** — 반대 방향만 모은 자료가 아님
  - 04→05는 비중 변화 +0.0022%p (0.01%p 미만 표시 규칙 확인용)
  - 기간 합산 비중 8.3778% (월 비중 평균 8.3760%과 다름)
  - applicability: R07 `allowed` / R06 `blocked` / R02 `needs_review`
- 레코드 `DEMO-R07-SIDO-HOLD` — 가상 시도 `DEMO-SIDO-A`
  - 03월 `no_data`, 05월 `invalid_denominator` → 비교 가능 1개, 보류 4개
  - applicability: R07 `needs_review` / R06·R02 `blocked`
  - 2단계 "자료가 부족한 경우 보기" 화면용
- 월별 수치 표: [1근거계산계층계획.md 9장](../../../../1근거계산계층계획.md#9-1-5-합성-근거-파일)
- `tests/test_demo_evidence.py`가 생성 스크립트와의 일치, 구간 구성, 가상 규모를 검사한다

## 원칙

- **실제 카드 분석 수치를 쓰지 않는다.** 최종기획서 4-2장 표의 금액·비중을 그대로 또는 비슷하게 옮기지 않는다. 가상 규모(외국인 800, 전체 10,000 단위 등)를 쓴다
- 모든 레코드 `data_kind: "synthetic"`, `dataset_version`은 `demo-`로 시작
- 손으로 비중을 적지 않는다. 스크립트가 정수 금액에서 계산한다
- 테스트 전용 경계 사례는 여기가 아니라 `tests/fixtures/evidence/`에 둔다
- 실제 파일은 `private/`에만 둔다
