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
from ..llm.opinions import OpinionSet
from ..plan.changes import diff_plan
from ..plan.models import PlanInput

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
    # AI 참고 의견과 그것을 만든 원안. 원안이 바뀌면 다시 부른다 (PlanInput은 해시할 수 없어 값으로 비교한다)
    opinions: OpinionSet | None = None
    opinions_for: PlanInput | None = None

    @property
    def review_restarted(self) -> bool:
        return bool(self.changed_fields)

    def start_review(self) -> None:
        self.changed_fields = diff_plan(self.original, self.plan)
        self.original = deepcopy(self.plan)
        self.opinions = None
        self.opinions_for = None

    def cached_opinions(self) -> OpinionSet | None:
        """이번 원안으로 만든 의견만 다시 쓴다."""
        if self.opinions is not None and self.opinions_for == self.original:
            return self.opinions
        return None

    def remember_opinions(self, opinions: OpinionSet) -> None:
        self.opinions = opinions
        self.opinions_for = deepcopy(self.original)


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
