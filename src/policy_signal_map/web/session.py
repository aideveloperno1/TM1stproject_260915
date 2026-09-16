"""작업 상태 보관.

첫 버전은 서버 메모리에만 두고 로그인·장기 보관은 하지 않는다 (최종기획서 11장 후순위).
서버가 다시 시작되면 모든 작업 상태가 초기화된다.
"""

from __future__ import annotations

import secrets
from copy import deepcopy
from dataclasses import dataclass, field
from threading import Lock

from ..plan.models import PlanInput

COOKIE_NAME = "psm_session"


@dataclass
class WorkState:
    # 사용자가 편집 중인 기획
    plan: PlanInput = field(default_factory=PlanInput)
    # [검토 시작] 시점에 보관한 원안. 보완 기획안의 "변경 전" 기준이 된다.
    original: PlanInput | None = None
    # 이번 제출에서 원안이 바뀌었는지. 이후 단계의 선택을 재확인할 때 쓴다.
    # 한 번 켜지면 계속 남지 않도록 제출할 때마다 다시 정한다 (4번에서 plan/changes.py의 항목별 재확인으로 대체 예정)
    review_restarted: bool = False

    def start_review(self) -> None:
        self.review_restarted = self.original is not None and self.original != self.plan
        self.original = deepcopy(self.plan)


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
