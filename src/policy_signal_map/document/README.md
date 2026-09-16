# document/ — 보완 기획안 생성과 Markdown 출력 (S04·S05)

## 역할

원안(`plan/`) + 검토 결과(`review/`) + 담당자 선택(`choices/`)을 합쳐 **전체 보완 기획안**을 만들고 Markdown 문자열로 출력한다.
AI 없이 정해 둔 양식에 확인된 값만 채운다. 미정 값을 지어내지 않는다.

## 기준 문서

- 워크플로우 S04 전체 기획안 생성, S05 수정·출력, 12장 (목표 유지·대안 취소, Markdown 내보내기)
- 최종기획서 4-5 최종 기획안에서 바뀌는 부분, 6장 제공할 화면과 문서, 8장 (문서 생성에 AI 필수 아님)
- checks.md: 파일명 `보완기획안_{사업명}_{날짜}.md`, 별첨은 같은 파일 맨 뒤, [전체 문서 보기]·[정밀 분석 요청서 초안]

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `__init__.py` | 있음 | 비어 있음 |
| `models.py` | 있음 | 문서 구조 데이터 형태 |
| `describe.py` | 있음 | 원안 → 장·줄 문장 (화면·문서 공용) |
| `builder.py` | 있음 | 원안 + 선택 → 문서 구조, 변경 목록 |
| `render.py` | 있음 | 문서 구조 → Markdown (`resources/documents/` 양식 사용) |
| `filename.py` | 있음 | 저장 파일 이름 만들기 (기획안·요청서) |

## 파일별 상세

### `models.py`

```
PlanDocument
  title: str
  sections: list[Section]
  changes: list[Change]              별첨 1 변경 전후
  evidence_refs: list[EvidenceRef]   별첨 2 근거
  pending: list[PendingItem]         추가 확정 필요
  request_draft: RequestDraft | None 별첨 3, 옵션 D 선택 시만
  data_notice: str                   "시연용 합성 수치" 또는 실제 자료 버전 표시

Section
  number: int
  title: str
  lines: list[Line]

Line
  text: str
  state: "original" | "changed" | "added" | "pending"
  change_id: str | None
  evidence_ids: list[str]

Change
  change_id, section_number
  before: str | None, after: str
  rule_ids: list[str], evidence_ids: list[str]
  decision: Decision, reason: str

EvidenceRef
  evidence_id, data_kind, dataset_version
  scope_label, period, limitations: list[str]
```

### `builder.py`

- `build_document(original, review_result, choice_set) -> PlanDocument`
- 장 구성 (최종기획서 6장 순서)
  1. 사업 개요 — 사업명, 기간, 지역
  2. 목적·대상
  3. 일정
  4. 혜택·사용처
  5. 모집·정산
  6. 예산 상태 — 미정/미입력은 "추가 확정 필요", 금액은 원 단위 그대로
  7. 성과 측정계획 — 지표 정의, 자료 수집, 담당자, 주기 (R07 반영 위치)
  8. 추가 확인사항 — pending 전체
- 규칙
  - **선택하지 않은 항목은 원안 문장을 그대로 유지** (S04)
  - 채택·수정한 변경만 `changed`/`added`로 표시하고 `Change` 기록
  - 취소한 선택은 문서에 흔적을 남기지 않는다 (12장)
  - 원안에 없는 값(예산 금액, 점포 수, 협약 기관)은 채우지 않고 pending으로 (최종기획서 3장)
  - 전국 근거를 쓴 변경에는 근거 표시에 "전국 참고" 포함
  - `needs_recheck` 선택이 있으면 `DocumentBlocked` 반환 (choices/recheck)
  - 옵션 D는 요청서 **초안**만 생성, "계약·자료 제공이 확정된 것이 아님" 문구 필수
- 원안 문장 만들기: 입력 필드를 사람이 읽는 문장으로 옮기는 함수(`describe_plan`)를 여기 둔다. 화면 원안 요약과 문서가 같은 함수를 쓴다

### `render.py`

- `render_markdown(doc) -> str`
- 양식: `resources/documents/plan.md.j2`, `resources/documents/request.md.j2`
- Jinja2 `Environment(autoescape=False)` + Markdown 특수문자 이스케이프 필터(`md_escape`)를 사용자 입력에만 적용 (표 깨짐·링크 삽입 방지)
- 변경 줄 표시: 줄 끝에 `〔변경 · 근거 R07-A〕` 같은 텍스트 표기 (HTML 주석은 외부 편집기에서 안 보이므로 쓰지 않음)
- 출력 순서: 본문 1~8장 → 별첨 1 변경 전후 → 별첨 2 근거와 한계 → 별첨 3 요청서 초안(있을 때)
- 같은 문서 구조면 항상 같은 문자열 (생성 시각은 파일 머리의 한 줄에만)

### `filename.py`

- `document_filename(plan_name, today) -> "보완기획안_{사업명}_{YYYYMMDD}.md"`
- 파일명에 쓸 수 없는 문자(`\ / : * ? " < > |`)와 앞뒤 공백 제거, 공백은 `_`, 최대 60자
- 사업명이 비면 `보완기획안_{YYYYMMDD}.md`

## 의존 관계

- 가져다 쓰는 곳: `plan/`, `review/`, `choices/`, `resources/documents/`, Jinja2 라이브러리
- 이 폴더를 쓰는 곳: `web/routes/draft.py`
- 쓰면 안 되는 것: `web/`, FastAPI, LLM (문서 생성에 AI 사용 안 함)

## 테스트

`tests/test_document_describe.py`, `test_document_builder.py`, `test_document_render.py`, `test_document_filename.py` (공용 준비는 `tests/document_helpers.py`)

| 확인 | 워크플로우 12장 |
|---|---|
| 선택 없음 → 원안과 같은 내용, 변경 0건 | 목표 유지·대안 취소 |
| 옵션 A 채택 → 7장에 수집계획·담당자·주기, 별첨 1에 변경 기록 | — |
| 옵션 A 채택 후 취소 → 변경 흔적 없음 | 목표 유지·대안 취소 |
| 예산 미정 → "추가 확정 필요", 금액 지어내지 않음 | 자료 수집 미정 |
| 담당자 빈 값 → pending | 자료 수집 미정 |
| 전국 근거 → 별첨 2에 전국 참고·한계 | 전국 자료 + 특정 지역 기획 |
| 합성 근거 → 문서에 "시연용 합성 수치" 표시 | 공개 배포 |
| needs_recheck 존재 → 생성 차단 | 목표·지역 변경 |
| 사용자 입력의 `|`, `[`, `](` 이스케이프 | — |
| 파일명 금지 문자 제거 | Markdown 내보내기 |
