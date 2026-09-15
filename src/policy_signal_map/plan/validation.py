from dataclasses import dataclass, field
from datetime import date

from .models import BudgetStatus, DataStatus, Goal, Metric, PlanInput, RegionLevel
from .regions import is_known_region


@dataclass
class ValidationResult:
    errors: dict[str, str] = field(default_factory=dict)
    # 선택 항목 중 비어 있어 기획안에 "추가 확정 필요"로 남을 항목
    pending: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def validate_plan(plan: PlanInput) -> ValidationResult:
    errors: dict[str, str] = {}

    if not plan.name:
        errors["name"] = "사업명을 입력해 주세요."

    if not plan.goals:
        errors["goals"] = "사업 목표를 하나 이상 골라 주세요."
    elif Goal.OTHER in plan.goals and not plan.goal_other:
        errors["goal_other"] = "기타 목표의 내용을 적어 주세요."

    if not plan.target:
        errors["target"] = "사업 대상을 입력해 주세요."

    region = plan.region
    if region is None:
        errors["region"] = "지역 범위를 골라 주세요."
    elif region.level is not RegionLevel.NATIONAL and not region.sido_code:
        errors["region"] = "시도를 골라 주세요."
    elif region.level is RegionLevel.SIGUNGU and not region.sigungu_code:
        errors["region"] = "시군구를 골라 주세요."
    elif not is_known_region(region):
        errors["region"] = "목록에 없는 지역입니다. 다시 골라 주세요."

    start, end = _parse_date(plan.period_start), _parse_date(plan.period_end)
    if not plan.period_start or not plan.period_end:
        errors["period"] = "시작일과 종료일을 모두 입력해 주세요."
    elif start is None or end is None:
        errors["period"] = "날짜 형식이 올바르지 않습니다."
    elif end < start:
        errors["period"] = "종료일이 시작일보다 빠릅니다."

    if plan.budget.status is BudgetStatus.AMOUNT and plan.budget.krw is None:
        errors["budget"] = "예산은 0 이상의 원 단위 정수로 입력해 주세요."

    if not plan.metrics:
        errors["metrics"] = "현재 성과지표를 하나 이상 골라 주세요."
    elif Metric.OTHER in plan.metrics and not plan.metric_other:
        errors["metric_other"] = "기타 지표의 내용을 적어 주세요."

    if plan.indicator_use is None:
        errors["indicator_use"] = "지표를 어떻게 쓰는지 골라 주세요."

    pending: list[str] = []
    if plan.budget.status is BudgetStatus.UNSET:
        pending.append("예산 (미입력)")
    elif plan.budget.status is BudgetStatus.UNDECIDED:
        pending.append("예산 (미정)")
    if not plan.usage_place:
        pending.append("쿠폰 사용처")
    if plan.data_status is None:
        pending.append("자료 확보 상태")
    elif plan.data_status is not DataStatus.SECURED:
        pending.append("성과 자료 확보")

    return ValidationResult(errors=errors, pending=pending)
