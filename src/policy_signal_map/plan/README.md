# plan/ — 기획 입력 (S01)

## 역할

사용자가 입력한 기획 원안의 데이터 형태, 필수·선택 항목 검증, 지역 목록을 담당한다. 웹 폼과 무관한 순수 로직이다.

## 기준 문서

- 워크플로우 3장 "입력폼 최소 항목", S01 입력과 원안 보관
- 최종기획서 3장 (첫 버전은 항목별 입력폼), 7장 (자료가 없으면 0으로 대체하지 않음)
- checks.md 입력폼 결정 (필수 7개, 목표·지표 복수 선택, 전국/시도/시군구, 예산 미정·0원 구분)

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | 비어 있음 |
| `models.py` | 있음 | 입력 데이터 형태와 예시 기획 |
| `validation.py` | 있음 | 필수 항목 오류, 추가 확정 필요 항목 |
| `regions.py` | 있음 | 시도·시군구 목록 조회, 지역 표시 이름 |
| `changes.py` | 예정 (9/17~18) | 원안 변경 비교 → 재확인이 필요한 항목 판단 |

## 파일별 상세

### `models.py` (있음)

- 선택지 열거형: `Goal`(금액 확대·비중 확대·참여 상점 이용 확대·기타), `Metric`(외국인 결제 비중·금액·쿠폰 사용·정산 실적·기타), `IndicatorUse`(직접 평가·참고 현황·아직 모름), `DataStatus`(확보됨·협의 중·미정), `RegionLevel`(전국·시도·시군구), `BudgetStatus`(미입력·미정·금액)
- `Region`: 범위와 시도·시군구 코드
- `Budget`: 상태, 원 단위 정수 금액, 숫자로 읽지 못한 원문(`raw`)
- `PlanInput`: 입력 전체
- `sample_plan()`: 최종기획서 4-1장 첫 시험 기획. 지역은 공개 시연용 예시(강원 강릉시)
- 추가 예정: 없음. 필드를 늘리면 `web/forms.py`, `web/templates/steps/input.html`, `validation.py`, 테스트를 함께 고친다

### `validation.py` (있음)

- `validate_plan(plan) -> ValidationResult(errors, pending)`
- errors 키: `name, goals, goal_other, target, region, period, budget, metrics, metric_other, indicator_use`
- pending: 비어 있는 선택 항목 → 보완 기획안 "추가 확정 필요"로 넘어갈 이름 (예산 미입력/미정, 쿠폰 사용처, 자료 확보 상태, 성과 자료 확보)
- 검증: 목록에 없는 지역 코드, 날짜 형식, 종료일 < 시작일, 예산 비정수
- 추정·보정하지 않는다. 예: 잘못된 예산 글자를 0으로 바꾸지 않는다

### `regions.py` (있음)

- `load_regions()`, `sido_list()`, `find_sido(code)`, `is_known_region(region)`, `region_label(region)`
- 자료: `resources/regions.json` (`scripts/build_regions.py`로 생성)
- 이 목록은 **입력 선택용**이다. 카드 근거의 지역 범위(`region_key`)와 같은 뜻이 아니다. 근거의 지역 적용 여부는 `evidence/`·`review/`가 판단한다

### `changes.py` (예정)

원안을 바꿔 다시 제출했을 때 이후 단계 선택 중 무엇을 다시 확인해야 하는지 계산한다 (워크플로우 S05, 11장).

- `diff_plan(before, after) -> set[ChangedField]`
- 재확인 트리거: 목표, 지역, 성과지표, 지표 용도, 대상, 기간 (워크플로우 11장: 목표·지역·지표 변경 시 영향받는 선택 재확인)
- 트리거가 아닌 변경 (예: 사업명 오타 수정)은 선택을 유지한다
- 결과는 `choices/`가 받아 해당 규칙의 선택을 "재확인 필요"로 바꾼다
- 현재 `web/session.py`의 `review_restarted` 플래그는 전체 변경 여부만 본다 → `changes.py` 구현 후 항목 단위로 대체

## 의존 관계

- 가져다 쓰는 곳: `paths.py`
- 이 폴더를 쓰는 곳: `review/`, `choices/`, `document/`, `web/`
- 쓰면 안 되는 것: `web/`, `evidence/`, FastAPI

## 테스트

- `tests/test_plan_validation.py` (있음): 필수 7개, 예산 3상태 구분, 잘못된 예산, pending, 기타 설명, 목록 밖 선택값·지역, 기간 역전
- `tests/test_plan_changes.py` (예정): 트리거 필드 변경 시에만 재확인 대상 반환
