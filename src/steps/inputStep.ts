// 1단계: 기획 입력 (워크플로우 S01)
import { findSido, sidoList } from "../data/regions";
import {
  DATA_STATUS_LABELS,
  GOAL_LABELS,
  INDICATOR_USE_LABELS,
  INDICATOR_USE_NOTES,
  METRIC_LABELS,
} from "../labels";
import { getState, replacePlan, samplePlan, startReview, updatePlan, emptyPlan } from "../state";
import type { DataStatus, GoalKey, IndicatorUse, MetricKey, PlanInput, RegionScope } from "../types";
import { esc, formatKrw } from "../ui/html";
import { isValid, validatePlan, type FieldKey } from "../validation";

// 규칙 표시 (checks.md 31번: 최종기획 기준)
const RULES = [
  { id: "R07", status: "implement", text: "성과지표가 금액·비중 목표와 맞는지, 두 지표의 방향 차이 확인" },
  { id: "R01", status: "basic", text: "목표와 쿠폰 사용처가 맞는지 확인" },
  { id: "R03", status: "basic", text: "대상과 성과 자료의 범위가 맞는지 확인" },
  { id: "R04", status: "basic", text: "사업 기간과 집계 주기가 맞는지 확인" },
  { id: "R05", status: "basic", text: "예산·사용처·정산 등 운영 조건 누락 표시" },
  { id: "R06", status: "example", text: "고액 소비 근거 — 분석 예시로 제시" },
  { id: "R02", status: "future", text: "업종 후보 — 지역 기준 확인 후 적용" },
] as const;

const RULE_STATUS_LABEL = {
  implement: "검토 구현",
  basic: "기본 검토",
  example: "분석 예시",
  future: "향후 기능",
} as const;

// 모든 입력을 건드리기 전에는 오류를 보여주지 않는다
let showErrors = false;

export function renderInputStep(root: HTMLElement) {
  showErrors = false;
  root.innerHTML = `
    <div class="layout-main-side">
      <form class="card card-lg" id="plan-form" novalidate>
        <div class="card-head">
          <div>
            <h1 class="title">기획 입력</h1>
            <p class="subtitle">입력한 내용만으로 검토합니다. 빈 값은 추측하지 않습니다.</p>
          </div>
          <div class="head-actions">
            <button type="button" class="btn btn-ghost" data-action="sample">예시 기획 채우기</button>
            <button type="button" class="btn btn-ghost" data-action="clear">모두 지우기</button>
          </div>
        </div>

        <div class="grid-fields">
          ${textField("name", "사업명", true, "예: 하반기 외국인 소비지원 쿠폰")}
          ${textField("target", "사업 대상", true, "예: 외국인 전체, 방한 관광객")}
        </div>

        <fieldset class="field" data-field="goals">
          <legend class="label">사업 목표 <span class="req">필수</span> <span class="hint">여러 개 선택 가능</span></legend>
          <div class="chips">
            ${(Object.keys(GOAL_LABELS) as GoalKey[])
              .map((k) => chipCheckbox("goals", k, GOAL_LABELS[k]))
              .join("")}
          </div>
          <input class="input other-input" name="goalOther" placeholder="기타 목표를 적어 주세요" hidden />
          <p class="note" data-note="goal-other" hidden>기타 목표에는 일부 검토만 적용됩니다.</p>
          <p class="error" data-error="goals"></p>
          <p class="error" data-error="goalOther"></p>
        </fieldset>

        <fieldset class="field" data-field="region">
          <legend class="label">지역 <span class="req">필수</span></legend>
          <div class="region-row">
            <div class="segmented" role="radiogroup">
              ${segRadio("regionLevel", "national", "전국")}
              ${segRadio("regionLevel", "sido", "시도")}
              ${segRadio("regionLevel", "sigungu", "시군구")}
            </div>
            <select class="input" name="sido" hidden>
              <option value="">시도 선택</option>
              ${sidoList.map((s) => `<option value="${s.code}">${esc(s.name)}</option>`).join("")}
            </select>
            <select class="input" name="sigungu" hidden></select>
          </div>
          <p class="note" data-note="region"></p>
          <p class="error" data-error="region"></p>
        </fieldset>

        <div class="grid-fields">
          <fieldset class="field" data-field="period">
            <legend class="label">사업 기간 <span class="req">필수</span></legend>
            <div class="period-row">
              <input class="input" type="date" name="periodStart" aria-label="시작일" />
              <span class="muted">~</span>
              <input class="input" type="date" name="periodEnd" aria-label="종료일" />
            </div>
            <p class="error" data-error="period"></p>
          </fieldset>

          <fieldset class="field" data-field="budget">
            <legend class="label">예산 <span class="opt">선택</span></legend>
            <div class="budget-row">
              <input class="input" type="text" inputmode="numeric" name="budgetKrw" placeholder="원 단위 금액" />
              <label class="check"><input type="checkbox" name="budgetUndecided" /> 미정</label>
            </div>
            <p class="note" data-note="budget"></p>
            <p class="error" data-error="budget"></p>
          </fieldset>
        </div>

        <div class="grid-fields">
          ${textField("usagePlace", "쿠폰 사용처", false, "예: 관내 참여 점포")}
          <label class="field">
            <span class="label">자료 확보 상태 <span class="opt">선택</span></span>
            <select class="input" name="dataStatus">
              <option value="">선택 안 함</option>
              ${(Object.keys(DATA_STATUS_LABELS) as DataStatus[])
                .map((k) => `<option value="${k}">${DATA_STATUS_LABELS[k]}</option>`)
                .join("")}
            </select>
          </label>
        </div>

        <div class="emphasis">
          <fieldset class="field" data-field="metrics">
            <legend class="label-strong"><span class="dot"></span>현재 성과지표 <span class="req">필수</span> <span class="hint">여러 개 선택 가능</span></legend>
            <div class="chips">
              ${(Object.keys(METRIC_LABELS) as MetricKey[])
                .map((k) => chipCheckbox("metrics", k, METRIC_LABELS[k]))
                .join("")}
            </div>
            <input class="input other-input" name="metricOther" placeholder="기타 지표를 적어 주세요" hidden />
            <p class="error" data-error="metrics"></p>
            <p class="error" data-error="metricOther"></p>
          </fieldset>

          <fieldset class="field" data-field="indicatorUse">
            <legend class="label-strong">이 지표를 어떻게 쓰나요? <span class="req">필수</span></legend>
            <div class="chips">
              ${(Object.keys(INDICATOR_USE_LABELS) as IndicatorUse[])
                .map((k) => chipRadio("indicatorUse", k, INDICATOR_USE_LABELS[k]))
                .join("")}
            </div>
            <p class="note" data-note="indicatorUse"></p>
            <p class="error" data-error="indicatorUse"></p>
          </fieldset>
        </div>

        <label class="field">
          <span class="label">변경 불가 조건 <span class="opt">선택</span></span>
          <textarea class="input" name="fixedConditions" rows="3" placeholder="예: 지원 금액은 1인 1만원으로 고정, 사업 기간 변경 불가"></textarea>
        </label>

        <div class="form-foot">
          <p class="muted small">작업 내용은 이 화면이 열린 동안만 유지됩니다. 새로고침하면 초기화됩니다.</p>
          <button type="submit" class="btn btn-primary">검토 시작 →</button>
        </div>
      </form>

      <aside class="side">
        <div class="card">
          <h2 class="side-title">입력 상태</h2>
          <div id="input-summary"></div>
        </div>
        <div class="card">
          <h2 class="side-title">검토 예정 규칙</h2>
          <div class="rule-list">
            ${RULES.map(
              (r) => `
              <div class="rule rule-${r.status}">
                <div class="rule-id">${r.id} · ${RULE_STATUS_LABEL[r.status]}</div>
                <div class="rule-text">${r.text}</div>
              </div>`,
            ).join("")}
          </div>
          <p class="side-foot">‘문제없음’과 ‘검토하지 않음’을 구분해 결과 화면에 표시합니다.</p>
        </div>
      </aside>
    </div>
  `;

  const form = root.querySelector<HTMLFormElement>("#plan-form")!;
  fillForm(form, getState().plan);
  syncDerived(form);

  form.addEventListener("input", () => {
    onFormChange(form);
    syncDerived(form);
  });
  form.addEventListener("change", (e) => {
    const target = e.target as HTMLElement;
    if (target instanceof HTMLInputElement && target.name === "regionLevel") {
      const plan = getState().plan;
      const level = target.value as RegionScope["level"];
      const sidoCode = plan.region && plan.region.level !== "national" ? plan.region.sidoCode : "";
      updatePlan({ region: makeRegion(level, sidoCode, "") });
      fillForm(form, getState().plan);
    } else if (target instanceof HTMLSelectElement && target.name === "sido") {
      const plan = getState().plan;
      const level = plan.region?.level ?? "sido";
      updatePlan({ region: makeRegion(level, target.value, "") });
      fillForm(form, getState().plan);
    } else {
      onFormChange(form);
    }
    syncDerived(form);
  });

  form.addEventListener("click", (e) => {
    const action = (e.target as HTMLElement).closest<HTMLElement>("[data-action]")?.dataset.action;
    if (action === "sample") {
      replacePlan(samplePlan());
      fillForm(form, getState().plan);
      syncDerived(form);
    } else if (action === "clear") {
      replacePlan(emptyPlan());
      showErrors = false;
      fillForm(form, getState().plan);
      syncDerived(form);
    }
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const result = validatePlan(getState().plan);
    if (!isValid(result)) {
      showErrors = true;
      syncDerived(form);
      form.querySelector<HTMLElement>(".error:not(:empty)")?.closest(".field")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      return;
    }
    startReview();
  });
}

function textField(name: string, label: string, required: boolean, placeholder: string): string {
  return `
    <label class="field" data-field="${name}">
      <span class="label">${label} ${required ? '<span class="req">필수</span>' : '<span class="opt">선택</span>'}</span>
      <input class="input" type="text" name="${name}" placeholder="${esc(placeholder)}" />
      <span class="error" data-error="${name}"></span>
    </label>`;
}

function chipCheckbox(name: string, value: string, label: string): string {
  return `<label class="chip"><input type="checkbox" name="${name}" value="${value}" /><span>${label}</span></label>`;
}

function chipRadio(name: string, value: string, label: string): string {
  return `<label class="chip"><input type="radio" name="${name}" value="${value}" /><span>${label}</span></label>`;
}

function segRadio(name: string, value: string, label: string): string {
  return `<label class="seg"><input type="radio" name="${name}" value="${value}" /><span>${label}</span></label>`;
}

function makeRegion(level: RegionScope["level"], sidoCode: string, sigunguCode: string): RegionScope {
  if (level === "national") return { level };
  if (level === "sido") return { level, sidoCode };
  return { level, sidoCode, sigunguCode };
}

// 상태 → 폼
function fillForm(form: HTMLFormElement, plan: PlanInput) {
  const el = form.elements;
  const input = (name: string) => el.namedItem(name) as HTMLInputElement;

  input("name").value = plan.name;
  input("target").value = plan.target;
  input("goalOther").value = plan.goalOther;
  input("periodStart").value = plan.periodStart;
  input("periodEnd").value = plan.periodEnd;
  input("usagePlace").value = plan.usagePlace;
  input("metricOther").value = plan.metricOther;
  (el.namedItem("fixedConditions") as HTMLTextAreaElement).value = plan.fixedConditions;
  (el.namedItem("dataStatus") as HTMLSelectElement).value = plan.dataStatus ?? "";

  for (const box of form.querySelectorAll<HTMLInputElement>('input[name="goals"]'))
    box.checked = plan.goals.includes(box.value as GoalKey);
  for (const box of form.querySelectorAll<HTMLInputElement>('input[name="metrics"]'))
    box.checked = plan.metrics.includes(box.value as MetricKey);
  for (const radio of form.querySelectorAll<HTMLInputElement>('input[name="indicatorUse"]'))
    radio.checked = plan.indicatorUse === radio.value;

  input("budgetUndecided").checked = plan.budget.status === "undecided";
  // 숫자가 아닌 금액은 사용자가 고칠 수 있도록 입력칸의 글자를 그대로 둔다
  if (!(plan.budget.status === "amount" && Number.isNaN(plan.budget.krw)))
    input("budgetKrw").value = plan.budget.status === "amount" ? String(plan.budget.krw) : "";

  for (const radio of form.querySelectorAll<HTMLInputElement>('input[name="regionLevel"]'))
    radio.checked = plan.region?.level === radio.value;

  const sidoSelect = el.namedItem("sido") as HTMLSelectElement;
  const sigunguSelect = el.namedItem("sigungu") as HTMLSelectElement;
  const region = plan.region;
  sidoSelect.hidden = !region || region.level === "national";
  sigunguSelect.hidden = !region || region.level !== "sigungu";
  sidoSelect.value = region && region.level !== "national" ? region.sidoCode : "";

  if (region?.level === "sigungu") {
    const sido = findSido(region.sidoCode);
    sigunguSelect.innerHTML =
      `<option value="">${sido ? "시군구 선택" : "시도를 먼저 선택"}</option>` +
      (sido?.sigungu.map((g) => `<option value="${g.code}">${esc(g.name)}</option>`).join("") ?? "");
    sigunguSelect.disabled = !sido || sido.sigungu.length === 0;
    if (sido && sido.sigungu.length === 0)
      sigunguSelect.innerHTML = `<option value="">시군구 없음 (시도 단위 선택)</option>`;
    sigunguSelect.value = region.sigunguCode;
  }
}

// 폼 → 상태
function onFormChange(form: HTMLFormElement) {
  const el = form.elements;
  const value = (name: string) => (el.namedItem(name) as HTMLInputElement).value;
  const checked = (name: string) =>
    [...form.querySelectorAll<HTMLInputElement>(`input[name="${name}"]:checked`)].map((b) => b.value);

  const undecided = (el.namedItem("budgetUndecided") as HTMLInputElement).checked;
  const krwInput = el.namedItem("budgetKrw") as HTMLInputElement;
  krwInput.disabled = undecided;
  const krwText = krwInput.value.replaceAll(",", "").trim();
  const budget: PlanInput["budget"] = undecided
    ? { status: "undecided" }
    : krwText === ""
      ? { status: "unset" }
      : { status: "amount", krw: /^\d+$/.test(krwText) ? Number(krwText) : Number.NaN };

  const plan = getState().plan;
  const region = plan.region;
  const sigunguCode = value("sigungu");

  updatePlan({
    name: value("name"),
    target: value("target"),
    goals: checked("goals") as GoalKey[],
    goalOther: value("goalOther"),
    periodStart: value("periodStart"),
    periodEnd: value("periodEnd"),
    budget,
    usagePlace: value("usagePlace"),
    dataStatus: (value("dataStatus") || null) as DataStatus | null,
    metrics: checked("metrics") as MetricKey[],
    metricOther: value("metricOther"),
    indicatorUse: (checked("indicatorUse")[0] ?? null) as IndicatorUse | null,
    fixedConditions: (el.namedItem("fixedConditions") as HTMLTextAreaElement).value,
    region: region?.level === "sigungu" ? { ...region, sigunguCode } : region,
  });
}

// 입력값에 따라 달라지는 표시 (기타 입력칸, 안내 문구, 오류, 요약)
function syncDerived(form: HTMLFormElement) {
  const plan = getState().plan;
  const result = validatePlan(plan);

  (form.elements.namedItem("goalOther") as HTMLInputElement).hidden = !plan.goals.includes("other");
  form.querySelector<HTMLElement>('[data-note="goal-other"]')!.hidden = !plan.goals.includes("other");
  (form.elements.namedItem("metricOther") as HTMLInputElement).hidden = !plan.metrics.includes("other");
  (form.elements.namedItem("budgetKrw") as HTMLInputElement).disabled = plan.budget.status === "undecided";

  const regionNote = form.querySelector<HTMLElement>('[data-note="region"]')!;
  regionNote.textContent =
    plan.region && plan.region.level !== "national"
      ? "카드 소비 근거는 전국 자료부터 제공합니다. 선택한 지역의 진단이 아니라 전국 참고 자료로 표시됩니다."
      : "";

  const budgetNote = form.querySelector<HTMLElement>('[data-note="budget"]')!;
  budgetNote.textContent =
    plan.budget.status === "amount" && Number.isInteger(plan.budget.krw)
      ? formatKrw(plan.budget.krw)
      : plan.budget.status === "undecided"
        ? "미정은 0원과 다르게 기록되며 기획안에 ‘추가 확정 필요’로 남습니다."
        : "";

  form.querySelector<HTMLElement>('[data-note="indicatorUse"]')!.textContent = plan.indicatorUse
    ? INDICATOR_USE_NOTES[plan.indicatorUse]
    : "";

  for (const node of form.querySelectorAll<HTMLElement>("[data-error]")) {
    const key = node.dataset.error as FieldKey;
    const message = showErrors ? (result.errors[key] ?? "") : "";
    node.textContent = message;
    node.closest(".field")?.classList.toggle("has-error", Boolean(message));
  }

  renderSummary(result.errors, result.pending);
}

function renderSummary(errors: Partial<Record<FieldKey, string>>, pending: string[]) {
  const box = document.querySelector<HTMLElement>("#input-summary");
  if (!box) return;
  const missing = Object.keys(errors).length;
  box.innerHTML = `
    <div class="summary-row">
      <span>필수 항목</span>
      <b class="${missing ? "text-warn" : "text-ok"}">${missing ? `${missing}개 확인 필요` : "모두 입력됨"}</b>
    </div>
    <div class="summary-row">
      <span>추가 확정 필요로 남을 항목</span>
      <b>${pending.length}개</b>
    </div>
    ${pending.length ? `<div class="pending-list">${pending.map((p) => `<span class="badge-warn">${esc(p)}</span>`).join("")}</div>` : ""}
  `;
}
