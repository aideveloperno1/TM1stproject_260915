"""선택지 한글 문구. 화면과 보완 기획안 문서가 함께 쓴다 (document/는 web/을 import할 수 없다)."""

from .plan.models import DataStatus, Goal, IndicatorUse, Metric

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
