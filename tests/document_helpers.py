from datetime import date

from policy_signal_map.choices.models import ChoiceSet
from policy_signal_map.choices.selection import apply_choice
from policy_signal_map.config import DEFAULT_EVIDENCE_PATH
from policy_signal_map.document.builder import build_document
from policy_signal_map.evidence.loader import load_evidence
from policy_signal_map.plan.models import sample_plan
from policy_signal_map.review.engine import run_review

TODAY = date(2026, 9, 17)
EVIDENCE = load_evidence(DEFAULT_EVIDENCE_PATH)
ADOPT_A = {
    "decision": "adopt",
    "option_id": "A",
    "owner": "관광과 김담당",
    "cycle": "월 1회",
    "availability": "available",
}


def plan_with(**changes):
    plan = sample_plan()
    for key, value in changes.items():
        setattr(plan, key, value)
    return plan


def review_of(plan, evidence=EVIDENCE):
    return run_review(plan, evidence)


def choose(result, choice_set: ChoiceSet, rule_id: str, form: dict, collect_items=()) -> dict:
    outcome = next(o for o in result.outcomes if o.rule_id == rule_id)
    return apply_choice(choice_set, outcome, form, list(collect_items))


def document_for(plan, choice_set: ChoiceSet | None = None, evidence=EVIDENCE, today=TODAY):
    result = review_of(plan, evidence)
    return build_document(plan, result, choice_set or ChoiceSet(), evidence, today), result


def section_of(document, number: int):
    return next(section for section in document.sections if section.number == number)


def texts(document, number: int) -> list[str]:
    return [line.text for line in section_of(document, number).lines]
