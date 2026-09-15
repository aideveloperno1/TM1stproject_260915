# web/static/ — CSS·JS 정적 파일

## 역할

`/static` 경로로 제공되는 파일. 화면 모양(CSS)과 서버 렌더링만으로 어려운 즉시 반응(JS)을 담당한다.
JS는 편의 기능만 맡고, **검증·계산·저장 내용 결정은 서버가 한다.** JS가 꺼져도 입력·제출·문서 보기는 동작해야 한다 (저장 위치 선택 창 제외).

이 폴더의 파일은 누구나 내려받을 수 있다. 실제 자료·API 키를 두지 않는다.

## 하위 폴더

| 폴더 | 내용 |
|---|---|
| `css/` | 스타일 |
| `js/` | 화면 반응 스크립트 |

## 외부 자원

| 자원 | 불러오는 곳 | 비고 |
|---|---|---|
| Pretendard 1.3.9 | `templates/base.html` (jsDelivr CDN) | SIL OFL |
| Chart.js 4.5.1 | `templates/steps/evidence.html` (jsDelivr CDN, 버전 고정) | MIT, 2단계에서만 로드 |

CDN을 쓸 수 없는 환경(내부 시연 오프라인 등)이 확인되면 `static/vendor/`에 파일을 내려받아 두는 방식으로 바꾼다.
