# 소비 시그널 정책맵 — 서비스

기획안을 입력하면 소비데이터 근거로 확인할 점을 보여주고, 담당자가 고른 보완 방법을 반영한 보완 기획안을 만드는 서비스.

- 기준 문서: [최종기획서](../최종기획/최종기획서.md) · [개발업무 워크플로우](../최종기획/개발업무_워크플로우.md)
- 합의·진행 기록: [checks.md](./checks.md)

## 개발 환경

uv + Python 3.12, FastAPI + Jinja2.

```powershell
uv sync                                   # 의존성 설치
uv run policy-signal-map                  # 로컬 실행 → http://127.0.0.1:8000
uv run pytest                             # 테스트
uv run python scripts/build_regions.py    # 지역 선택 목록 다시 만들기
```

## 구조

순수 로직(plan·evidence·review·choices·document)과 웹 계층(web)을 나눈다. 의존 방향은 한쪽으로만 간다.

```
web → document → choices → review → evidence, plan
llm → review 결과만 사용 (evidence 직접 사용 금지)
```

**모든 폴더에 `README.md`가 있다.** 폴더의 역할, 만들 파일(있음/예정), 파일별 상세, 지켜야 할 원칙, 테스트를 적어 두었다. 새 파일을 만들기 전에 해당 폴더 README를 먼저 보고, 구현하면 표의 상태를 갱신한다.

| 폴더 | 역할 | 설명 |
|---|---|---|
| `src/policy_signal_map/` | 패키지 루트: app·paths·config | [README](src/policy_signal_map/README.md) |
| `  plan/` | S01 기획 입력 | [README](src/policy_signal_map/plan/README.md) |
| `  evidence/` | 분석 근거 읽기·검증, 비교 A/B 계산 | [README](src/policy_signal_map/evidence/README.md) |
| `  review/` | S02 검토 규칙 실행 | [README](src/policy_signal_map/review/README.md) |
| `  choices/` | S03 보완 선택·실행 조건·재확인 | [README](src/policy_signal_map/choices/README.md) |
| `  document/` | S04·S05 보완 기획안 Markdown | [README](src/policy_signal_map/document/README.md) |
| `  llm/` | C 단계 AI 참고 의견 | [README](src/policy_signal_map/llm/README.md) |
| `  web/` | 세션·폼·표시 형식 | [README](src/policy_signal_map/web/README.md) |
| `    routes/` | 단계별 라우트 | [README](src/policy_signal_map/web/routes/README.md) |
| `    templates/` (`steps/`, `partials/`) | Jinja2 화면 | [README](src/policy_signal_map/web/templates/README.md) |
| `    static/` (`css/`, `js/`) | 스타일·화면 반응·결과 저장 | [README](src/policy_signal_map/web/static/README.md) |
| `  resources/` (`rules/`, `evidence/`, `documents/`) | 규칙 원본·합성 근거·문서 양식 | [README](src/policy_signal_map/resources/README.md) |
| `tests/` (`fixtures/evidence/`) | pytest, 경계 사례 | [README](tests/README.md) |
| `scripts/` | 지역 목록·합성 근거 생성, 공개 자료 검사 | [README](scripts/README.md) |
| `docs/` (`screenshots/`) | 규칙 설명·대안 비교·사용법·제출 구성 | [README](docs/README.md) |
| `private/` | 실제 분석 근거 (README 외 git 제외) | [README](private/README.md) |

데이터 분석 담당의 작업은 `../Analysis/`에 둔다. 두 폴더 사이에서는 `review_evidence.json`만 오간다.

화면의 모든 수치는 시연용 합성 수치다. 실제 카드 분석 결과는 `private/`에만 둔다.

## 권리 고지

이 저장소는 「제1회 AI금융빅데이터플랫폼 소비데이터 활용 아이디어 공모전」 제출을 위한 작업물이며, 오픈소스 라이선스를 부여하지 않는다.
코드와 문서의 모든 권리는 작성자에게 있고, 사전 허락 없이 사용·복제·수정·배포할 수 없다.
공모전 수상 시 산출물의 권리는 공모전 규정에 따른다.

사용한 외부 라이브러리와 글꼴은 각자의 라이선스를 따른다 (FastAPI·Chart.js: MIT, Jinja2·uvicorn: BSD, Pretendard: SIL OFL).
