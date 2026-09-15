# tests/fixtures/evidence/ — 근거 파일 경계 사례

## 역할

`evidence/` 로더·비교 계산이 기획 문서의 모든 예외를 올바르게 처리하는지 확인하는 합성 JSON 모음.
각 파일은 워크플로우 9-3장 형식을 따르고, 확인할 상황만 담도록 2~3개월로 작게 만든다.

## 만들 파일 — 정상 파일, 비교 계산 (워크플로우 8-5장)

| 파일 | 상황 | 기대 결과 |
|---|---|---|
| `amount_up_share_down.json` | 외국인 금액 증가, 전체 금액이 더 빠르게 증가 | 비교 A opposite=True (금액 up, 비중 down) |
| `amount_down_share_up.json` | 외국인 금액 감소, 전체 금액이 더 빠르게 감소 | 비교 A opposite=True (금액 down, 비중 up) |
| `same_direction.json` | 외국인 금액·비중 모두 증가 | opposite=False, 반대 문구 없음 |
| `flat_change.json` | 금액 또는 비중 변화 0 | 해당 방향 flat, opposite=False |
| `prev_foreign_zero.json` | 이전 달 외국인 금액 0 | 증감률 None, 금액 차이 방향 up |
| `missing_month.json` | 3월이 `no_data` (금액 null) | 2→3, 3→4 비교 skipped, 2→4를 잇지 않음 |
| `tiny_change.json` | 비중 변화 절대값 0.005%p | 방향 유지, 표시 "0.01%p 미만" |
| `known_only_differs.json` | 전체 분모 비중은 down, 미상 제외 비중은 up | 비교 B opposite=True, 비교 A와 별개 |
| `large_amounts.json` | 수조 원 단위 금액 | 교차곱 부호가 float 반올림과 달라지는 경우도 정확 |
| `unknown_equals_total.json` | U = T (미상 제외 분모 0) | 미상 제외 비중 None, 전체 분모 비중은 계산 |

## 만들 파일 — 오류 파일, 로더 검증 (워크플로우 9장)

| 파일 | 상황 | 기대 결과 |
|---|---|---|
| `invalid_status_value.json` | `calculation_status: "okay"` | EvidenceError (목록에 없는 상태값) |
| `invalid_applicability.json` | applicability status `"maybe"` | EvidenceError |
| `missing_reason.json` | applicability `reason` 빈 문자열 | EvidenceError |
| `relation_broken.json` | ok 월에 F + U > T | EvidenceError |
| `negative_amount.json` | 금액 음수 | EvidenceError |
| `decimal_amount.json` | 금액 `800.5` | EvidenceError (원 단위 정수) |
| `no_data_with_zero.json` | no_data 월에 금액 0 | EvidenceError (자료 없음을 0으로 표시) |
| `month_omitted.json` | 기간 안 월이 months에서 빠짐 | EvidenceError (생략 금지) |
| `schema_version_unsupported.json` | `schema_version: "1.0"` | EvidenceError, 버전 확인 안내 |
| `mixed_data_kind.json` | synthetic·real 레코드 혼합 (real은 가짜 수치) | EvidenceError |
| `denominator_zero.json` | `invalid_denominator` 월, T = 0 | 로드 성공, 비중 None, 해당 구간 skipped |
| `national_region_key_wrong.json` | national인데 region_key가 ALL이 아님 | EvidenceError |

## 원칙

- `mixed_data_kind.json`의 `real` 레코드도 수치는 가짜로 만든다. 이름표만 real이다
  → `scripts/check_public_bundle.py`는 `tests/fixtures/` 아래 이 파일을 예외 목록으로 허용한다 (파일 경로를 명시적으로 등록)
- 기대 결과는 테스트 코드에 적고, JSON에는 사례 설명을 `"_case"` 필드로 한 줄 남긴다 (로더는 `_`로 시작하는 최상위 필드를 무시)
