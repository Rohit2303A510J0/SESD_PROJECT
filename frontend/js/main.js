document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("access_token");
  const authLink = document.getElementById("authLink");
  const heroButtons = document.getElementById("heroButtons");

  if (token) {
    // User is logged in
    authLink.innerHTML = `<a href="frontend/logout.html">Logout</a>`;
    if (heroButtons) {
      // Redirect to map automatically
      window.location.href = "frontend/map.html";
    }
  } else {
    // User not logged in
    authLink.innerHTML = `<a href="frontend/login.html">Login</a>`;
  }
});
