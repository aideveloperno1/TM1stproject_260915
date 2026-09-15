"""검토 결과 형태.

서비스는 판정하지 않는다. 관측을 질문으로 전달하고 결정은 담당자가 한다 (최종기획서 1장).
'문제없음'(no_finding)과 '검토하지 않음'(not_reviewed)을 구분한다 (워크플로우 S02).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from .rules import OptionSpec, RuleInfo

OutcomeKind = Literal["question", "notice", "pending", "held", "not_reviewed"]


@dataclass(frozen=True)
class ReviewOutcome:
    rule_id: str
    # 4단계 선택이 참조하는 키. 같은 merge_group 질문끼리 추가 입력을 공유한다
    question_key: str
    kind: OutcomeKind
    title: str
    message: str
    why: str | None = None
    evidence_ids: tuple[str, ...] = ()
    scope_label: str | None = None
    region_note: str | None = None
    options: tuple[OptionSpec, ...] = ()
    related_fields: tuple[str, ...] = ()
    # 같은 자료를 묻는 다른 규칙 (3단계는 카드를 합치지 않고 서로를 가리킨다)
    related_rule_ids: tuple[str, ...] = ()
    # 문장 조립에 쓴 수치. 화면 표시용이며 LLM에는 넘기지 않는다
    observations: dict[str, Any] = field(default_factory=dict)

    @property
    def needs_choice(self) -> bool:
        return self.kind == "question"

    def to_llm_summary(self) -> dict[str, Any]:
        """C 단계용 요약. 금액·비중·구간 수 같은 수치를 넣지 않는다."""
        return {
            "rule_id": self.rule_id,
            "kind": self.kind,
            "title": self.title,
            "has_evidence": bool(self.evidence_ids),
            "scope_label": self.scope_label,
            "related_rule_ids": list(self.related_rule_ids),
        }


@dataclass(frozen=True)
class NotReviewed:
    rule_id: str
    title: str
    scope_label: str
    reason: str


@dataclass(frozen=True)
class NoFinding:
    rule_id: str
    title: str


@dataclass(frozen=True)
class ReviewResult:
    outcomes: tuple[ReviewOutcome, ...]
    # 조건을 확인했지만 물을 것이 없는 규칙 ("검토하지 않음"과 다름)
    no_finding: tuple[NoFinding, ...]
    not_reviewed: tuple[NotReviewed, ...]
    evidence_id: str | None

    @property
    def questions(self) -> tuple[ReviewOutcome, ...]:
        return tuple(o for o in self.outcomes if o.kind == "question")

    def by_key(self, question_key: str) -> ReviewOutcome | None:
        return next((o for o in self.outcomes if o.question_key == question_key), None)


def not_reviewed_from(rule: RuleInfo) -> NotReviewed:
    return NotReviewed(
        rule_id=rule.id,
        title=rule.title,
        scope_label=rule.scope_label,
        reason=rule.message("not_reviewed"),
    )
