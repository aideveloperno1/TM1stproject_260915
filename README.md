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

```
src/policy_signal_map/
  app.py              FastAPI 생성, 라우터 등록
  paths.py            패키지 내 경로
  plan/               S01 기획 입력: models, validation, regions
  evidence/           분석 근거 읽기·검증, 비교 A/B 계산        (구현 예정)
  review/             검토 규칙: rules (규칙 목록 읽기)
  choices/            S03 보완 선택                              (구현 예정)
  document/           S04·S05 보완 기획안 Markdown               (구현 예정)
  llm/                C 단계 LLM 연결                            (구현 예정)
  web/
    session.py        작업 상태 보관 (서버 메모리)
    forms.py          폼 값 → 기획 입력
    labels.py         화면 선택지 문구
    templating.py     템플릿·리다이렉트 공통
    routes/           input.py, steps.py(2~5단계 임시)
    templates/        base.html, steps/*.html
    static/           css/, js/
  resources/          regions.json, rules/review_rules.json (규칙 원본)
tests/                pytest (helpers.py 공통)
scripts/              build_regions.py
private/              실제 분석 근거 파일 (git 제외, 공개 배포 금지)
```

데이터 분석 담당의 작업은 `../Analysis/`에 둔다. 두 폴더 사이에서는 `review_evidence.json`만 오간다.

화면의 모든 수치는 시연용 합성 수치다. 실제 카드 분석 결과는 `private/`에만 둔다.
