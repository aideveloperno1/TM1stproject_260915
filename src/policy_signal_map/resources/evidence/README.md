# resources/evidence/ — 합성 분석 근거 파일 (공개용)

## 역할

서비스가 기본으로 읽는 **시연용 합성** 분석 근거 파일. 공개 저장소·공개 배포·화면 개발에 사용한다.
형식은 실제 파일과 똑같이 워크플로우 9-3장을 따르므로, 실제 파일로 바꿔도 코드는 그대로 동작한다.

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `review_evidence_demo_v1.json` | 예정 (9/16) | 화면 시연용 합성 근거. `scripts/build_demo_evidence.py`로 생성 |

## `review_evidence_demo_v1.json` 내용

- `schema_version`: `"2.0"`, `dataset_version`: `"demo-001"`
- 레코드 `DEMO-R07-NATIONAL`
  - `data_kind: "synthetic"`, `geographic_scope: "national"`, `region_key: "ALL"`, 기간 2026-01~2026-06
  - 6개월 모두 `ok`
  - 인접 5구간 중 비교 A 반대 방향과 같은 방향이 섞이게 구성 (반대 방향만으로 만들지 않음)
  - 0.01%p 미만 변화 구간 1개 포함 (표시 규칙 확인용)
  - applicability: R07 `allowed`(합성 전국 예시로만 사용) / R06 `blocked`(업종·월 보정 자료 없음) / R02 `needs_review`(지역 기준과 업종 후보 자료 미확인)
  - limitations: "합성 자료", "전국 참고 예시이며 선택 지역 진단이 아님", "미상 제외 비중을 정답으로 해석하지 않음"
- 레코드 `DEMO-R07-SIDO-HOLD`
  - `geographic_scope: "sido"`, 가상 시도 키, `no_data` 월과 `invalid_denominator` 월 포함
  - applicability R07 `needs_review`
  - 2단계 "자료가 부족한 경우 보기" 화면용

## 원칙

- **실제 카드 분석 수치를 쓰지 않는다.** 최종기획서 4-2장 표의 금액·비중을 그대로 또는 비슷하게 옮기지 않는다. 가상 규모(외국인 800, 전체 10,000 단위 등)를 쓴다
- 모든 레코드 `data_kind: "synthetic"`, `dataset_version`은 `demo-`로 시작
- 손으로 비중을 적지 않는다. 스크립트가 정수 금액에서 계산한다
- 테스트 전용 경계 사례는 여기가 아니라 `tests/fixtures/evidence/`에 둔다
- 실제 파일은 `private/`에만 둔다
