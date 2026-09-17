"""작업 상태 보관.

첫 버전은 서버 메모리에만 두고 로그인·장기 보관은 하지 않는다 (최종기획서 11장 후순위).
서버가 다시 시작되면 모든 작업 상태가 초기화된다.
"""

from __future__ import annotations

import secrets
from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock

from ..choices.models import ChoiceSet
from ..choices.recheck import sync_after_review
from ..llm.opinions import OpinionSet
from ..plan.changes import diff_plan
from ..plan.models import PlanInput
from ..review.outcome import ReviewResult

COOKIE_NAME = "psm_session"


@dataclass
class WorkState:
    # 사용자가 편집 중인 기획
    plan: PlanInput = field(default_factory=PlanInput)
    # [검토 시작] 시점에 보관한 원안. 보완 기획안의 "변경 전" 기준이 된다.
    original: PlanInput | None = None
    # 이번 제출에서 바뀐 입력 항목 (plan/changes.py 이름). 관련된 선택만 재확인 대상이 된다.
    changed_fields: frozenset[str] = frozenset()
    # 담당자가 고른 보완 방법
    choices: ChoiceSet = field(default_factory=ChoiceSet)
    # 담당자가 3단계에서 고른 AI 모델. None이면 설정의 기본 모델
    llm_model: str | None = None
    # AI 참고 의견을 모델별로 보관하고, 그것을 만든 원안을 함께 둔다.
    # 원안이 바뀌면 모두 다시 부른다 (PlanInput은 해시할 수 없어 값으로 비교한다).
    # 모델을 바꿨다가 돌아오면 앞서 받은 의견을 다시 쓴다 (모델 호출이 느리기 때문)
    opinions: dict[str, OpinionSet] = field(default_factory=dict)
    opinions_for: PlanInput | None = None
    # 이번 원안에 대해 선택 정리(재확인 표시·사라진 질문 보관)를 마쳤는지.
    # 원안을 제출할 때마다 한 번만 한다. 매번 하면 다시 저장해 푼 재확인 표시가 또 붙는다 (6-5a)
    choices_synced: bool = False

    @property
    def review_restarted(self) -> bool:
        return bool(self.changed_fields)

    def start_review(self) -> None:
        self.changed_fields = diff_plan(self.original, self.plan)
        self.original = deepcopy(self.plan)
        self.choices_synced = False
        self.opinions = {}
        self.opinions_for = None

    def sync_choices(self, result: ReviewResult) -> None:
        """원안이 바뀐 뒤 선택을 정리한다. 4단계·5단계·내려받기 어디로 먼저 가도 문서를 만들기 전에 거친다."""
        if not self.choices_synced:
            sync_after_review(self.choices, result, self.changed_fields)
            self.choices_synced = True

    def cached_opinions(self, model: str) -> OpinionSet | None:
        """이번 원안으로 이 모델이 만든 의견만 다시 쓴다."""
        if self.opinions_for == self.original:
            return self.opinions.get(model)
        return None

    def remember_opinions(self, model: str, opinions: OpinionSet) -> None:
        if self.opinions_for != self.original:
            self.opinions = {}
            self.opinions_for = deepcopy(self.original)
        self.opinions[model] = opinions


class SessionStore:
    def __init__(self) -> None:
        self._states: dict[str, WorkState] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str | None) -> tuple[str, WorkState]:
        with self._lock:
            if session_id and session_id in self._states:
                return session_id, self._states[session_id]
            new_id = secrets.token_urlsafe(24)
            state = WorkState()
            self._states[new_id] = state
            return new_id, state

    def reset(self, session_id: str) -> None:
        with self._lock:
            self._states[session_id] = WorkState()


store = SessionStore()
