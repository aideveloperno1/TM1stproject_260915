// 기획 입력 화면의 즉시 반응 (서버 검증을 대신하지 않음)
(() => {
  const form = document.getElementById("plan-form");
  if (!form) return;
  const regions = JSON.parse(document.getElementById("regions-data").textContent).sido;

  // 기타 선택 시 내용 입력칸 표시
  form.addEventListener("change", (e) => {
    const t = e.target;
    const group = t.dataset?.toggleOther;
    if (group) {
      const otherChecked = form.querySelector(`[data-toggle-other="${group}"][value="other"]`).checked;
      form.querySelector(`[data-other="${group}"]`).hidden = !otherChecked;
    }
  });

  // 지역: 범위에 따라 시도·시군구 선택 표시, 시도에 맞춰 시군구 목록 갱신
  const sido = form.elements.namedItem("sido");
  const sigungu = form.elements.namedItem("sigungu");
  const regionNote = form.querySelector('[data-note="region"]');

  function level() {
    return form.querySelector('input[name="region_level"]:checked')?.value ?? "";
  }

  function fillSigungu() {
    const found = regions.find((s) => s.code === sido.value);
    const options = found?.sigungu ?? [];
    sigungu.replaceChildren(new Option(found ? (options.length ? "시군구 선택" : "시군구 없음 (시도 단위 선택)") : "시도를 먼저 선택", ""));
    for (const g of options) sigungu.add(new Option(g.name, g.code));
    sigungu.disabled = Boolean(found) && options.length === 0;
  }

  function syncRegion() {
    const lv = level();
    sido.hidden = lv !== "sido" && lv !== "sigungu";
    sigungu.hidden = lv !== "sigungu";
    regionNote.hidden = sido.hidden;
  }

  form.querySelectorAll('input[name="region_level"]').forEach((r) => r.addEventListener("change", syncRegion));
  sido.addEventListener("change", fillSigungu);

  // 예산: 미정이면 금액 입력 비활성화
  const krw = form.elements.namedItem("budget_krw");
  const undecided = form.elements.namedItem("budget_undecided");
  const budgetNote = form.querySelector('[data-note="budget"]');

  function syncBudget() {
    krw.disabled = undecided.checked;
    const digits = krw.value.replaceAll(",", "").trim();
    if (undecided.checked) budgetNote.textContent = "미정은 0원과 다르게 기록되며 기획안에 ‘추가 확정 필요’로 남습니다.";
    else if (/^\d+$/.test(digits)) budgetNote.textContent = `${Number(digits).toLocaleString("ko-KR")}원`;
    else budgetNote.textContent = "";
  }

  undecided.addEventListener("change", syncBudget);
  krw.addEventListener("input", syncBudget);

  // 지표 용도 안내 문구
  const useNote = form.querySelector('[data-note="indicator_use"]');
  form.querySelectorAll('input[name="indicator_use"]').forEach((r) =>
    r.addEventListener("change", () => {
      useNote.textContent = r.dataset.noteText;
    }),
  );

  // 잘못된 항목이 있으면 첫 오류로 이동
  form.querySelector(".has-error")?.scrollIntoView({ block: "center" });
})();
