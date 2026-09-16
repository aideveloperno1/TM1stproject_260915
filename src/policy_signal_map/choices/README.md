# choices/ — 보완 선택과 실행 조건 (S03)

## 역할

검토 결과(`review/`)의 질문마다 담당자가 고른 결정(원안 유지·채택·수정·보류)과 실행 조건 입력을 보관하고 검증한다.
원안이 바뀌면 영향받는 선택을 "재확인 필요"로 되돌린다. 서비스가 대신 고르지 않는다.

## 기준 문서

- 워크플로우 S03 보완 선택, S05 수정·출력, 11장 (재확인), 12장 (목표 유지·대안 취소, 목표·지역 변경)
- 최종기획서 3장 3~4단계, 4-4 선택할 보완 방법, 9장 (BC 제휴를 선택하지 않아도 기본 검토 제공)
- checks.md: 시안의 A~D 대안 + 원안 유지·보류 + 수정, "실행 조건"은 보완 선택 화면의 추가 입력 칸

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | 비어 있음 |
| `models.py` | 있음 | `Decision`(원안 유지·채택·수정·보류), `ExecutionInput`(merge_group 공유), `Choice`, `ChoiceSet`(보관함 포함) |
| `selection.py` | 있음 | 적용·취소·검증, 추가 확정 필요 목록, 5단계 차단 사유 |
| `recheck.py` | 있음 | 관련 항목이 바뀐 선택만 재확인, 사라진 질문의 선택 보관 |

## 파일별 상세

### `models.py`

```
Decision = "keep_original" | "adopt" | "modify" | "hold"

Choice
  rule_ids: list[str]              묶인 질문이면 여러 개
  decision: Decision
  option_id: str | None            adopt/modify일 때 A·B·C·D
  modified_text: str | None        modify일 때 담당자가 고친 문장
  execution: ExecutionInput | None 옵션이 요구할 때
  reason: str                      선택 이유 (선택 입력, 최종기획서 3장 "선택 이유와 변경 내용 기록")
  status: "confirmed" | "needs_recheck"
  evidence_ids: list[str]          review 결과에서 그대로 복사

ExecutionInput                     옵션 A 참여 실적 추가 기준
  collect_items: list[str]         예: 쿠폰 발급, 사용, 정산 실적
  availability: "available" | "negotiating" | "unavailable" | None
  owner: str                       담당자 (빈 값 허용 → 추가 확정 필요)
  cycle: str                       확인 주기 (빈 값 허용 → 추가 확정 필요)

ChoiceSet
  by_question: dict[question_key, Choice]
```

### `selection.py`

- `apply_choice(choice_set, outcome, form_values) -> ChoiceSet | ChoiceErrors`
- `cancel_choice(choice_set, question_key)` : 선택 삭제 → 문서에서도 해당 변경이 사라져야 함 (12장)
- `pending_from_choices(choice_set) -> list[str]` : 빈 담당자·주기, 확보 불가 자료, 보류 질문 → 추가 확정 필요
- 검증
  - `option_id`는 해당 규칙 JSON에 정의된 대안만 허용
  - `modify`는 수정 문장 필수
  - 옵션 A 선택 시 `collect_items` 1개 이상 필수, 담당자·주기는 비워도 됨 (비우면 "추가 확정 필요", 시안)
  - 아직 없는 자료는 "계획"으로 남긴다 (S03). 확보된 것처럼 바꾸지 않는다
  - 옵션 D는 "요청서 초안" 상태로만 저장. 계약·제공 확정 필드를 두지 않는다 (S03)
- 선택하지 않은 질문은 `keep_original`로 간주하지 않는다. "미선택"으로 남겨 기획안 생성 전에 확인받는다

### `recheck.py`

- `mark_recheck(choice_set, changed_fields, outcomes) -> ChoiceSet`
- `plan/changes.py`의 변경 필드와 `ReviewOutcome.related_fields`가 겹치는 선택만 `needs_recheck`
- 원안 변경 후 규칙을 다시 실행해 **질문 자체가 사라진 경우**: 선택을 보관함으로 옮기고 화면에 "원안 변경으로 더 이상 해당하지 않음" 표시, 문서에는 반영하지 않음
- `needs_recheck`가 하나라도 있으면 보완 기획안 생성을 막고 확인받는다 (11장: 최종 문서 생성 전에 확인)

## 의존 관계

- 가져다 쓰는 곳: `plan/`, `review/`
- 이 폴더를 쓰는 곳: `document/`, `web/`
- 쓰면 안 되는 것: `web/`, FastAPI, `evidence/` 직접 계산 (근거는 review 결과로만 받음)

## 테스트

`tests/test_choices.py` (예정)

| 확인 | 워크플로우 12장 |
|---|---|
| 대안 취소 시 ChoiceSet에서 제거 | 목표 유지·대안 취소 |
| 원안 유지 선택 시 변경 없음 | 목표 유지·대안 취소 |
| 목표 변경 → R07 선택만 needs_recheck, 사업명 변경은 유지 | 목표·지역 변경 |
| 옵션 A 담당자 빈 값 → pending 항목 | 자료 수집 미정 |
| JSON에 없는 option_id 거부 | — |
| needs_recheck 존재 시 문서 생성 차단 신호 | — |
