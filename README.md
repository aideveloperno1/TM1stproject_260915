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

```
src/policy_signal_map/
  app.py          라우트 (단계별 화면)
  models.py       기획 입력 데이터 형태
  forms.py        폼 값 → 기획 입력
  validation.py   필수 항목 검증, 추가 확정 필요 항목
  session.py      작업 상태 보관 (서버 메모리)
  regions.py      시도·시군구 목록
  labels.py       화면 문구·검토 규칙 표시
  data/           regions.json (공개 주민등록인구 CSV에서 생성)
  templates/      Jinja2 화면
  static/         CSS, 화면 반응용 JS
tests/            pytest
private/          실제 분석 근거 파일 (git 제외, 공개 배포 금지)
```

화면의 모든 수치는 시연용 합성 수치다. 실제 카드 분석 결과는 `private/`에만 둔다.
