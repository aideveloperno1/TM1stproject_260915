import type { PlanInput } from "./types";

export type FieldKey =
  | "name"
  | "goals"
  | "goalOther"
  | "target"
  | "region"
  | "period"
  | "budget"
  | "metrics"
  | "metricOther"
  | "indicatorUse";

export interface ValidationResult {
  errors: Partial<Record<FieldKey, string>>;
  // 선택 항목 중 비어 있어 기획안에 "추가 확정 필요"로 남을 항목
  pending: string[];
}

export function validatePlan(plan: PlanInput): ValidationResult {
  const errors: ValidationResult["errors"] = {};

  if (!plan.name.trim()) errors.name = "사업명을 입력해 주세요.";

  if (plan.goals.length === 0) errors.goals = "사업 목표를 하나 이상 골라 주세요.";
  else if (plan.goals.includes("other") && !plan.goalOther.trim())
    errors.goalOther = "기타 목표의 내용을 적어 주세요.";

  if (!plan.target.trim()) errors.target = "사업 대상을 입력해 주세요.";

  if (!plan.region) errors.region = "지역 범위를 골라 주세요.";
  else if (plan.region.level !== "national" && !plan.region.sidoCode) errors.region = "시도를 골라 주세요.";
  else if (plan.region.level === "sigungu" && !plan.region.sigunguCode) errors.region = "시군구를 골라 주세요.";

  if (!plan.periodStart || !plan.periodEnd) errors.period = "시작일과 종료일을 모두 입력해 주세요.";
  else if (plan.periodEnd < plan.periodStart) errors.period = "종료일이 시작일보다 빠릅니다.";

  if (plan.budget.status === "amount" && (!Number.isInteger(plan.budget.krw) || plan.budget.krw < 0))
    errors.budget = "예산은 0 이상의 원 단위 정수로 입력해 주세요.";

  if (plan.metrics.length === 0) errors.metrics = "현재 성과지표를 하나 이상 골라 주세요.";
  else if (plan.metrics.includes("other") && !plan.metricOther.trim())
    errors.metricOther = "기타 지표의 내용을 적어 주세요.";

  if (!plan.indicatorUse) errors.indicatorUse = "지표를 어떻게 쓰는지 골라 주세요.";

  const pending: string[] = [];
  if (plan.budget.status === "unset") pending.push("예산 (미입력)");
  else if (plan.budget.status === "undecided") pending.push("예산 (미정)");
  if (!plan.usagePlace.trim()) pending.push("쿠폰 사용처");
  if (!plan.dataStatus) pending.push("자료 확보 상태");
  else if (plan.dataStatus !== "secured") pending.push("성과 자료 확보");

  return { errors, pending };
}

export function isValid(result: ValidationResult): boolean {
  return Object.keys(result.errors).length === 0;
}
