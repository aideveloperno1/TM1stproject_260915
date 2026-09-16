"""원안 + 담당자 선택 → 보완 기획안 구조 (워크플로우 S04).

AI를 쓰지 않고 확인된 값만 양식에 채운다. 선택하지 않은 항목은 원안을 그대로 둔다.
"""

from __future__ import annotations

from datetime import date

from ..choices.models import AVAILABILITY_LABELS, Choice, ChoiceSet, Decision
from ..choices.selection import blocking_reasons, pending_from_choices
from ..evidence.loader import LoadResult
from ..formatting import period_label
from ..labels import DECISION_LABELS_FOR_DOCUMENT
from ..plan.models import Goal, PlanInput
from ..plan.validation import validate_plan
from ..review.context import scope_label, select_main_record
from ..review.outcome import ReviewOutcome, ReviewResult
from ..review.rules import OptionSpec
from .describe import describe_plan, goal_labels, metric_labels
from .models import (
    PENDING_MARK,
    Change,
    DocumentBlocked,
    EvidenceRef,
    Line,
    PlanDocument,
    RequestDraft,
    Section,
)

DATA_KIND_LABELS = {"synthetic": "시연용 합성 수치", "real": "실제 분석 자료"}


def _values(plan: PlanInput, choice: Choice, choice_set: ChoiceSet) -> dict[str, str]:
    execution = choice_set.execution_for(choice.merge_group)
    availability = (
        AVAILABILITY_LABELS[execution.availability]
        if execution and execution.availability is not None
        else PENDING_MARK
    )
    return {
        "collect_items": ", ".join(execution.collect_items) if execution and execution.collect_items else PENDING_MARK,
        "owner": execution.owner if execution and execution.owner else PENDING_MARK,
        "cycle": execution.cycle if execution and execution.cycle else PENDING_MARK,
        "availability": availability,
        "usage_place": plan.usage_place or PENDING_MARK,
        "target": plan.target or PENDING_MARK,
        "goals": goal_labels(plan),
        "goals_without_store_usage": goal_labels(plan, exclude=Goal.STORE_USAGE),
        "metrics": metric_labels(plan),
    }


def _option_lines(option: OptionSpec, choice: Choice, values: dict[str, str]) -> list[str]:
    if choice.decision is Decision.MODIFY and choice.modified_text:
        # 담당자가 고친 문장이 대안 문장을 대체한다 (5보완기획안계획 결정 ③)
        return [choice.modified_text]
    return [line.format(**values) for line in option.document.lines] if option.document else []


def _apply_choice(
    sections: dict[int, Section],
    plan: PlanInput,
    choice: Choice,
    choice_set: ChoiceSet,
    outcome: ReviewOutcome,
    changes: list[Change],
) -> None:
    option = outcome.option(choice.option_id) if choice.option_id else None
    if option is None or option.document is None:
        return

    document = option.document
    section = sections[document.section]
    values = _values(plan, choice, choice_set)
    lines = _option_lines(option, choice, values)
    decision_label = DECISION_LABELS_FOR_DOCUMENT[choice.decision]

    for index, text in enumerate(lines):
        change_id = f"{choice.rule_id}-{option.id}-{index + 1}"
        replace_at = section.find(document.replace_key) if document.mode == "replace" and index == 0 else None

        if replace_at is not None:
            before = section.lines[replace_at].text
            section.lines[replace_at] = Line(text, key=document.replace_key, state="changed", change_id=change_id, evidence_ids=choice.evidence_ids)
        else:
            before = None
            if any(line.text == text for line in section.lines):
                continue  # 같은 장에 같은 문장은 한 번만 (대안을 여러 개 채택한 경우)
            section.lines.append(Line(text, state="added", change_id=change_id, evidence_ids=choice.evidence_ids))

        changes.append(
            Change(
                change_id=change_id,
                section=document.section,
                before=before,
                after=text,
                rule_id=choice.rule_id,
                option_id=option.id,
                decision_label=decision_label,
                evidence_ids=choice.evidence_ids,
                modified=choice.decision is Decision.MODIFY,
            )
        )


def _auto_records(result: ReviewResult) -> list[str]:
    """보류·추가 확정 필요 결과는 선택 없이 8장에 기록한다 (4보완선택계획 결정 ⑤)."""
    records = []
    for outcome in result.outcomes:
        if outcome.kind == "held":
            records.append(f"{outcome.rule_id} {outcome.title}: {outcome.message}")
    return records


def _evidence_refs(result: ReviewResult, evidence: LoadResult) -> tuple[EvidenceRef, ...]:
    used = {evidence_id for outcome in result.outcomes for evidence_id in outcome.evidence_ids}
    refs = []
    for record in evidence.file.records:
        if record.evidence_id not in used:
            continue
        refs.append(
            EvidenceRef(
                evidence_id=record.evidence_id,
                data_kind=record.data_kind,
                dataset_version=evidence.file.dataset_version,
                scope_label=scope_label(record) or "",
                period_label=period_label(record.scope.period_start, record.scope.period_end),
                limitations=record.limitations,
            )
        )
    return tuple(refs)


def _request_draft(plan: PlanInput, choice_set: ChoiceSet, result: ReviewResult) -> RequestDraft | None:
    wants_request = any(
        (outcome := result.by_key(choice.question_key))
        and (option := outcome.option(choice.option_id or ""))
        and option.document
        and option.document.appendix == "request"
        for choice in choice_set.choices.values()
        if choice.changes_document and choice.option_id
    )
    if not wants_request:
        return None
    return RequestDraft(
        purpose="참여 점포의 외국인 결제 실적 확인",
        targets=f"참여 점포 목록 {PENDING_MARK}",
        period=f"{plan.period_start} ~ {plan.period_end}",
        metrics="참여 점포 외국인 결제금액·건수, 사업 전후 비교",
        to_confirm=(
            "점포 식별 가능 여부",
            "자료 제공·계약 조건과 비용",
            "참여자 결제와 점포 전체 결제의 차이",
        ),
    )


def build_document(
    plan: PlanInput,
    result: ReviewResult,
    choice_set: ChoiceSet,
    evidence: LoadResult,
    today: date,
) -> PlanDocument | DocumentBlocked:
    blocked = blocking_reasons(result, choice_set)
    if blocked:
        return DocumentBlocked(tuple(blocked))

    sections = {section.number: section for section in describe_plan(plan)}
    changes: list[Change] = []
    for outcome in result.outcomes:
        choice = choice_set.get(outcome.question_key)
        if choice is not None and choice.changes_document:
            _apply_choice(sections, plan, choice, choice_set, outcome, changes)

    pending = [*validate_plan(plan).pending, *pending_from_choices(choice_set, result), *_auto_records(result)]
    section8 = sections[8]
    for item in dict.fromkeys(pending):  # 중복 제거, 순서 유지
        if not any(line.text.startswith(item) for line in section8.lines):
            section8.lines.append(Line(f"{item} {PENDING_MARK}", state="pending"))

    data_kind = evidence.file.data_kind
    return PlanDocument(
        title=f"보완 기획안 — {plan.name}" if plan.name else "보완 기획안",
        created_on=today.isoformat(),
        data_notice=f"{DATA_KIND_LABELS[data_kind]} · 자료 버전 {evidence.file.dataset_version}",
        sections=tuple(sections[number] for number in sorted(sections)),
        changes=tuple(changes),
        evidence_refs=_evidence_refs(result, evidence),
        pending=tuple(dict.fromkeys(pending)),
        request_draft=_request_draft(plan, choice_set, result),
    )
