"""기본 검토 R01·R03·R04·R05와 이번 범위에서 검토하지 않는 R06·R02.

조건은 초안이며 docs/review_rules.md에서 데이터 담당과 확정한다.
사용자가 입력하지 않은 사실을 추정해 지적하지 않는다.
"""

from __future__ import annotations

from datetime import date

from ..plan.models import Goal, IndicatorUse, Metric, PlanInput
from ..plan.validation import validate_plan
from .outcome import ReviewOutcome
from .rules import RuleInfo

SHORT_PERIOD_DAYS = 31
TOURIST_WORDS = ("관광객", "방문객", "여행객")
CARD_METRICS = (Metric.FOREIGN_SHARE, Metric.FOREIGN_AMOUNT)


def _outcome(rule: RuleInfo, kind: str, message: str) -> ReviewOutcome:
    return ReviewOutcome(
        rule_id=rule.id,
        question_key=rule.id,
        merge_group=rule.merge_group,
        kind=kind,  # type: ignore[arg-type]
        title=rule.title,
        message=message,
        related_fields=rule.related_fields,
    )


def run_r01(rule: RuleInfo, plan: PlanInput) -> ReviewOutcome | None:
    """목표에 참여 상점 이용 확대가 있는데 사용처가 비어 있으면 묻는다."""
    if Goal.STORE_USAGE in plan.goals and not plan.usage_place:
        return _outcome(rule, "question", rule.message("question"))
    return None


def run_r03(rule: RuleInfo, plan: PlanInput) -> ReviewOutcome | None:
    """대상이 관광객인데 성과지표가 외국인 전체 카드 지표이면 묻는다 (최종기획서 5-2)."""
    target = plan.target
    if any(word in target for word in TOURIST_WORDS) and any(m in CARD_METRICS for m in plan.metrics):
        return _outcome(rule, "question", rule.message("question"))
    return None


def _period_days(plan: PlanInput) -> int | None:
    try:
        start, end = date.fromisoformat(plan.period_start), date.fromisoformat(plan.period_end)
    except ValueError:
        return None
    return (end - start).days + 1


def run_r04(rule: RuleInfo, plan: PlanInput) -> ReviewOutcome | None:
    """사업 기간이 한 달이 안 되는데 월 단위 카드 지표로 직접 평가하면 묻는다."""
    days = _period_days(plan)
    if days is None or days >= SHORT_PERIOD_DAYS:
        return None
    if plan.indicator_use is not IndicatorUse.DIRECT or not any(m in CARD_METRICS for m in plan.metrics):
        return None
    return _outcome(rule, "question", rule.message("question"))


def run_r05(rule: RuleInfo, plan: PlanInput) -> ReviewOutcome | None:
    """입력 검증의 '추가 확정 필요' 항목을 그대로 보여준다. 값을 추측해 채우지 않는다."""
    pending = validate_plan(plan).pending
    if not pending:
        return None
    return _outcome(rule, "pending", rule.message("pending", pending_list=", ".join(pending)))


RUNNERS = {"R01": run_r01, "R03": run_r03, "R04": run_r04, "R05": run_r05}
