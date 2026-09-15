# tests/fixtures/evidence/ — 근거 파일 경계 사례

## 역할

`evidence/` 로더·비교 계산이 기획 문서의 모든 예외를 올바르게 처리하는지 확인하는 합성 JSON 22개.
각 파일은 워크플로우 9-3장 형식을 따르고, 확인할 상황만 담도록 2~3개월로 작게 만든다.

## 만드는 방법

**손으로 고치지 않는다.** `scripts/build_fixtures.py`로 생성해 커밋한다.

```powershell
uv run python scripts/build_fixtures.py
```

- 비중은 정수 금액에서 계산해 넣는다 (`scripts/_evidence_builder.py`)
- 오류 사례는 정상 사례 `amount_up_share_down`을 만든 뒤 **한 곳만 바꿔** 생성한다 → 테스트가 오류 문구 정확히 1개를 확인
- `tests/test_evidence_loader.py::test_fixtures_match_generator`가 스크립트 결과와 커밋된 파일이 같은지 검사한다. 스크립트만 고치고 재생성을 잊으면 테스트가 실패한다
- 모든 레코드 ID `FX-01`, `dataset_version: fixture-{파일이름}`
- 사례별 월 수치와 기대 결과(방향·비교 A/B·증감률)는 [1근거계산계층계획.md 6장](../../../1근거계산계층계획.md#6-1-2-경계-사례-22개)

## 정상 파일 11개 — 로드 성공

| 파일 | 상황 | 기대 결과 |
|---|---|---|
| `amount_up_share_down.json` | 외국인 금액 증가, 전체 금액이 더 빠르게 증가 | 비교 A 반대 (금액 up, 비중 down) |
| `amount_down_share_up.json` | 외국인 금액 감소, 전체 금액이 더 빠르게 감소 | 비교 A 반대 (금액 down, 비중 up) |
| `same_direction.json` | 외국인 금액·비중 모두 증가 | 반대 아님 |
| `flat_change.json` | 01→02 금액 변화 0, 02→03 비중 변화 0 | flat이 있으면 반대 아님 |
| `prev_foreign_zero.json` | 이전 달 외국인 금액 0 (관측 행 없음 경고) | 증감률 None, 금액 차이 +500 |
| `missing_month.json` | 02월 `no_data` (금액 null) | 01→02, 02→03 보류, 01→03을 잇지 않음 |
| `tiny_change.json` | 비중 변화 −0.0004%p | 방향 유지(비교 A 반대), 표시는 "0.01%p 미만" |
| `known_only_differs.json` | 전체 분모 비중 down, 미상 제외 비중 up | 비교 B만 반대 |
| `large_amounts.json` | 1,000조 원 규모 | 소수점 계산은 flat, 정수 교차곱은 up |
| `unknown_equals_total.json` | 02월 U = T (미상 제외 분모 0) | 미상 제외 비중 null, 비교 B 계산 불가 |
| `denominator_zero.json` | 02월 `invalid_denominator`, T = 0 | 로드 성공, 01→02 보류 |

## 오류 파일 11개 — 로드 실패 (오류 문구 1개)

| 파일 | 바꾼 곳 | 기대 오류 |
|---|---|---|
| `invalid_status_value.json` | 02월 `calculation_status: "okay"` | 허용되지 않는 값 |
| `invalid_applicability.json` | R07 status `"maybe"` | 허용되지 않는 값 |
| `missing_reason.json` | R06 `reason: ""` | 사유(reason)가 비어 있습니다 |
| `relation_broken.json` | 02월 `unknown_amount` → F + U > T | 외국인+미상 금액이 전체 금액보다 큽니다 |
| `negative_amount.json` | 01월 외국인 금액 음수 | 0 이상이어야 합니다 (값 출력 안 함) |
| `decimal_amount.json` | 01월 외국인 금액 소수 | 원 단위 정수여야 합니다 (받은 형식: 소수) |
| `no_data_with_zero.json` | 02월 `no_data`, 비중·건수 null, **F·T·U만 0** | 자료 없음 월의 금액은 null이어야 합니다 |
| `month_omitted.json` | 기간 끝 03월, 03월 항목 없음 | 2026-03 월이 없습니다 |
| `schema_version_unsupported.json` | `schema_version: "1.0"` | 지원하지 않는 형식 버전, 데이터 담당 확인 안내 |
| `mixed_data_kind.json` | 두 번째 레코드 `data_kind: "real"` (수치는 가짜) | 합성 자료와 실제 자료가 섞여 있습니다 |
| `national_region_key_wrong.json` | 전국인데 `region_key: "11"` | 전국 범위의 region_key는 "ALL" |

## 원칙

- 모든 수치는 가상 규모다. 실제 카드 분석 수치를 쓰지 않는다
- `mixed_data_kind.json`의 `real` 레코드도 수치는 가짜이며 이름표만 real이다 → `scripts/check_public_bundle.py`는 이 파일 경로를 예외 목록에 명시해 허용한다
- JSON의 `_case` 필드에 사례 설명을 한 줄 남긴다 (로더는 `_`로 시작하는 최상위 필드를 무시)
- 새 사례를 추가하면 `build_fixtures.py`, `tests/evidence_helpers.py`의 목록, 이 README를 함께 고친다 (`test_every_fixture_file_is_covered_by_a_test`가 누락을 잡는다)
