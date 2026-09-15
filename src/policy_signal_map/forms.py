"""기획 입력 폼 값을 PlanInput으로 읽는다. 목록에 없는 선택값은 버린다."""

from collections.abc import Mapping, Sequence

from .models import (
    Budget,
    BudgetStatus,
    DataStatus,
    Goal,
    IndicatorUse,
    Metric,
    PlanInput,
    Region,
    RegionLevel,
)


def _one[E](enum: type[E], value: str | None) -> E | None:
    try:
        return enum(value)  # type: ignore[call-arg]
    except ValueError:
        return None


def _many[E](enum: type[E], values: Sequence[str]) -> list[E]:
    picked = [_one(enum, v) for v in values]
    # 순서를 유지하며 중복 제거
    return list(dict.fromkeys(p for p in picked if p is not None))


def parse_plan_form(single: Mapping[str, str], multi: Mapping[str, Sequence[str]]) -> PlanInput:
    def text(name: str) -> str:
        return single.get(name, "").strip()

    level = _one(RegionLevel, single.get("region_level"))
    region = None
    if level is RegionLevel.NATIONAL:
        region = Region(level)
    elif level is RegionLevel.SIDO:
        region = Region(level, sido_code=text("sido"))
    elif level is RegionLevel.SIGUNGU:
        region = Region(level, sido_code=text("sido"), sigungu_code=text("sigungu"))

    raw_krw = text("budget_krw").replace(",", "")
    if single.get("budget_undecided"):
        budget = Budget(BudgetStatus.UNDECIDED)
    elif raw_krw == "":
        budget = Budget(BudgetStatus.UNSET)
    elif raw_krw.isdigit():
        budget = Budget(BudgetStatus.AMOUNT, krw=int(raw_krw), raw=raw_krw)
    else:
        budget = Budget(BudgetStatus.AMOUNT, krw=None, raw=text("budget_krw"))

    return PlanInput(
        name=text("name"),
        goals=_many(Goal, multi.get("goals", [])),
        goal_other=text("goal_other"),
        target=text("target"),
        region=region,
        period_start=text("period_start"),
        period_end=text("period_end"),
        budget=budget,
        usage_place=text("usage_place"),
        metrics=_many(Metric, multi.get("metrics", [])),
        metric_other=text("metric_other"),
        indicator_use=_one(IndicatorUse, single.get("indicator_use")),
        data_status=_one(DataStatus, single.get("data_status")),
        fixed_conditions=text("fixed_conditions"),
    )
