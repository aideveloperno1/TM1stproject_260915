# resources/rules/ — 검토 규칙 원본

## 역할

규칙 R01~R07의 이름·구현 범위·질문 문구·대안·문서 반영 위치를 담는 **원본**. 사람이 읽는 설명은 `docs/review_rules.md`이며, 두 파일은 항상 일치해야 한다.
조건 판단 로직은 `review/`의 코드가 규칙 ID별로 맡는다.

## 만들 파일

| 파일 | 상태 | 내용 |
|---|---|---|
| `review_rules.json` | 있음 (v0.1, 확장 예정 9/17) | 규칙 목록 |

## `review_rules.json` 구조

현재(v0.1)는 `id`, `title`, `scope`, `summary`만 있다. v1.0에서 아래 필드를 추가한다.

```
{
  "version": "1.0",
  "rules": [
    {
      "id": "R07",
      "title": "금액·비중과 성과지표 확인",
      "scope": "implement" | "basic" | "example" | "future",
      "summary": "오른쪽 패널 한 줄 설명",
      "not_reviewed_reason": "scope가 example/future일 때 표시할 이유",

      "messages": {
        "question_direct": "직접 평가일 때 질문 문장 ({goal} 같은 자리표시자 허용)",
        "question_unknown": "지표 용도 아직 모름일 때",
        "notice_reference": "참고 현황일 때 안내 (오류 표현 금지)",
        "why_opposite": "왜 묻나요? — 반대 방향 구간이 있을 때 ({opposite_count}, {pair_count})",
        "why_same": "왜 묻나요? — 반대 방향 구간이 없을 때",
        "held": "근거 보류 시"
      },

      "options": [
        {
          "id": "A",
          "title": "참여 실적 추가",
          "where": "7. 성과 측정계획",
          "need": "쿠폰 발급·사용·정산 자료",
          "load": "중",
          "execution_fields": ["collect_items", "availability", "owner", "cycle"],
          "document": {
            "section": 7,
            "lines": ["주요 지표: {collect_items}", "참고 지표: 외국인 결제금액·비중(전체·미상 제외)", "수집 담당: {owner}", "수집 주기: {cycle}"]
          }
        },
        { "id": "B", "title": "해석 조건 명시", ... },
        { "id": "C", "title": "자료 확보 전", ... },
        { "id": "D", "title": "정밀 분석 요청서 초안", "document": { "appendix": "request" }, ... }
      ],

      "related_fields": ["goals", "metrics", "indicator_use", "region"],
      "merge_group": "participation_data"
    }
  ]
}
```

- `related_fields`: 이 필드가 바뀌면 선택을 재확인 (`choices/recheck.py`)
- `merge_group`: 같은 값을 가진 규칙의 질문은 하나로 묶는다 (워크플로우 11장)
- 문구 자리표시자에는 **숫자를 넣지 않는 문구와 숫자를 넣는 문구를 구분**한다. LLM 요약(`to_llm_summary`)은 숫자 없는 문구만 사용

## 대안 문구 출처

- R07 대안 A~D: 최종기획서 4-4장, 시안 `OPTS`
- R07 문서 반영: 최종기획서 4-5장, 워크플로우 11장 "지표 정의·자료 수집·담당자·주기"
- R01·R03·R04·R05: 워크플로우 11장 표 (조건은 `docs/review_rules.md`에서 데이터 담당과 확정)

## 원칙

- 질문 문구에 "오류", "잘못", "실패" 같은 판정 단어를 쓰지 않는다
- 대안에 성공 확률·점수·추천 순위를 두지 않는다
- 옵션 D 문구에 계약·제공이 확정된 것처럼 읽히는 표현을 쓰지 않는다
- 파일 수정 후 `uv run pytest`의 규칙 ID·코드 일치 테스트를 통과해야 한다
