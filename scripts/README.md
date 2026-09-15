# scripts/ — 개발·배포 보조 스크립트

## 역할

서비스 실행 중에는 쓰지 않고, 개발자가 필요할 때 직접 실행하는 도구를 둔다. 모두 `uv run python scripts/<파일>.py`로 실행한다.

## 만들 파일

| 파일 | 상태 | 실행 시점 |
|---|---|---|
| `build_regions.py` | 있음 | 지역 원본 CSV가 바뀔 때 |
| `_evidence_builder.py` | 있음 | (직접 실행 안 함) 근거 JSON 조립 도우미 |
| `build_fixtures.py` | 있음 | 테스트 경계 사례를 바꿀 때 |
| `build_demo_evidence.py` | 있음 | 합성 근거 파일 형식·시나리오를 바꿀 때 |
| `check_public_bundle.py` | 예정 (9/16~17) | 매 푸시·배포 전 |

## 파일별 상세

### `build_regions.py` (있음)

- 입력: `../데이터/2/202601_202606_주민등록인구및세대현황_월간.csv` (행정안전부 공개 자료, cp949)
- 출력: `src/policy_signal_map/resources/regions.json`
- 규칙: 10자리 행정코드 끝 8자리가 0이면 시도, 6월 총인구 0인 코드 제외, 세종처럼 시군구 없는 시도는 하위 목록 비움
- 카드 CSV는 사용하지 않는다

### `_evidence_builder.py` (있음)

`ok_month`, `status_month`, `record`, `evidence_file`, `write_json`. 비중을 정수 금액에서 계산해 소수 10자리로 넣고, 미상 제외 분모가 0이면 null과 경고를 넣는다. JSON은 UTF-8·LF로 쓴다.

### `build_fixtures.py` (있음)

`tests/fixtures/evidence/`의 경계 사례 22개를 만든다. 정상 11개는 월 수치로, 오류 11개는 정상 사례에서 한 곳만 바꿔 만든다. `build_all()`은 테스트가 커밋된 파일과 비교할 때도 쓴다. 생성 목록에 없는 JSON이 폴더에 남아 있으면 종료 코드 1.

### `build_demo_evidence.py` (있음)

화면 시연용 합성 근거 파일을 만든다. 손으로 JSON을 쓰면 비중(%)과 금액이 서로 안 맞기 쉬워서, 정수 금액만 정하고 비중은 계산해서 넣는다.

- 출력: `src/policy_signal_map/resources/evidence/review_evidence_demo_v1.json`
- 내용
  - 레코드 A: 전국, 2026-01~06, 6개월 모두 `ok`. 금액·비중 반대 방향 구간과 같은 방향 구간이 섞이도록 구성 (반대 방향만 고르지 않음, 워크플로우 8-3장)
  - 레코드 B: 가상 시도 1곳, `no_data` 월과 `invalid_denominator` 월 포함 → 보류 사례 화면용
- 모든 레코드에 `data_kind: "synthetic"`, `dataset_version: "demo-001"`, limitations에 "합성 자료" 포함
- 금액은 800·10,000처럼 누가 봐도 가상 규모로 정한다. 최종기획서 4-2장 등 **실제 분석 수치를 쓰지 않는다**
- 비중 계산은 `_evidence_builder.py`를 쓰고, 만든 파일을 `evidence/loader.py`로 다시 읽어 오류·경고가 없는지 확인한다
- 테스트용 경계 사례는 이 스크립트가 아니라 `build_fixtures.py`가 만든다

### `check_public_bundle.py` (예정)

공개 저장소·공개 배포에 실제 자료가 섞이지 않았는지 검사한다. 파일 이름이 아니라 내용으로 검사해 이름을 바꿔 둔 실수도 잡는다.

- 대상: `git -c core.quotepath=false ls-files -z`로 얻은 추적 파일 전체 (한글 경로가 이스케이프되면 파일을 열지 못해 검사가 빠지므로), 열 수 없는 추적 파일은 위반
- 실패 조건
  - `.json` 파일 안에 `"data_kind": "real"`이 있음
  - 경로에 `private/`가 있음 (README.md 제외)
  - `.env` 파일이 추적됨
  - `dataset_version`이 `demo-`·`fixture-`로 시작하지 않는 근거 파일
  - 경로에 `_real_`이 있는 파일
- 결과: 문제 파일 목록을 출력하고 종료 코드 1
- `tests/test_public_bundle.py`에서도 같은 함수를 호출해 `uv run pytest`로 함께 검사한다

## 지켜야 할 원칙

- 스크립트는 `src/policy_signal_map`의 함수를 가져다 쓸 수 있지만, 서비스 코드가 스크립트를 가져다 쓰지는 않는다.
- 스크립트가 만든 결과 파일도 커밋 전에 `check_public_bundle.py`를 통과해야 한다.
