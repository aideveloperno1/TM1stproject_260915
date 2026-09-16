// 4단계 보완 선택: 고른 결정·대안에 따라 입력칸을 보여준다. 검증은 서버가 한다.
(() => {
  const forms = document.querySelectorAll(".choice-form");
  if (!forms.length) return;

  const sync = (form) => {
    const decision = form.querySelector('input[name="decision"]:checked')?.value ?? "";
    const option = form.querySelector('input[name="option_id"]:checked');
    const usesOption = decision === "adopt" || decision === "modify";

    form.querySelectorAll(".option-card").forEach((card) => {
      const input = card.querySelector('input[name="option_id"]');
      card.classList.toggle("option-card-on", usesOption && input.checked);
      card.classList.toggle("option-card-off", !usesOption);
    });

    const modify = form.querySelector('textarea[name="modified_text"]')?.closest(".field");
    if (modify) modify.hidden = decision !== "modify";

    const execution = form.querySelector(".execution-box");
    if (execution) {
      const needed = usesOption && option?.dataset.hasExecution === "1";
      execution.hidden = !needed;
    }
  };

  forms.forEach((form) => {
    sync(form);
    form.addEventListener("change", () => sync(form));
  });
})();
