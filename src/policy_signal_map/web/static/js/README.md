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
| `charts.js` | 있음 | 2 근거 확인 | Chart.js 차트 2개, 분모 전환, 불러오기 실패 시 대체 문구 |
| `choices.js` | 있음 | 4 보완 선택 | 결정·대안에 따라 실행 조건 상자와 수정 입력칸 표시 (검증은 서버) |
| `save.js` | 있음 | 5 보완 기획안, 전체 문서 보기, 요청서 초안 | [결과 저장] 저장 위치 선택 |
| `trace.js` | 있음 | 5 보완 기획안 | 근거 칩을 누르면 해당 근거 추적 항목 강조 |
| `print.js` | 있음 | 5 보완 기획안, 전체 문서, 요청서 초안 | [PDF로 저장] → `window.print()` (사용자가 대화상자에서 대상을 PDF로 고른다) |
| `opinions.js` | 있음 | 3 검토 질문 (설정이 local일 때만) | 화면이 뜬 뒤 `/step/3/opinions`를 받아 채운다. 받은 문장은 `textContent`로만 넣는다 |

## 파일별 상세

### `charts.js`

- 입력: `<script id="chart-data" type="application/json">` (`web/evidence_view.chart_data`)
  ```
  { "unit": "원" | "억원",
    "labels": ["1월", ...],
    "status": ["ok", "no_data", ...],
    "foreign_amount": [820, null, ...],       원 단위면 정수, 억원이면 소수 둘째 자리, 계산할 수 없는 월은 null
    "share_all_pct": [8.2, ...], "share_known_pct": [8.5864, ...] }
  ```
- Chart.js 4.5.1은 jsDelivr CDN에서 `integrity`(sha384)와 함께 불러온다. `window.Chart`가 없으면 차트 카드를 숨기고 `.chart-fallback`을 보인다 (9/16 주소를 임시로 틀리게 바꿔 확인)
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

1. 버튼의 `data-url`(`/step/5/download`, 요청서는 `?kind=request`)과 `data-filename`을 읽는다
2. `window.showSaveFilePicker`가 있으면 먼저 위치를 고르게 하고(취소하면 "저장을 취소했습니다") 그다음 본문을 `fetch`해 `createWritable()` → `write()` → `close()`
3. 없으면 (Firefox·Safari 등) `<a download>`로 내려받고 "저장 위치 선택을 지원하지 않는 브라우저라 내려받기 폴더에 저장했습니다" 안내
4. 실패하면 안내 후 내려받기로 대신한다. 안내 문구는 화면의 `[data-save-note]` 자리에 넣는다
- 저장 위치 선택 창은 HTTPS 또는 localhost에서만 동작한다. 공개 배포는 HTTPS 필수
- 서버에는 파일을 남기지 않는다 (최종기획서 4-5)

### `print.js`

- 서버에서 PDF를 만들지 않는다. 서버 PDF 생성기(WeasyPrint·headless Chrome)는 한글 글꼴과 브라우저 바이너리를 배포에 얹어야 해서 공모전 일정에 위험이 크다
- `.md` 저장과 용도가 다르다: `.md`는 담당자가 **고쳐 쓰는 원고**, PDF는 **그대로 공유하는 사본**
- 인쇄 모양은 `style.css`의 `@media print`가 정한다

### `trace.js`

- `data-trace-link` 칩을 누르면 `data-trace`가 같은 근거 항목에 `trace-on`을 준다 (앵커 이동은 HTML만으로 동작)
- 패널 내용은 서버가 렌더링해 둔 것을 보여주기만 한다
