"""검토 규칙 실행. 같은 입력이면 항상 같은 결과를 낸다 (난수·시간 사용 금지)."""

from __future__ import annotations

from dataclasses import replace

from ..evidence.loader import LoadResult
from ..plan.models import PlanInput
from . import basic_checks, r07_indicator
from .context import region_note, scope_label, select_main_record
from .outcome import NoFinding, ReviewOutcome, ReviewResult, not_reviewed_from
from .rules import RuleInfo, load_rule_catalog, rules_by_id  # noqa: F401  (rules_by_id는 run_review에서 사용)

# 화면에 보여줄 순서: 성과지표 → 대상 → 기간 → 목표·사용처 → 운영 조건
RUN_ORDER = ("R07", "R03", "R04", "R01", "R05")


def check_rule_functions() -> None:
    """실행해야 하는 규칙에 코드가 있는지 확인한다 (JSON과 코드가 어긋나지 않게).

    이 모듈을 불러올 때 한 번 실행한다. 화면을 여는 순간이 아니라 서버가 시작할 때 멈추게 하려는 것이다.
    """
    missing = [
        rule.id
        for rule in load_rule_catalog()
        if rule.scope in ("implement", "basic") and rule.id not in RUN_ORDER
    ]
    if missing:
        raise ValueError(f"실행 함수가 없는 규칙: {', '.join(missing)} (review_rules.json과 engine.RUN_ORDER 확인)")


def _with_related(outcomes: list[ReviewOutcome]) -> tuple[ReviewOutcome, ...]:
    """같은 merge_group 질문끼리 서로를 가리킨다. 카드를 합치지는 않는다 (3검토질문계획 결정 ④)."""
    result = []
    for outcome in outcomes:
        related = (
            tuple(
                other.rule_id
                for other in outcomes
                if other is not outcome and other.merge_group == outcome.merge_group and other.kind == "question"
            )
            if outcome.merge_group and outcome.kind == "question"
            else ()
        )
        result.append(outcome if not related else replace(outcome, related_rule_ids=related))
    return tuple(result)


def _run_rule(
    rule: RuleInfo, plan: PlanInput, result: LoadResult | None
) -> ReviewOutcome | None:
    if rule.id == "R07":
        file = result.file if result else None
        record = select_main_record(file) if file else None
        return r07_indicator.run(
            rule,
            plan,
            file,
            record,
            scope_label=scope_label(record),
            region_note=region_note(plan),
        )
    return basic_checks.RUNNERS[rule.id](rule, plan)


def run_review(plan: PlanInput, evidence: LoadResult | None) -> ReviewResult:
    rules = rules_by_id()

    outcomes: list[ReviewOutcome] = []
    no_finding: list[NoFinding] = []
    for rule_id in RUN_ORDER:
        rule = rules[rule_id]
        outcome = _run_rule(rule, plan, evidence)
        if outcome is None:
            # 조건을 확인했지만 물을 것이 없음 ("검토하지 않음"과 구분)
            no_finding.append(NoFinding(rule.id, rule.title))
        else:
            outcomes.append(outcome)

    not_reviewed = tuple(
        not_reviewed_from(rule) for rule in load_rule_catalog() if rule.scope in ("example", "future")
    )

    record = select_main_record(evidence.file) if evidence else None
    return ReviewResult(
        outcomes=_with_related(outcomes),
        no_finding=tuple(no_finding),
        not_reviewed=not_reviewed,
        evidence_id=record.evidence_id if record else None,
    )


# 규칙 파일과 코드가 어긋나면 화면을 여는 순간이 아니라 서버가 시작할 때 멈춘다
check_rule_functions()
