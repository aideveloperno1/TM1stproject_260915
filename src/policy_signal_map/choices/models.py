"""보완 선택 데이터 형태 (워크플로우 S03, 4보완선택계획.md 3장).

서비스는 대신 고르지 않는다. 비어 있는 값은 추측해 채우지 않고 "추가 확정 필요"로 남긴다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Decision(StrEnum):
    KEEP_ORIGINAL = "keep_original"
    ADOPT = "adopt"
    MODIFY = "modify"
    HOLD = "hold"


class Availability(StrEnum):
    AVAILABLE = "available"
    NEGOTIATING = "negotiating"
    UNAVAILABLE = "unavailable"


DECISION_LABELS = {
    Decision.KEEP_ORIGINAL: "원안 유지",
    Decision.ADOPT: "채택",
    Decision.MODIFY: "수정",
    Decision.HOLD: "보류",
}

AVAILABILITY_LABELS = {
    Availability.AVAILABLE: "확보 가능",
    Availability.NEGOTIATING: "협의 중",
    Availability.UNAVAILABLE: "확보 어려움",
}


@dataclass(frozen=True)
class ExecutionInput:
    """실행 조건. 같은 merge_group 질문들이 한 번만 입력해 함께 쓴다."""

    collect_items: tuple[str, ...] = ()
    availability: Availability | None = None
    owner: str = ""
    cycle: str = ""

    def pending_labels(self) -> list[str]:
        pending = []
        if not self.owner:
            pending.append("수집 담당자")
        if not self.cycle:
            pending.append("확인 주기")
        if self.availability is None:
            pending.append("자료 확보 여부")
        elif self.availability is not Availability.AVAILABLE:
            pending.append(f"자료 확보 협의 ({AVAILABILITY_LABELS[self.availability]})")
        return pending


@dataclass(frozen=True)
class Choice:
    question_key: str
    rule_id: str
    decision: Decision
    merge_group: str | None = None
    option_id: str | None = None
    modified_text: str | None = None
    reason: str = ""
    evidence_ids: tuple[str, ...] = ()
    needs_recheck: bool = False

    @property
    def changes_document(self) -> bool:
        return self.decision in (Decision.ADOPT, Decision.MODIFY)


@dataclass(frozen=True)
class ArchivedChoice:
    choice: Choice
    reason: str = "원안 변경으로 더 이상 해당하지 않음"


@dataclass
class ChoiceSet:
    choices: dict[str, Choice] = field(default_factory=dict)
    executions: dict[str, ExecutionInput] = field(default_factory=dict)
    archived: list[ArchivedChoice] = field(default_factory=list)

    def get(self, question_key: str) -> Choice | None:
        return self.choices.get(question_key)

    def put(self, choice: Choice) -> None:
        self.choices[choice.question_key] = choice

    def remove(self, question_key: str) -> Choice | None:
        return self.choices.pop(question_key, None)

    def execution_for(self, merge_group: str | None) -> ExecutionInput | None:
        return self.executions.get(merge_group) if merge_group else None

    def set_execution(self, merge_group: str, execution: ExecutionInput) -> None:
        self.executions[merge_group] = execution

    @property
    def needs_recheck_keys(self) -> tuple[str, ...]:
        return tuple(key for key, choice in self.choices.items() if choice.needs_recheck)
