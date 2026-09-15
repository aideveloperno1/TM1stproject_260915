// 작업 상태는 브라우저 화면이 열린 동안만 유지한다 (워크플로우 S01).
import type { PlanInput, StepIndex } from "./types";

export function emptyPlan(): PlanInput {
  return {
    name: "",
    goals: [],
    goalOther: "",
    target: "",
    region: null,
    periodStart: "",
    periodEnd: "",
    budget: { status: "unset" },
    usagePlace: "",
    metrics: [],
    metricOther: "",
    indicatorUse: null,
    dataStatus: null,
    fixedConditions: "",
  };
}

// 공개 시연용 예시 기획. 최종기획서 4-1장의 첫 시험 기획.
export function samplePlan(): PlanInput {
  return {
    name: "하반기 외국인 소비지원 쿠폰",
    goals: ["foreign_share"],
    goalOther: "",
    target: "외국인 전체",
    region: { level: "sigungu", sidoCode: "5100000000", sigunguCode: "5115000000" },
    periodStart: "2026-10-01",
    periodEnd: "2026-12-31",
    budget: { status: "undecided" },
    usagePlace: "관내 참여 점포",
    metrics: ["foreign_share"],
    metricOther: "",
    indicatorUse: "direct",
    dataStatus: null,
    fixedConditions: "",
  };
}

export interface AppState {
  step: StepIndex;
  // 사용자가 편집 중인 기획
  plan: PlanInput;
  // [검토 시작] 시점에 보관한 원안. 보완 기획안의 "변경 전" 기준이 된다.
  original: PlanInput | null;
  // 원안 보관 이후 입력이 바뀌었는지. 이후 단계의 선택을 재확인할 때 쓴다.
  changedSinceReview: boolean;
}

type Listener = (state: AppState) => void;

const state: AppState = {
  step: 0,
  plan: emptyPlan(),
  original: null,
  changedSinceReview: false,
};

const listeners = new Set<Listener>();

export function getState(): AppState {
  return state;
}

export function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function notify() {
  for (const listener of listeners) listener(state);
}

export function updatePlan(patch: Partial<PlanInput>) {
  Object.assign(state.plan, patch);
  if (state.original) state.changedSinceReview = true;
  notify();
}

export function replacePlan(plan: PlanInput) {
  state.plan = plan;
  if (state.original) state.changedSinceReview = true;
  notify();
}

export function startReview() {
  state.original = structuredClone(state.plan);
  state.changedSinceReview = false;
  state.step = 1;
  notify();
}

export function goToStep(step: StepIndex) {
  state.step = step;
  notify();
}

export function resetAll() {
  state.step = 0;
  state.plan = emptyPlan();
  state.original = null;
  state.changedSinceReview = false;
  notify();
}
