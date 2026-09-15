import type { DataStatus, GoalKey, IndicatorUse, MetricKey } from "./types";

export const GOAL_LABELS: Record<GoalKey, string> = {
  foreign_amount: "외국인 결제금액 확대",
  foreign_share: "외국인 결제 비중 확대",
  store_usage: "참여 상점 이용 확대",
  other: "기타",
};

export const METRIC_LABELS: Record<MetricKey, string> = {
  foreign_share: "외국인 결제 비중",
  foreign_amount: "외국인 결제금액",
  coupon_usage: "쿠폰 사용·정산 실적",
  other: "기타",
};

export const INDICATOR_USE_LABELS: Record<IndicatorUse, string> = {
  direct: "사업 성과로 직접 평가",
  reference: "참고 현황",
  unknown: "아직 모름",
};

export const INDICATOR_USE_NOTES: Record<IndicatorUse, string> = {
  direct: "직접 평가에 쓰면 지표가 사업 목표를 대표하는지 먼저 확인합니다.",
  reference: "참고 현황으로 쓰면 오류로 표시하지 않고, 해석 조건만 문서에 적도록 제안합니다.",
  unknown: "용도가 정해지지 않았다면 결론을 내지 않고 선택지만 함께 보여줍니다.",
};

export const DATA_STATUS_LABELS: Record<DataStatus, string> = {
  secured: "확보됨",
  negotiating: "협의 중",
  undecided: "미정",
};

export const STEP_LABELS = ["기획 입력", "근거 확인", "검토 질문", "보완 선택", "보완 기획안"] as const;
