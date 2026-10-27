"use strict";

const $ = (id) => document.getElementById(id);

const API = {
    current: "/api/weather/current",
    forecast: "/api/weather/forecast",
    favorites: "/api/favorites"
};

let currentPlace = null;
let favoritesExpanded = false;

function iconUrl(icon, size = "2x") {
    return icon
        ? `https://openweathermap.org/img/wn/${icon}@${size}.png`
        : "https://openweathermap.org/img/wn/02d@2x.png";
}

function safeText(value, fallback = "—") {
    return value === null || value === undefined || value === ""
        ? fallback
        : String(value);
}

function weatherEmoji(description = "", icon = "") {
    const text = `${description} ${icon}`.toLowerCase();

    if (text.includes("thunder")) return "⛈️";
    if (text.includes("snow")) return "🌨️";
    if (text.includes("rain") || text.includes("drizzle")) return "🌧️";
    if (text.includes("cloud") || text.includes("04")) return "☁️";
    if (text.includes("mist") || text.includes("fog") || text.includes("haze")) return "🌫️";
    if (text.includes("02") || text.includes("partly")) return "🌤️";

    return "☀️";
}

// API helper
async function api(url, options = {}) {
    let response;

    try {
        response = await fetch(url, options);
    } catch {
        throw new Error(
            "Cannot reach the Flask server. Check that your backend is running."
        );
    }

    const body = await response.json().catch(() => null);

    if (!response.ok || body?.status === "error") {
        throw new Error(
            body?.message || `Request failed (${response.status}).`
        );
    }

    return body;
}

function jsonOptions(method, payload) {
    return {
        method,
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    };
}

// Notifications
function showMessage(message, type = "error") {
    const box = $("message");

    box.textContent = message;
    box.className = `message ${type}`;
    box.hidden = false;
}

function clearMessage() {
    $("message").hidden = true;
}

// Date and clock
function formatDate(date, options) {
    return new Intl.DateTimeFormat(undefined, options).format(date);
}

function updateClock() {
    const now = new Date();

    $("today-date").textContent = formatDate(now, {
        weekday: "short",
        day: "2-digit",
        month: "short",
        year: "numeric"
    });

    $("today-time").textContent = formatDate(now, {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function formatForecastDate(value) {
    const date = new Date(`${value}T12:00:00`);

    return {
        day: formatDate(date, { weekday: "short" }),
        date: formatDate(date, { day: "2-digit", month: "short" })
    };
}

// Render current weather
function renderCurrent(data) {
    currentPlace = data;

    $("current-city").textContent =
        `${data.city}${data.country ? `, ${data.country}` : ""}`;

    $("current-location").textContent =
        data.country ? `${data.city}, ${data.country}` : data.city;

    $("observed-date").textContent = data.observed_at
        ? `Updated ${formatDate(
            new Date(data.observed_at * 1000),
            {
                weekday: "long",
                day: "numeric",
                month: "long"
            }
        )}`
        : "Current local weather";

    $("current-temperature").textContent =
        Math.round(Number(data.temperature_c));

    $("current-description").textContent =
        safeText(data.description, "Weather unavailable");

    $("current-icon").src = iconUrl(data.icon);
    $("current-icon").alt = safeText(data.description, "Weather icon");

    $("feels-like").textContent =
        `${Math.round(Number(data.feels_like_c))}°C`;

    $("stat-feels").textContent =
        `${Math.round(Number(data.feels_like_c))}°C`;

    $("stat-humidity").textContent =
        `${safeText(data.humidity_percent)}%`;

    $("stat-wind").textContent =
        data.wind_speed_mps == null
            ? "— m/s"
            : `${Number(data.wind_speed_mps).toFixed(1)} m/s`;

    $("stat-pressure").textContent =
        `${safeText(data.pressure_hpa)} hPa`;

    $("stat-visibility").textContent =
        data.visibility_m == null
            ? "— km"
            : `${(
                Number(data.visibility_m) / 1000
            ).toFixed(1).replace(/\.0$/, "")} km`;
}

// Render five-day forecast
function renderForecast(data) {
    const byDay = new Map();

    for (const item of data.forecast || []) {
        if (!item.forecast_time_utc) continue;

        const date = item.forecast_time_utc.split(" ")[0];

        if (!byDay.has(date)) {
            byDay.set(date, []);
        }

        byDay.get(date).push(item);
    }

    const days = [...byDay.entries()].slice(0, 5);

    const cards = days.map(([date, items], index) => {
        const midday = items.reduce((best, item) => {
            const hour = Number(
                (item.forecast_time_utc.split(" ")[1] || "12:00")
                    .split(":")[0]
            );

            const bestHour = Number(
                (best.forecast_time_utc.split(" ")[1] || "12:00")
                    .split(":")[0]
            );

            return Math.abs(hour - 12) < Math.abs(bestHour - 12)
                ? item
                : best;
        }, items[0]);

        const temperatures = items
            .map(item => Number(item.temperature_c))
            .filter(Number.isFinite);

        const high = temperatures.length
            ? Math.round(Math.max(...temperatures))
            : "—";

        const low = temperatures.length
            ? Math.round(Math.min(...temperatures))
            : "—";

        const labels = formatForecastDate(date);

        const card = document.createElement("article");

        card.className = `day-card${index === 0 ? " today" : ""}`;

        card.innerHTML = `
            <strong class="day-name"></strong>
            <span class="day-date"></span>
            <img alt="" loading="lazy">

            <strong class="day-temperatures">
                <span class="day-high"></span> /
                <span class="day-low"></span>
            </strong>

            <span class="day-description"></span>

            <span class="rain-chance">
                <i data-lucide="droplet"></i>
                <span></span>
            </span>
        `;

        card.querySelector(".day-name").textContent = labels.day;
        card.querySelector(".day-date").textContent = labels.date;

        const image = card.querySelector("img");

        image.src = iconUrl(midday.icon);
        image.alt = safeText(midday.description, "Weather");

        card.querySelector(".day-high").textContent = `${high}°`;
        card.querySelector(".day-low").textContent = `${low}°`;

        card.querySelector(".day-description").textContent =
            safeText(midday.description, "No description");

        card.querySelector(".rain-chance span").textContent =
            `${safeText(midday.precipitation_probability_percent, 0)}%`;

        return card;
    });

    $("forecast-list").replaceChildren(...cards);

    if (!cards.length) {
        $("forecast-list").innerHTML =
            '<p class="skeleton">No forecast data was returned.</p>';
    }

    refreshIcons();
}

// Search and load weather
async function searchWeather(city, country = "") {
    city = city.trim();
    country = country.trim().toUpperCase();

    if (!city) {
        showMessage("Please enter a city name.");
        return;
    }

    $("city").value = city;
    $("country").value = country;

    showMessage(`Getting weather for ${city}...`, "info");

    const query = new URLSearchParams({ city, country });

    try {
        const [current, forecast] = await Promise.all([
            api(`${API.current}?${query.toString()}`),
            api(`${API.forecast}?${query.toString()}`)
        ]);

        renderCurrent(current.data);
        renderForecast(forecast.data);

        clearMessage();
    } catch (error) {
        showMessage(error.message);

        $("current-temperature").textContent = "—";
        $("current-description").textContent = "Unable to load weather";

        $("forecast-list").innerHTML =
            '<p class="skeleton">Forecast is unavailable. Try searching again.</p>';
    }
}

// Build favourite-city row
function favoriteItem(favorite, index, weather = null) {
    const row = document.createElement("article");
    row.className = "favorite-row";

    const icon = document.createElement("div");
    icon.className = "favorite-weather-icon";

    icon.textContent = weather
        ? weatherEmoji(weather.description, weather.icon)
        : ["☀️", "🌤️", "🌧️", "☀️", "☁️"][index % 5];

    icon.setAttribute("aria-hidden", "true");

    const city = document.createElement("div");

    const cityButton = document.createElement("button");
    cityButton.className = "favorite-city-button";
    cityButton.type = "button";
    cityButton.textContent = favorite.city;
    cityButton.title = `Show weather for ${favorite.city}`;

    cityButton.addEventListener("click", () => {
        searchWeather(favorite.city, favorite.country || "");
    });

    const country = document.createElement("div");
    country.className = "favorite-country";

    country.textContent =
        `${favorite.country || "—"}${favorite.note ? ` | ${favorite.note}` : ""}`;

    city.append(cityButton, country);

    const temperature = document.createElement("div");

    const tempValue = document.createElement("div");
    tempValue.className = "favorite-temp";

    tempValue.textContent = weather
        ? `${Math.round(Number(weather.temperature_c))}°C`
        : "—°C";

    const condition = document.createElement("div");
    condition.className = "favorite-condition";

    condition.textContent = weather
        ? safeText(weather.description, "Weather")
        : "Saved city";

    temperature.append(tempValue, condition);

    const actions = document.createElement("div");
    actions.className = "favorite-actions";

    const edit = document.createElement("button");

    edit.className = "mini-button edit-button";
    edit.type = "button";
    edit.title = "Edit note";
    edit.setAttribute("aria-label", `Edit ${favorite.city}`);
    edit.innerHTML = '<i data-lucide="pencil"></i>';

    edit.addEventListener("click", () => editFavorite(favorite));

    const remove = document.createElement("button");

    remove.className = "mini-button delete-button";
    remove.type = "button";
    remove.title = "Delete favourite";
    remove.setAttribute("aria-label", `Delete ${favorite.city}`);
    remove.innerHTML = '<i data-lucide="trash-2"></i>';

    remove.addEventListener("click", () => deleteFavorite(favorite));

    actions.append(edit, remove);

    const spacer = document.createElement("span");

    row.append(icon, city, temperature, spacer, actions);

    return row;
}

// Load favourite cities and their weather
async function loadFavorites() {
    const list = $("favorites-list");

    try {
        const result = await api(API.favorites);
        const items = result.data || [];

        const visible = favoritesExpanded
            ? items
            : items.slice(0, 5);

        const weatherResults = await Promise.all(
            visible.map(async favorite => {
                try {
                    const query = new URLSearchParams({
                        city: favorite.city,
                        country: favorite.country || ""
                    });

                    const result = await api(
                        `${API.current}?${query.toString()}`
                    );

                    return result.data;
                } catch {
                    return null;
                }
            })
        );

        if (!items.length) {
            list.innerHTML =
                '<p class="skeleton">No favourite cities yet. Add one to get started.</p>';
        } else {
            list.replaceChildren(
                ...visible.map((favorite, index) =>
                    favoriteItem(favorite, index, weatherResults[index])
                )
            );
        }

        $("view-all-favorites").hidden = items.length <= 5;

        $("view-all-favorites").textContent = favoritesExpanded
            ? "Show Fewer Cities"
            : "View All Favourite Cities";

        const arrow = document.createElement("i");

        arrow.setAttribute(
            "data-lucide",
            favoritesExpanded ? "arrow-up" : "arrow-right"
        );

        $("view-all-favorites").append(" ", arrow);

        refreshIcons();
    } catch (error) {
        list.innerHTML = "";

        const message = document.createElement("p");
        message.className = "skeleton";
        message.textContent = error.message;

        list.append(message);
    }
}

// Add favourite city
async function addFavorite(city, country, note = "") {
    const query = new URLSearchParams({ city, country });

    let place = currentPlace;

    if (!place || place.city.toLowerCase() !== city.toLowerCase()) {
        const result = await api(`${API.current}?${query.toString()}`);
        place = result.data;
    }

    await api(
        API.favorites,
        jsonOptions("POST", {
            city: place.city,
            country: place.country || country || "",
            latitude: place.latitude ?? null,
            longitude: place.longitude ?? null,
            note
        })
    );

    showMessage(
        `${place.city} added to favourite cities.`,
        "success"
    );

    await loadFavorites();
}

// Edit favourite note
async function editFavorite(favorite) {
    const note = prompt(
        `Add or edit a note for ${favorite.city}:`,
        favorite.note || ""
    );

    if (note === null) return;

    try {
        await api(
            `${API.favorites}/${favorite.id}`,
            jsonOptions("PUT", { note })
        );

        showMessage(`Updated ${favorite.city}.`, "success");

        await loadFavorites();
    } catch (error) {
        showMessage(error.message);
    }
}

// Delete favourite city
async function deleteFavorite(favorite) {
    if (!confirm(
        `Remove ${favorite.city} from your favourite cities?`
    )) {
        return;
    }

    try {
        await api(
            `${API.favorites}/${favorite.id}`,
            { method: "DELETE" }
        );

        showMessage(
            `${favorite.city} removed from favourites.`,
            "success"
        );

        await loadFavorites();
    } catch (error) {
        showMessage(error.message);
    }
}

// Refresh Lucide icons
function refreshIcons() {
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

// Theme toggle
function setupTheme() {
    const light = $("light-theme");
    const dark = $("dark-theme");

    function setDark(enabled) {
        document.body.classList.toggle("light-mode", !enabled);

        light.classList.toggle("active", !enabled);
        dark.classList.toggle("active", enabled);
    }

    light.addEventListener("click", () => setDark(false));
    dark.addEventListener("click", () => setDark(true));
}

// Add-city dialog
function setupDialog() {
    const dialog = $("add-city-dialog");

    $("add-city-button").addEventListener("click", () => {
        $("favorite-city").value = $("city").value.trim();

        $("favorite-country").value =
            $("country").value.trim();

        if (typeof dialog.showModal === "function") {
            dialog.showModal();
        } else {
            dialog.setAttribute("open", "");
        }
    });

    const close = () => {
        if (typeof dialog.close === "function") {
            dialog.close();
        } else {
            dialog.removeAttribute("open");
        }
    };

    $("close-dialog").addEventListener("click", close);
    $("cancel-dialog").addEventListener("click", close);

    $("add-city-form").addEventListener("submit", async event => {
        event.preventDefault();

        const city = $("favorite-city").value.trim();

        const country = $("favorite-country")
            .value.trim()
            .toUpperCase();

        const note = $("favorite-note").value.trim();

        if (!city) return;

        try {
            await addFavorite(city, country, note);

            $("favorite-note").value = "";

            close();
        } catch (error) {
            showMessage(error.message);
        }
    });
}

// Sidebar navigation
function setupNavigation() {
    const sidebar = $("sidebar");

    $("menu-toggle").addEventListener("click", () => {
        sidebar.classList.toggle("open");
    });

    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", () => {
            document.querySelectorAll(".nav-link").forEach(item => {
                item.classList.toggle("active", item === link);
            });

            sidebar.classList.remove("open");
        });
    });

    $("view-all-favorites").addEventListener("click", () => {
        favoritesExpanded = !favoritesExpanded;
        loadFavorites();
    });
}

// Search form
$("search-form").addEventListener("submit", event => {
    event.preventDefault();

    searchWeather(
        $("city").value,
        $("country").value
    );
});

// Initialize dashboard
setupTheme();
setupDialog();
setupNavigation();

updateClock();

setInterval(updateClock, 60_000);

refreshIcons();

searchWeather("Vijayawada", "IN");
loadFavorites();