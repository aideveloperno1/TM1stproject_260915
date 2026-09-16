# web/templates/partials/ — 반복되는 화면 조각

## 역할

여러 단계 화면에서 같은 모양으로 반복되는 부분을 `{% include %}` 또는 매크로로 분리한다. 같은 정보(예: 전국 참고 표시)가 화면마다 다르게 보이지 않게 하는 것이 목적이다.

## 만들 파일

| 파일 | 상태 | 쓰는 화면 | 내용 |
|---|---|---|---|
| `evidence_badges.html` | 있음 | evidence (이후 questions, draft) | 매크로 `evidence_badges(record_view, dataset_version, data_kind, is_main)`: 범위(전국 참고 — 특정 지역의 진단이 아님 / 예시), 기간, 자료 버전, 합성·실제 |
| `month_table.html` | 있음 | evidence | 매크로 `month_table(record_view)`: 월·외국인 결제금액·전체 분모 비중·미상 비중·미상 제외 비중·상태(+경고). 보류 월 회색 행, 행마다 `data-row="month"` |
| `pair_table.html` | 있음 | evidence | 매크로 `pair_table(record_view)`: 구간·증감률 2개·비중 변화·비교 A·미상 제외 변화·비교 B. 보류 구간은 한 칸에 사유. 시안의 구간 칩 대신 표 (2근거확인화면계획 결정 ③) |
| `rule_card.html` | 있음 | questions | 매크로 `rule_card(outcome, kind_labels)`: 규칙 ID·제목·결과 종류·메시지·"왜 묻나요?"·범위/근거 칩·지역 안내·함께 확인. **대안은 4단계에서만 보여준다** |
| `option_card.html` | 있음 | choices | 대안 제목·바뀌는 곳·필요 자료·운영 부담·선택 표시. 점수·추천 순위 없음 |
| `pending_badge.html` | 있음 | choices (이후 input, draft) | "추가 확정 필요" 노란 칩 매크로 |
| `evidence_trace.html` | 예정 (9/18) | draft | 변경 문장의 근거 추적 패널 |

## 원칙

- 조각은 받은 값만 표시한다. 필요한 값이 없으면 빈칸이 아니라 "자료 없음"을 표시한다
- 매크로 인자 이름은 로직 데이터 형태의 필드 이름과 같게 둔다 (예: `evidence_id`, `calculation_status`)
