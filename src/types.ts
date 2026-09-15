// 사용자가 입력하는 기획 원안의 형태. 워크플로우 3장 입력폼 최소 항목 기준.

export type GoalKey = "foreign_amount" | "foreign_share" | "store_usage" | "other";
export type MetricKey = "foreign_share" | "foreign_amount" | "coupon_usage" | "other";
export type IndicatorUse = "direct" | "reference" | "unknown";
export type DataStatus = "secured" | "negotiating" | "undecided";

export type RegionScope =
  | { level: "national" }
  | { level: "sido"; sidoCode: string }
  | { level: "sigungu"; sidoCode: string; sigunguCode: string };

// 미입력(unset), 미정(undecided), 금액(amount)을 구분한다. 0원은 amount다.
export type Budget =
  | { status: "unset" }
  | { status: "undecided" }
  | { status: "amount"; krw: number };

export interface PlanInput {
  name: string;
  goals: GoalKey[];
  goalOther: string;
  target: string;
  region: RegionScope | null;
  periodStart: string; // YYYY-MM-DD
  periodEnd: string;
  budget: Budget;
  usagePlace: string;
  metrics: MetricKey[];
  metricOther: string;
  indicatorUse: IndicatorUse | null;
  dataStatus: DataStatus | null;
  fixedConditions: string;
}

export type StepIndex = 0 | 1 | 2 | 3 | 4;
