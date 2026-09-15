import "./style.css";
import { STEP_LABELS } from "./labels";
import { getState, goToStep, resetAll, subscribe } from "./state";
import { renderInputStep } from "./steps/inputStep";
import { renderPlaceholderStep } from "./steps/placeholderStep";
import type { StepIndex } from "./types";

const app = document.querySelector<HTMLDivElement>("#app")!;

app.innerHTML = `
  <header class="topbar">
    <div class="topbar-inner">
      <div class="brand"><span class="brand-mark"></span><span>소비 시그널 정책맵</span></div>
      <span class="tag-mono" id="data-kind">시연용 합성 수치</span>
      <span class="spacer"></span>
      <button type="button" class="btn btn-ghost" id="reset">처음으로</button>
    </div>
    <nav class="rail" id="rail"></nav>
  </header>
  <main class="page" id="page"></main>
`;

const rail = app.querySelector<HTMLElement>("#rail")!;
const page = app.querySelector<HTMLElement>("#page")!;
let renderedStep: StepIndex | null = null;

function renderRail() {
  const { step, original } = getState();
  rail.innerHTML = STEP_LABELS.map((label, i) => {
    // 원안을 보관하기 전에는 기획 입력만 열 수 있다
    const locked = i > 0 && !original;
    const cls = i === step ? "active" : i < step ? "done" : "";
    return `
      <button type="button" class="rail-item ${cls}" data-step="${i}" ${locked ? "disabled" : ""}>
        <span class="rail-num">${i < step ? "✓" : i + 1}</span>
        <span>${label}</span>
      </button>`;
  }).join("");
}

function renderPage() {
  const { step } = getState();
  // 입력 중 포커스를 잃지 않도록 단계가 바뀔 때만 화면을 다시 그린다
  if (step === renderedStep) return;
  renderedStep = step;
  if (step === 0) renderInputStep(page);
  else renderPlaceholderStep(page, step);
  window.scrollTo({ top: 0 });
}

rail.addEventListener("click", (e) => {
  const item = (e.target as HTMLElement).closest<HTMLButtonElement>("[data-step]");
  if (item && !item.disabled) goToStep(Number(item.dataset.step) as StepIndex);
});

app.querySelector("#reset")!.addEventListener("click", () => {
  renderedStep = null;
  resetAll();
});

subscribe(() => {
  renderRail();
  renderPage();
});

renderRail();
renderPage();
