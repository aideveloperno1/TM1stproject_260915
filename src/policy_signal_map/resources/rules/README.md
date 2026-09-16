# resources/rules/ — 검토 규칙 원본

## 역할

규칙 R01~R07의 이름·구현 범위·질문 문구·대안·대안별 문서 문장·AI용 상황 설명을 담는 **원본**. 사람이 읽는 설명은 `docs/review_rules.md`이며, 두 파일은 항상 일치해야 한다.
조건 판단 로직은 `review/`의 코드가 규칙 ID별로 맡는다.

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `review_rules.json` | 있음 (v1.0) | 규칙 7개, 묶음 이름, 문구·대안·문서 문장·상황 설명 |

## `review_rules.json` 구조

```
{
  "version": "1.0",
  "description": "...",
  "merge_groups": { "participation_data": "참여 실적 자료" },
  "rules": [
    {
      "id": "R07",
      "title": "금액·비중과 성과지표 확인",
      "scope": "implement" | "basic" | "example" | "future",
      "summary": "입력 화면 오른쪽 패널 한 줄 설명",
      "messages": {
        "question_direct": "...", "question_unknown": "...", "notice_reference": "...",
        "goal_mismatch_prefix": "... {goal_label} ... {metric_label} ...",
        "why_opposite": "... {period} ... {comparable_count} ... {opposite_count} ...",
        "why_same": "...", "held_no_record": "...", "held_blocked": "... {reason}",
        "held_needs_review": "... {reason}", "held_no_pairs": "..."
      },
      "options": [
        {
          "id": "A", "title": "참여 실적 추가", "where": "7. 성과 측정계획",
          "need": "쿠폰 발급·사용·정산 자료", "load": "중",
          "execution_fields": ["collect_items", "availability", "owner", "cycle"],
          "document": {
            "section": 7, "mode": "append",
            "lines": ["주요 지표: {collect_items}", "...", "수집 담당: {owner}", "확인 주기: {cycle}", "자료 확보 여부: {availability}"]
          }
        },
        { "id": "D", "...": "...", "document": { "section": 8, "mode": "append", "lines": ["..."], "appendix": "request" } }
      ],
      "related_fields": ["goals", "metrics", "indicator_use", "region"],
      "document_targets": ["..."],
      "merge_group": "participation_data",
      "llm_context": { "question_direct": "수치 없는 상황 설명", "why_opposite": "...", "...": "..." }
    }
  ]
}
```

| 필드 | 뜻 | 불러올 때 검사 (`review/rules.py`) |
|---|---|---|
| `version` | `"1.0"`만 허용 | 다르면 오류 |
| `merge_groups` | 묶음 키 → 화면·문서에 쓸 한글 이름 | 규칙의 `merge_group`에 이름이 없으면 오류 (내부 키가 문서에 실리지 않게) |
| `scope` | implement(검토 구현)·basic(기본 검토)·example(분석 예시)·future(향후 기능) | 목록 밖이면 오류. implement·basic인데 `engine.RUN_ORDER`에 실행 함수가 없으면 **앱 시작 실패** |
| `messages` | 화면 문장. `{이름}` 자리에 값을 채움. example·future는 `not_reviewed` 키 | 없는 키를 쓰면 실행 중 오류 |
| `options[].execution_fields` | 대안 A를 고르면 받는 입력(수집 자료는 필수) | — |
| `options[].document` | 대안을 채택했을 때 보완 기획안에 들어갈 문장. `section` 1~8, `mode` append(장 끝에 덧붙임)·replace(`replace_key` 줄을 바꿈), `appendix: "request"`면 요청서 초안 첨부 | 없거나 장 번호·방식이 틀리거나 replace인데 `replace_key`가 없으면 오류 |
| `lines` 자리표시자 | `{collect_items}{owner}{cycle}{availability}{usage_place}{target}{goals}{goals_without_store_usage}{metrics}` — 빈 값은 `[추가 확정 필요]` | — |
| `related_fields` | 이 입력이 바뀌면 선택을 "재확인 필요"로 (`plan/changes.py`의 항목 이름과 같아야 함) | — |
| `merge_group` | 같은 값의 질문끼리 **4단계 실행 조건 입력을 공유**. 3단계 카드는 합치지 않고 서로 가리킨다 | — |
| `llm_context` | `messages`와 같은 키로, AI 참고 의견에 넘길 **수치 없는 상황 설명** 한 줄. R06·R02(`not_reviewed`)의 것은 정의만 있고 지금은 넘기지 않음 | 테스트가 숫자·`%`·`원`·`{`·판정 단어를 막음 |

- 규칙 7개: R07(implement, 대안 A~D), R01·R03·R04(basic, 대안 A·B), R05(basic, 대안 없음), R06(example), R02(future)
- `why_opposite` 같은 문장에는 수치가 들어간다. **LLM에는 `messages`가 아니라 `llm_context`만 넘긴다** (`ReviewOutcome.context_keys` → `to_llm_summary`)

## 대안 문구 출처

- R07 대안 A~D: 최종기획서 4-4장, 시안 `OPTS`
- R07 문서 반영: 최종기획서 4-5장, 워크플로우 11장 "지표 정의·자료 수집·담당자·주기"
- R01·R03·R04·R05: 워크플로우 11장 표 (조건은 `docs/review_rules.md`에서 데이터 담당과 확정)

## 원칙

- 질문 문구에 "오류", "잘못", "실패" 같은 판정 단어를 쓰지 않는다
- 대안에 성공 확률·점수·추천 순위를 두지 않는다
- 옵션 D 문구에 계약·제공이 확정된 것처럼 읽히는 표현을 쓰지 않는다
- 파일 수정 후 `uv run pytest`를 통과해야 한다 (규칙 ID·코드 일치, 판정 단어, `llm_context` 수치, 실행 중 나온 문구 키가 모두 상황 설명을 찾는지)
- 한글이 들어 있으므로 스크립트로 고칠 때는 Python(`ensure_ascii=False, indent=2`)을 쓴다. PowerShell `ConvertTo-Json`은 한글을 깨뜨렸다
- 고치면 `docs/review_rules.md`도 함께 고친다
