const BASE_URL = "https://sesd-project-7gqa.onrender.com"; // your Render backend
let token = localStorage.getItem("access_token");

// ----- AUTH -----
document.getElementById("loginBtn").addEventListener("click", async () => {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  try {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");
    token = data.access_token;
    localStorage.setItem("access_token", token);
    document.getElementById("authStatus").innerText = "✅ Logged in!";
  } catch (err) {
    document.getElementById("authStatus").innerText = "❌ " + err.message;
  }
});

document.getElementById("registerBtn").addEventListener("click", async () => {
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
    document.getElementById("authStatus").innerText = "✅ Registered successfully!";
  } catch (err) {
    document.getElementById("authStatus").innerText = "❌ " + err.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("access_token");
  token = null;
  document.getElementById("authStatus").innerText = "🚪 Logged out!";
});

// ----- LOCATION -----
let currentLat = null;
let currentLon = null;

document.getElementById("getLocationBtn").addEventListener("click", async () => {
  const country = document.getElementById("countryInput").value.trim();
  try {
    const res = await fetch(`${BASE_URL}/location/?query=${encodeURIComponent(country)}`);
    const data = await res.json();
    document.getElementById("locationOutput").textContent = JSON.stringify(data, null, 2);
    if (data.latitude && data.longitude) {
      currentLat = data.latitude;
      currentLon = data.longitude;
    }
  } catch (err) {
    document.getElementById("locationOutput").textContent = "❌ " + err.message;
  }
});

// ----- WEATHER -----
document.getElementById("getWeatherBtn").addEventListener("click", async () => {
  if (!currentLat || !currentLon) return alert("Please get location first!");
  try {
    const res = await fetch(`${BASE_URL}/weather?lat=${currentLat}&lon=${currentLon}`);
    const data = await res.json();
    document.getElementById("weatherOutput").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("weatherOutput").textContent = "❌ " + err.message;
  }
});

// ----- ATTRACTIONS -----
document.getElementById("getAttractionsBtn").addEventListener("click", async () => {
  if (!currentLat || !currentLon) return alert("Please get location first!");
  try {
    const res = await fetch(`${BASE_URL}/attractions?lat=${currentLat}&lon=${currentLon}`);
    const data = await res.json();
    document.getElementById("attractionsOutput").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("attractionsOutput").textContent = "❌ " + err.message;
  }
});

// ----- FAVORITES -----
document.getElementById("getFavoritesBtn").addEventListener("click", async () => {
  if (!token) return alert("Login first!");
  try {
    const res = await fetch(`${BASE_URL}/favorites/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    document.getElementById("favoritesOutput").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("favoritesOutput").textContent = "❌ " + err.message;
  }
});

document.getElementById("addFavoriteBtn").addEventListener("click", async () => {
  if (!token) return alert("Login first!");
  const id = parseInt(document.getElementById("favAttractionId").value);
  if (!id) return alert("Enter a valid attraction ID");
  try {
    const res = await fetch(`${BASE_URL}/favorites/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ attraction_id: id }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to add favorite");
    document.getElementById("favoritesOutput").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("favoritesOutput").textContent = "❌ " + err.message;
  }
});

document.getElementById("deleteFavoriteBtn").addEventListener("click", async () => {
  if (!token) return alert("Login first!");
  const id = parseInt(document.getElementById("favAttractionId").value);
  if (!id) return alert("Enter a valid attraction ID");
  try {
    const res = await fetch(`${BASE_URL}/favorites/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    document.getElementById("favoritesOutput").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("favoritesOutput").textContent = "❌ " + err.message;
  }
});
