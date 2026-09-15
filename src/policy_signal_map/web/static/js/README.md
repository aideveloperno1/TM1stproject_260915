# web/static/js/ — 화면 반응 스크립트

## 원칙

- 빌드 도구 없이 브라우저가 바로 읽는 일반 JS (모듈 번들 없음)
- 파일마다 즉시 실행 함수로 감싸 전역 변수를 만들지 않는다
- 서버가 `<script type="application/json">`으로 넘긴 데이터만 사용하고, 숫자를 다시 계산하지 않는다
- 사용자 입력을 `innerHTML`에 넣지 않는다 (`textContent`, `new Option()` 사용)

## 만들 파일

| 파일 | 상태 | 쓰는 화면 | 내용 |
|---|---|---|---|
| `input.js` | 있음 | 1 기획 입력 | 기타 입력칸 표시, 지역 범위별 시도·시군구 선택 표시와 시군구 목록 갱신, 예산 미정 시 금액 입력 비활성·금액 표시, 지표 용도 안내 문구, 첫 오류로 스크롤 |
| `charts.js` | 예정 (9/16~17) | 2 근거 확인 | Chart.js 차트 2개 |
| `choices.js` | 예정 (9/17) | 4 보완 선택 | 대안 선택에 따라 실행 조건 입력 박스 표시, 수정 입력칸 표시 |
| `save.js` | 예정 (9/18) | 5 보완 기획안, 전체 문서 보기 | [결과 저장] 저장 위치 선택 |
| `trace.js` | 예정 (9/18) | 5 보완 기획안 | 근거 칩 클릭 시 근거 추적 패널 열고 닫기 |

## 파일별 상세

### `charts.js`

- 입력: `<script id="chart-data" type="application/json">`
  ```
  { "months": ["2026-01", ...],
    "foreign_amount_eok": [.., null, ..],     서버가 억원으로 변환, 자료 없음은 null
    "share_all_pct": [...], "share_known_pct": [...],
    "status": ["ok", "no_data", ...] }
  ```
- 금액 막대 차트, 비중 선 차트 (전체 분모 / 미상 제외 버튼으로 데이터셋 전환)
- null은 막대·점을 그리지 않고 끊는다 (`spanGaps: false`). 0으로 그리지 않는다
- 축 눈금 소수 둘째 자리, 툴팁에 상태 표시
- 색상: 시안 파랑 계열만. 반대 방향 구간을 빨간색으로 강조하지 않는다

### `choices.js`

- 대안 라디오 변경 → 해당 질문의 실행 조건 박스(`data-execution-for`) 표시/숨김
- [수정] 선택 → 수정 문장 입력칸 표시
- 필수 검증은 서버가 한다. JS는 표시만

### `save.js`

checks.md 결정: [결과 저장] → 저장 위치 선택 창 → 사용자가 고른 폴더에 Markdown 저장.

1. 버튼의 `data-download-url`(`/step/5/download`)로 `fetch` → 본문 텍스트, 응답 헤더에서 파일명 추출
2. `window.showSaveFilePicker`가 있으면
   - `suggestedName`: 파일명, `types`: `[{ description: "Markdown", accept: { "text/markdown": [".md"] } }]`
   - `createWritable()` → `write()` → `close()`
   - 사용자가 창을 닫으면(`AbortError`) 아무 안내 없이 종료
3. 없으면 (Firefox·Safari 등) `Blob` + `<a download>` 방식으로 다운로드 → "다운로드 폴더에 저장되었습니다" 안내
4. 실패 시 "저장하지 못했습니다. [전체 문서 보기]에서 내용을 복사할 수 있습니다" 안내
- 저장 위치 선택 창은 HTTPS 또는 localhost에서만 동작한다. 공개 배포는 HTTPS 필수

### `trace.js`

- `data-trace-target` 칩 클릭 → 해당 근거 패널 `hidden` 토글, 포커스 이동
- 패널 내용은 서버가 렌더링해 둔 것을 보여주기만 한다
