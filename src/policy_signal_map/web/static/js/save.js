// 결과 저장: 저장 위치를 고르는 창을 띄우고, 지원하지 않는 브라우저에서는 내려받기로 대신한다.
// 서버에는 파일을 남기지 않는다 (최종기획서 4-5).
(function () {
  "use strict";

  function note(button, message) {
    var box = document.querySelector("[data-save-note]");
    if (!box) return;
    box.textContent = message;
    box.hidden = !message;
  }

  function fallbackDownload(url, filename) {
    var link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  async function save(button) {
    var url = button.dataset.url;
    var filename = button.dataset.filename || "보완기획안.md";

    if (typeof window.showSaveFilePicker !== "function") {
      fallbackDownload(url, filename);
      note(button, "저장 위치 선택을 지원하지 않는 브라우저라 내려받기 폴더에 저장했습니다.");
      return;
    }

    var handle;
    try {
      handle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [{ description: "Markdown 문서", accept: { "text/markdown": [".md"] } }],
      });
    } catch (error) {
      note(button, "저장을 취소했습니다.");
      return;
    }

    button.disabled = true;
    try {
      var response = await fetch(url, { credentials: "same-origin" });
      if (!response.ok) throw new Error(String(response.status));
      var text = await response.text();
      var stream = await handle.createWritable();
      await stream.write(text);
      await stream.close();
      note(button, "저장했습니다: " + handle.name);
    } catch (error) {
      note(button, "저장하지 못했습니다. 내려받기로 다시 시도합니다.");
      fallbackDownload(url, filename);
    } finally {
      button.disabled = false;
    }
  }

  document.querySelectorAll("[data-save-button]").forEach(function (button) {
    button.addEventListener("click", function () {
      save(button);
    });
  });
})();
