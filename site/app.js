// "Kopiuj tekst" buttons: data-copy="<id of the element whose text is copied>"
document.querySelectorAll("[data-copy]").forEach((button) => {
  button.addEventListener("click", async () => {
    const source = document.getElementById(button.dataset.copy);
    try {
      await navigator.clipboard.writeText(source.innerText);
    } catch {
      // older browsers or a page opened from disk: select the text so it can be copied by hand
      const range = document.createRange();
      range.selectNodeContents(source);
      getSelection().removeAllRanges();
      getSelection().addRange(range);
      document.execCommand("copy");
    }
    const label = button.textContent;
    button.textContent = "Skopiowano";
    setTimeout(() => { button.textContent = label; }, 2000);
  });
});

// "Drukuj" buttons
document.querySelectorAll("[data-print]").forEach((button) => {
  button.addEventListener("click", () => window.print());
});
