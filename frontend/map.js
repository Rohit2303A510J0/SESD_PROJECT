const BASE_URL = "https://sesd-project-7gqa.onrender.com";
const token = localStorage.getItem("access_token");

// Redirect if not logged in
if (!token) {
  alert("Please log in first!");
  window.location.href = "login.html";
}

// Initialize map
const map = L.map("map").setView([20.5937, 78.9629], 5); // India default

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const searchBtn = document.getElementById("searchBtn");
const searchInput = document.getElementById("searchInput");
const locationName = document.getElementById("locationName");
const weatherInfo = document.getElementById("weatherInfo");
const attractionList = document.getElementById("attractionList");
const logoutBtn = document.getElementById("logoutBtn");

// Search location
searchBtn.addEventListener("click", async () => {
  const query = searchInput.value.trim();
  if (!query) return alert("Enter a location to search.");

  try {
    // 1️⃣ Get location coordinates
    const locRes = await fetch(`${BASE_URL}/location/?query=${encodeURIComponent(query)}`);
    const locData = await locRes.json();

    if (!locRes.ok) throw new Error(locData.detail || "Failed to fetch location");

    const { latitude, longitude, display_name } = locData;
    map.setView([latitude, longitude], 10);

    L.marker([latitude, longitude]).addTo(map).bindPopup(display_name).openPopup();
    locationName.textContent = display_name;

    // 2️⃣ Get weather
    const weatherRes = await fetch(`${BASE_URL}/weather?lat=${latitude}&lon=${longitude}`);
    const weatherData = await weatherRes.json();

    weatherInfo.textContent = `🌡️ ${weatherData.temperature}°C, ${weatherData.description}`;

    // 3️⃣ Get attractions
    const attrRes = await fetch(`${BASE_URL}/attractions?lat=${latitude}&lon=${longitude}`);
    const attractions = await attrRes.json();

    attractionList.innerHTML = "";
    attractions.forEach((a) => {
      const div = document.createElement("div");
      div.classList.add("attraction-item");
      div.innerHTML = `
        <h4>${a.name}</h4>
        <p>${a.country}</p>
        <button class="favorite-btn" data-id="${a.id}">❤️ Add to Favorites</button>
      `;
      attractionList.appendChild(div);
    });

    // Handle favorite button clicks
    document.querySelectorAll(".favorite-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const attractionId = btn.getAttribute("data-id");

        try {
          const res = await fetch(`${BASE_URL}/favorites/`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ attraction_id: parseInt(attractionId) }),
          });

          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Failed to add favorite");

          alert("✅ Added to favorites!");
        } catch (err) {
          alert("❌ " + err.message);
        }
      });
    });
  } catch (err) {
    alert("❌ " + err.message);
  }
});

// Logout
logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("access_token");
  window.location.href = "login.html";
});
