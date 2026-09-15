// 아직 구현하지 않은 단계의 임시 화면
import { regionLabel } from "../data/regions";
import { GOAL_LABELS, INDICATOR_USE_LABELS, METRIC_LABELS, STEP_LABELS } from "../labels";
import { getState, goToStep } from "../state";
import type { StepIndex } from "../types";
import { esc } from "../ui/html";

export function renderPlaceholderStep(root: HTMLElement, step: StepIndex) {
  const { original, changedSinceReview } = getState();
  const summary = original
    ? `
      <dl class="kv">
        <dt>사업명</dt><dd>${esc(original.name)}</dd>
        <dt>목표</dt><dd>${original.goals.map((g) => (g === "other" ? esc(original.goalOther) : GOAL_LABELS[g])).join(", ")}</dd>
        <dt>지역</dt><dd>${esc(regionLabel(original.region))}</dd>
        <dt>성과지표</dt><dd>${original.metrics.map((m) => (m === "other" ? esc(original.metricOther) : METRIC_LABELS[m])).join(", ")}</dd>
        <dt>지표 용도</dt><dd>${original.indicatorUse ? INDICATOR_USE_LABELS[original.indicatorUse] : ""}</dd>
      </dl>`
    : "";

  root.innerHTML = `
    <div class="card card-lg">
      <h1 class="title">${STEP_LABELS[step]}</h1>
      <p class="subtitle">다음 작업에서 구현할 화면입니다.</p>
      ${changedSinceReview ? `<p class="badge-warn inline">원안 보관 후 입력이 바뀌었습니다. 검토를 다시 시작해 주세요.</p>` : ""}
      <h2 class="side-title mt">보관된 원안</h2>
      ${summary}
      <div class="form-foot">
        <button type="button" class="btn btn-ghost" data-back>← 기획 입력으로</button>
      </div>
    </div>`;

  root.querySelector("[data-back]")!.addEventListener("click", () => goToStep(0));
}
