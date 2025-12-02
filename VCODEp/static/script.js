document.addEventListener("DOMContentLoaded", function() {
  const progressBar = document.getElementById("progressBar");
  const value = progressBar.getAttribute("data-value");
  progressBar.style.width = value + "%";
});
