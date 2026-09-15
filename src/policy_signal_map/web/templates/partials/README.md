# web/templates/partials/ — 반복되는 화면 조각

## 역할

여러 단계 화면에서 같은 모양으로 반복되는 부분을 `{% include %}` 또는 매크로로 분리한다. 같은 정보(예: 전국 참고 표시)가 화면마다 다르게 보이지 않게 하는 것이 목적이다.

## 만들 파일

| 파일 | 상태 | 쓰는 화면 | 내용 |
|---|---|---|---|
| `evidence_badges.html` | 예정 (9/16~17) | evidence, questions, draft | 범위(전국 참고/시도/넓은 범위 참고), 기간, 자료 버전, 합성·실제 칩 |
| `month_table.html` | 예정 (9/16~17) | evidence | 월·금액(억원)·비중·미상 비중·미상 제외 비중·상태 표. 보류 월은 회색 행과 사유 |
| `pair_chips.html` | 예정 (9/17) | evidence | 인접 구간 방향 칩 (같음/다름/보류, 0.01%p 미만 표기) |
| `rule_card.html` | 예정 (9/17) | questions | 규칙 ID·제목·메시지·"왜 묻나요?"·근거 칩. kind별 스타일 (질문/안내/추가 확정 필요/보류) |
| `option_card.html` | 예정 (9/17) | choices | 대안 제목·바뀌는 곳·필요 자료·운영 부담·선택 표시 |
| `pending_badge.html` | 예정 (9/17) | input, choices, draft | "추가 확정 필요" 노란 칩 매크로 |
| `evidence_trace.html` | 예정 (9/18) | draft | 변경 문장의 근거 추적 패널 |

## 원칙

- 조각은 받은 값만 표시한다. 필요한 값이 없으면 빈칸이 아니라 "자료 없음"을 표시한다
- 매크로 인자 이름은 로직 데이터 형태의 필드 이름과 같게 둔다 (예: `evidence_id`, `calculation_status`)
