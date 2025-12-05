/* script.js */


function showPage(pageId) {
  const pages = document.querySelectorAll(".page");
  pages.forEach(page => {
    page.classList.toggle("active", page.id === pageId);
  });
}

document.querySelectorAll(".next-button").forEach(button => {
  button.addEventListener("click", () => {
    showPage(button.getAttribute("data-next"));
  });
});

document.querySelectorAll(".back-button").forEach(button => {
  button.addEventListener("click", () => {
    showPage(button.getAttribute("data-prev"));
  });
});