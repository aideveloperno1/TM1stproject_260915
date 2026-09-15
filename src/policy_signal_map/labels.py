from .models import DataStatus, Goal, IndicatorUse, Metric

GOAL_LABELS: dict[Goal, str] = {
    Goal.FOREIGN_AMOUNT: "외국인 결제금액 확대",
    Goal.FOREIGN_SHARE: "외국인 결제 비중 확대",
    Goal.STORE_USAGE: "참여 상점 이용 확대",
    Goal.OTHER: "기타",
}

METRIC_LABELS: dict[Metric, str] = {
    Metric.FOREIGN_SHARE: "외국인 결제 비중",
    Metric.FOREIGN_AMOUNT: "외국인 결제금액",
    Metric.COUPON_USAGE: "쿠폰 사용·정산 실적",
    Metric.OTHER: "기타",
}

INDICATOR_USE_LABELS: dict[IndicatorUse, str] = {
    IndicatorUse.DIRECT: "사업 성과로 직접 평가",
    IndicatorUse.REFERENCE: "참고 현황",
    IndicatorUse.UNKNOWN: "아직 모름",
}

INDICATOR_USE_NOTES: dict[IndicatorUse, str] = {
    IndicatorUse.DIRECT: "직접 평가에 쓰면 지표가 사업 목표를 대표하는지 먼저 확인합니다.",
    IndicatorUse.REFERENCE: "참고 현황으로 쓰면 오류로 표시하지 않고, 해석 조건만 문서에 적도록 제안합니다.",
    IndicatorUse.UNKNOWN: "용도가 정해지지 않았다면 결론을 내지 않고 선택지만 함께 보여줍니다.",
}

DATA_STATUS_LABELS: dict[DataStatus, str] = {
    DataStatus.SECURED: "확보됨",
    DataStatus.NEGOTIATING: "협의 중",
    DataStatus.UNDECIDED: "미정",
}

STEP_LABELS = ["기획 입력", "근거 확인", "검토 질문", "보완 선택", "보완 기획안"]

# 검토 규칙 표시 (checks.md: 최종기획 기준)
RULES = [
    ("R07", "implement", "성과지표가 금액·비중 목표와 맞는지, 두 지표의 방향 차이 확인"),
    ("R01", "basic", "목표와 쿠폰 사용처가 맞는지 확인"),
    ("R03", "basic", "대상과 성과 자료의 범위가 맞는지 확인"),
    ("R04", "basic", "사업 기간과 집계 주기가 맞는지 확인"),
    ("R05", "basic", "예산·사용처·정산 등 운영 조건 누락 표시"),
    ("R06", "example", "고액 소비 근거 — 분석 예시로 제시"),
    ("R02", "future", "업종 후보 — 지역 기준 확인 후 적용"),
]

RULE_STATUS_LABELS = {
    "implement": "검토 구현",
    "basic": "기본 검토",
    "example": "분석 예시",
    "future": "향후 기능",
}
