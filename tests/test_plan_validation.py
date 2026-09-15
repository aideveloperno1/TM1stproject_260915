from helpers import VALID_FORM, parse

from policy_signal_map.plan.models import BudgetStatus, Goal, sample_plan
from policy_signal_map.plan.validation import validate_plan


def test_sample_plan_is_valid():
    assert validate_plan(sample_plan()).ok


def test_empty_plan_reports_seven_required_fields():
    result = validate_plan(parse({}))
    assert set(result.errors) == {"name", "goals", "target", "region", "period", "metrics", "indicator_use"}


def test_budget_distinguishes_unset_undecided_and_zero():
    assert parse({}).budget.status is BudgetStatus.UNSET
    assert parse({"budget_undecided": "1", "budget_krw": "5000"}).budget.status is BudgetStatus.UNDECIDED
    zero = parse({"budget_krw": "0"}).budget
    assert zero.status is BudgetStatus.AMOUNT and zero.krw == 0
    assert parse({"budget_krw": "1,000,000"}).budget.krw == 1_000_000


def test_invalid_budget_text_is_error_not_zero():
    plan = parse({**VALID_FORM, "budget_krw": "십만원"})
    assert plan.budget.krw is None
    assert "budget" in validate_plan(plan).errors


def test_pending_items_for_empty_optional_fields():
    pending = validate_plan(parse(VALID_FORM)).pending
    assert pending == ["예산 (미입력)", "쿠폰 사용처", "자료 확보 상태"]


def test_other_goal_requires_description():
    plan = parse({**VALID_FORM, "goals": ["other"]})
    assert plan.goals == [Goal.OTHER]
    assert "goal_other" in validate_plan(plan).errors


def test_unknown_choices_are_dropped():
    plan = parse({**VALID_FORM, "goals": ["foreign_share", "hack"], "indicator_use": "x"})
    assert plan.goals == [Goal.FOREIGN_SHARE]
    assert plan.indicator_use is None


def test_unknown_region_is_rejected():
    plan = parse({**VALID_FORM, "sigungu": "9999999999"})
    assert "region" in validate_plan(plan).errors


def test_period_end_before_start():
    plan = parse({**VALID_FORM, "period_end": "2026-09-01"})
    assert validate_plan(plan).errors["period"] == "종료일이 시작일보다 빠릅니다."
