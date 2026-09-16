// AI 참고 의견을 화면이 뜬 뒤에 받아 채운다. 실패해도 검토 질문 화면은 그대로 둔다.
// 받은 문장은 textContent로만 넣는다 (AI 출력을 HTML로 해석하지 않는다).
(function () {
  "use strict";

  var box = document.querySelector("[data-ai-box]");
  if (!box) return;

  var list = box.querySelector("[data-ai-list]");
  var message = box.querySelector("[data-ai-message]");
  var source = box.querySelector("[data-ai-source]");

  function show(text) {
    message.textContent = text;
    message.hidden = false;
  }

  function addOpinion(opinion) {
    var item = document.createElement("p");
    item.className = "ai-opinion";
    item.textContent = opinion.text;

    if (opinion.rule_ids && opinion.rule_ids.length) {
      var badges = document.createElement("span");
      badges.className = "badge-row";
      opinion.rule_ids.forEach(function (ruleId) {
        var badge = document.createElement("span");
        badge.className = "scope-badge";
        badge.textContent = "근거 " + ruleId;
        badges.appendChild(badge);
      });
      item.appendChild(badges);
    }
    list.appendChild(item);
  }

  fetch("/step/3/opinions", { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error(String(response.status));
      return response.json();
    })
    .then(function (data) {
      if (data.state === "off") return; // 설정으로 꺼 둔 경우: 영역을 열지 않는다
      box.hidden = false;

      if (data.state !== "ok") {
        show("AI 의견을 불러오지 못했습니다.");
        return;
      }
      if (!data.opinions.length) {
        show("이번에는 참고 의견이 없습니다.");
        return;
      }
      data.opinions.forEach(addOpinion);
      message.hidden = true;
      source.textContent = (data.model || "로컬 모델") + " · " + data.created_at;
    })
    .catch(function () {
      box.hidden = false;
      show("AI 의견을 불러오지 못했습니다.");
    });
})();
