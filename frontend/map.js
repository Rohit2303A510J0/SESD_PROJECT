const BASE_URL = "https://sesd-project-7gqa.onrender.com";
const token = localStorage.getItem("access_token");

if (!token) {
  alert("Please log in first!");
  window.location.href = "login.html";
}

const map = L.map("map", {
  worldCopyJump: true,
  minZoom: 2,
}).setView([20, 0], 2);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

let geojsonLayer;
let activeCountry = null;

// Load GeoJSON world map
async function loadGeoJSON() {
  const res = await fetch("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json");
  const data = await res.json();

  geojsonLayer = L.geoJson(data, {
    style: {
      color: "#00bfa6",
      weight: 1,
      fillOpacity: 0.1,
    },
    onEachFeature: onEachCountry,
  }).addTo(map);
}

function onEachCountry(feature, layer) {
  layer.on({
    mouseover: (e) => highlightCountry(e, feature),
    mouseout: resetHighlight,
    click: (e) => zoomToCountry(e, feature),
  });
}

function highlightCountry(e, feature) {
  const layer = e.target;
  layer.setStyle({
    weight: 2,
    color: "#00d4b4",
    fillOpacity: 0.3,
  });

  const name = feature.properties.name || "Unknown";
  document.getElementById("countryName").textContent = name;
  document.getElementById("countryDetails").innerHTML = `Loading info...`;

  fetch(`https://restcountries.com/v3.1/name/${encodeURIComponent(name)}?fullText=true`)
    .then((r) => r.json())
    .then((info) => {
      if (info && info[0]) {
        const c = info[0];
        document.getElementById(
          "countryDetails"
        ).innerHTML = `<b>Capital:</b> ${c.capital?.[0] || "N/A"}<br>
                       <b>Region:</b> ${c.region}<br>
                       <b>Population:</b> ${c.population.toLocaleString()}`;
      }
    })
    .catch(() => {
      document.getElementById("countryDetails").innerText = "Info not available";
    });
}

function resetHighlight(e) {
  geojsonLayer.resetStyle(e.target);
}

async function zoomToCountry(e, feature) {
  if (activeCountry) geojsonLayer.resetStyle(activeCountry);
  activeCountry = e.target;

  map.fitBounds(activeCountry.getBounds());

  const countryName = feature.properties.name;
  document.getElementById("countryName").textContent = countryName;

  // Get lat/lon for weather & attractions
  const locRes = await fetch(`${BASE_URL}/location/?query=${encodeURIComponent(countryName)}`);
  const locData = await locRes.json();

  if (!locRes.ok || !locData.latitude || !locData.longitude) {
    document.getElementById("weatherInfo").innerHTML = "⚠️ Unable to fetch location data.";
    return;
  }

  const { latitude, longitude } = locData;

  // Weather
  const weatherRes = await fetch(`${BASE_URL}/weather?lat=${latitude}&lon=${longitude}`);
  const weatherData = await weatherRes.json();
  document.getElementById("weatherInfo").innerHTML = `
    <p>🌡️ ${weatherData.temperature}°C, ${weatherData.description}</p>
  `;

  // Attractions
  const attrRes = await fetch(`${BASE_URL}/attractions?lat=${latitude}&lon=${longitude}`);
  const attractions = await attrRes.json();

  const attractionList = document.getElementById("attractionList");
  attractionList.innerHTML = "<h4>Attractions:</h4>";

  if (attractions.length === 0) {
    attractionList.innerHTML += "<p>No attractions found.</p>";
  } else {
    attractions.forEach((a) => {
      const div = document.createElement("div");
      div.classList.add("attraction-item");
      div.innerHTML = `
        <b>${a.name}</b><br>${a.country}<br>
        <button class="favorite-btn" data-id="${a.id}">❤️ Add to Favorites</button>
      `;
      attractionList.appendChild(div);
    });
  }

  // Handle favorites
  document.querySelectorAll(".favorite-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const attractionId = btn.getAttribute("data-id");
      try {
        const res = await fetch(`${BASE_URL}/favorites/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
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
}

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("access_token");
  window.location.href = "login.html";
});

loadGeoJSON();
