"""사용자가 입력하는 기획 원안의 형태. 워크플로우 3장 입력폼 최소 항목 기준."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Goal(StrEnum):
    FOREIGN_AMOUNT = "foreign_amount"
    FOREIGN_SHARE = "foreign_share"
    STORE_USAGE = "store_usage"
    OTHER = "other"


class Metric(StrEnum):
    FOREIGN_SHARE = "foreign_share"
    FOREIGN_AMOUNT = "foreign_amount"
    COUPON_USAGE = "coupon_usage"
    OTHER = "other"


class IndicatorUse(StrEnum):
    DIRECT = "direct"
    REFERENCE = "reference"
    UNKNOWN = "unknown"


class DataStatus(StrEnum):
    SECURED = "secured"
    NEGOTIATING = "negotiating"
    UNDECIDED = "undecided"


class RegionLevel(StrEnum):
    NATIONAL = "national"
    SIDO = "sido"
    SIGUNGU = "sigungu"


class BudgetStatus(StrEnum):
    UNSET = "unset"  # 입력하지 않음
    UNDECIDED = "undecided"  # 미정으로 표시함
    AMOUNT = "amount"  # 금액 입력 (0원 포함)


@dataclass
class Region:
    level: RegionLevel
    sido_code: str = ""
    sigungu_code: str = ""


@dataclass
class Budget:
    status: BudgetStatus = BudgetStatus.UNSET
    krw: int | None = None
    # 숫자로 읽지 못한 입력을 사용자가 고칠 수 있도록 원문을 남긴다
    raw: str = ""


@dataclass
class PlanInput:
    name: str = ""
    goals: list[Goal] = field(default_factory=list)
    goal_other: str = ""
    target: str = ""
    region: Region | None = None
    period_start: str = ""  # YYYY-MM-DD
    period_end: str = ""
    budget: Budget = field(default_factory=Budget)
    usage_place: str = ""
    metrics: list[Metric] = field(default_factory=list)
    metric_other: str = ""
    indicator_use: IndicatorUse | None = None
    data_status: DataStatus | None = None
    fixed_conditions: str = ""


def sample_plan() -> PlanInput:
    """공개 시연용 예시 기획. 최종기획서 4-1장의 첫 시험 기획."""
    return PlanInput(
        name="하반기 외국인 소비지원 쿠폰",
        goals=[Goal.FOREIGN_SHARE],
        target="외국인 전체",
        region=Region(RegionLevel.SIGUNGU, sido_code="5100000000", sigungu_code="5115000000"),
        period_start="2026-10-01",
        period_end="2026-12-31",
        budget=Budget(BudgetStatus.UNDECIDED),
        usage_place="관내 참여 점포",
        metrics=[Metric.FOREIGN_SHARE],
        indicator_use=IndicatorUse.DIRECT,
    )
