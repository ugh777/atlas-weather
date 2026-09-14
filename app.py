import datetime as dt
from typing import Any

import requests
import streamlit as st


st.set_page_config(
    page_title="Atlas Weather",
    page_icon="🌤️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

FALLBACK = {
    "name": "Tokyo",
    "country": "Japan",
    "latitude": 35.6762,
    "longitude": 139.6503,
    "current": {
        "temperature_2m": 22,
        "apparent_temperature": 23,
        "relative_humidity_2m": 62,
        "wind_speed_10m": 11,
        "weather_code": 1,
    },
    "daily": {
        "time": ["2026-09-14", "2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"],
        "weather_code": [1, 2, 3, 61, 80],
        "temperature_2m_max": [25, 26, 24, 23, 25],
        "temperature_2m_min": [18, 19, 20, 18, 19],
    },
}

WEATHER = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Heavy drizzle", "🌧️"),
    61: ("Light rain", "🌦️"),
    63: ("Rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    71: ("Light snow", "🌨️"),
    73: ("Snow", "❄️"),
    75: ("Heavy snow", "❄️"),
    80: ("Rain showers", "🌦️"),
    81: ("Showers", "🌧️"),
    82: ("Heavy showers", "⛈️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm", "⛈️"),
    99: ("Thunderstorm", "⛈️"),
}

st.markdown(
    """
    <style>
    :root { --ink:#163247; --muted:#6f8794; --accent:#168b9b; }
    .stApp { position:relative; overflow:hidden; background:linear-gradient(145deg,#dff3f4 0%,#f7f4eb 48%,#dceef6 100%); color:var(--ink); }
    .stApp::before, .stApp::after { content:""; position:fixed; z-index:0; width:34rem; height:34rem; border-radius:50%; pointer-events:none; filter:blur(10px); opacity:.7; }
    .stApp::before { top:-15rem; right:-10rem; background:radial-gradient(circle at 35% 35%,rgba(67,201,196,.5),rgba(67,201,196,0) 68%); }
    .stApp::after { bottom:-18rem; left:-12rem; background:radial-gradient(circle at 55% 45%,rgba(255,193,102,.45),rgba(255,193,102,0) 68%); }
    .stApp > * { position:relative; z-index:1; }
    @media (prefers-color-scheme: dark) {
      .stApp { background:linear-gradient(145deg,#102d38 0%,#172a3a 48%,#243148 100%); }
      .stApp::before { background:radial-gradient(circle at 35% 35%,rgba(61,194,195,.34),rgba(61,194,195,0) 68%); }
      .stApp::after { background:radial-gradient(circle at 55% 45%,rgba(245,173,90,.22),rgba(245,173,90,0) 68%); }
    }
    .block-container { max-width: 640px; padding-top: 3.5rem; }
    .eyebrow { color:var(--accent); font-size:.74rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
    .intro { color:var(--muted); font-size:1rem; margin-bottom:1.5rem; }
    .weather-card { border:1px solid rgba(255,255,255,.62); border-radius:24px; padding:1.55rem; background:rgba(255,255,255,.58); box-shadow:0 22px 60px rgba(26,76,94,.18); backdrop-filter:blur(18px); }
    @media (prefers-color-scheme: dark) { .weather-card { background:rgba(25,50,61,.68); border-color:rgba(220,248,249,.16); } }
    .place { color:var(--muted); font-size:.9rem; font-weight:650; }
    .hero { display:flex; align-items:center; justify-content:space-between; margin-top:1.2rem; }
    .temperature { font-size:clamp(4.2rem,18vw,7rem); font-weight:250; line-height:.82; letter-spacing:-.1em; }
    .temperature small { font-size:.35em; font-weight:600; letter-spacing:-.04em; vertical-align:top; }
    .condition { text-align:right; } .condition .icon { font-size:3.2rem; line-height:1; }
    .condition strong, .condition span { display:block; } .condition span { color:var(--muted); font-size:.82rem; }
    .metric-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.55rem; margin-top:1.5rem; }
    .metric { border:1px solid rgba(29,75,99,.12); border-radius:13px; padding:.7rem; }
    .metric span { display:block; color:var(--muted); font-size:.73rem; } .metric strong { font-size:.9rem; }
    .forecast-title { display:flex; justify-content:space-between; align-items:baseline; margin:2rem 0 .8rem; }
    .forecast-title span { color:var(--muted); font-size:.8rem; }
    .forecast-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:.5rem; }
    .forecast-day { border:1px solid rgba(29,75,99,.12); border-radius:16px; padding:.8rem .25rem; text-align:center; background:rgba(255,255,255,.55); }
    .forecast-day .name { color:var(--muted); font-size:.74rem; font-weight:700; }
    .forecast-day .icon { font-size:1.65rem; margin:.65rem 0; } .forecast-day .low { color:var(--muted); font-weight:500; }
    </style>
    """,
    unsafe_allow_html=True,
)


def weather_info(code: int) -> tuple[str, str]:
    return WEATHER.get(code, ("Changing skies", "🌤️"))


def city_search(query: str) -> dict[str, Any]:
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": query, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise ValueError("No city found. Try a different spelling.")
    return results[0]


def fetch_weather(place: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "timezone": "auto",
            "forecast_days": 5,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        },
        timeout=10,
    )
    response.raise_for_status()
    return {**place, **response.json()}


@st.cache_data(ttl=600, show_spinner=False)
def load_weather(query: str) -> tuple[dict[str, Any], bool, str | None]:
    try:
        place = FALLBACK if query.casefold() == "tokyo" else city_search(query)
    except ValueError as error:
        return FALLBACK, True, str(error)
    except requests.RequestException:
        return FALLBACK, True, None
    try:
        return fetch_weather(place), False, None
    except requests.RequestException:
        return FALLBACK, True, None


st.markdown('<div class="eyebrow">Atlas weather</div>', unsafe_allow_html=True)
st.title("Find your weather.")
st.markdown('<p class="intro">A clear view of today and the days ahead, wherever in the world you are.</p>', unsafe_allow_html=True)

with st.form("city-search"):
    query = st.text_input("Search any city in the world", value="Tokyo", label_visibility="collapsed", placeholder="Search any city in the world")
    submitted = st.form_submit_button("Search", use_container_width=True)

if "weather_query" not in st.session_state:
    st.session_state.weather_query = "Tokyo"
if submitted and query.strip():
    st.session_state.weather_query = query.strip()

data, is_fallback, error = load_weather(st.session_state.weather_query)
current = data["current"]
daily = data["daily"]
name = f'{data["name"]}, {data.get("country", "World")}'
label, icon = weather_info(current["weather_code"])

if error:
    st.error(error)
elif is_fallback:
    st.info("Live data is unavailable — showing the Tokyo fallback forecast.")
else:
    st.caption(f"Live conditions for {data['name']}.")

st.markdown(
    f"""
    <section class="weather-card">
      <div class="place">📍 {name}</div>
      <div class="hero">
        <div class="temperature">{round(current["temperature_2m"])}<small>°C</small></div>
        <div class="condition"><div class="icon">{icon}</div><strong>{label}</strong><span>{'Offline forecast' if is_fallback else 'Updated just now'}</span></div>
      </div>
      <div class="metric-grid">
        <div class="metric"><span>Feels like</span><strong>{round(current["apparent_temperature"])}°</strong></div>
        <div class="metric"><span>Humidity</span><strong>{round(current["relative_humidity_2m"])}%</strong></div>
        <div class="metric"><span>Wind</span><strong>{round(current["wind_speed_10m"])} km/h</strong></div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(f'<div class="forecast-title"><h3>5-day forecast</h3><span>{data["name"]}</span></div>', unsafe_allow_html=True)
cards = []
for index, date in enumerate(daily["time"][:5]):
    day = "Today" if index == 0 else dt.date.fromisoformat(date).strftime("%a")
    day_label, day_icon = weather_info(daily["weather_code"][index])
    cards.append(
        f'<div class="forecast-day"><div class="name">{day}</div><div class="icon">{day_icon}</div>'
        f'<strong>{round(daily["temperature_2m_max"][index])}° <span class="low">{round(daily["temperature_2m_min"][index])}°</span></strong></div>'
    )
st.markdown(f'<div class="forecast-grid">{"".join(cards)}</div>', unsafe_allow_html=True)
st.markdown(
    '<div style="margin-top:2rem;text-align:center;color:#6f8794;font-size:.76rem">'
    'Weather data by <a href="https://open-meteo.com/" target="_blank">Open-Meteo</a>'
    ' · <a href="https://ugh777.github.io/atlas-weather/" target="_blank">Web app</a>'
    ' · <a href="https://atlas-weather-ugh.streamlit.app/" target="_blank">Streamlit app</a>'
    '</div>',
    unsafe_allow_html=True,
)
