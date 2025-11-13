// Base API URL — your Render backend
const BASE_URL = "https://sesd-project-7gqa.onrender.com";

// ---------- LOGIN ----------
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Invalid credentials");

      localStorage.setItem("access_token", data.access_token);
      alert("✅ Login successful!");
      window.location.href = "map.html";
    } catch (err) {
      alert("❌ " + err.message);
      console.error("Login error:", err);
    }
  });
}

// ---------- REGISTER ----------
const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const res = await fetch(`${BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");

      alert("✅ Registration successful! You can now log in.");
      window.location.href = "login.html";
    } catch (err) {
      alert("❌ " + err.message);
      console.error("Register error:", err);
    }
  });
}
