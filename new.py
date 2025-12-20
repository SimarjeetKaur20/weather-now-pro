# new.py -- Weather Now (Pro edition)
import streamlit as st
import requests
from datetime import datetime, timedelta
import base64
import os
import json
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# ====================================================================
# CONFIGURATION AND TRANSLATIONS (Updated with new features)
# ====================================================================

# 🔑 API KEYS - USING PLACEHOLDERS HERE, ASSUMING USER HAS VALID KEYS
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
UNSPLASH_ACCESS_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"


# Persistence files
FAV_FILE = os.path.join(os.getcwd(), "favourites.json")
CACHE_FILE = os.path.join(os.getcwd(), "cache.json")

# --- Dynamic Background Image URLs ---
BACKGROUND_IMAGES = {
    "clear": "https://images.pexels.com/photos/281260/pexels-photo-281260.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=2000",
    "clouds": "https://images.pexels.com/photos/531767/pexels-photo-531767.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=2000",
    "rain": "https://images.unsplash.com/photo-1610741083757-1ae88e1a17f7?q=80&w=2000&auto=format&fit=crop",
    "drizzle": "https://images.unsplash.com/photo-1610741083757-1ae88e1a17f7?q=80&w=2000&auto=format&fit=crop",
    "thunderstorm": "https://images.pexels.com/photos/1118873/pexels-photo-1118873.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=2000",
    "snow": "https://images.pexels.com/photos/1144211/pexels-photo-1144211.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=2000",
    "mist": "https://images.unsplash.com/photo-1544321045-8664165d5686?q=80&w=2000&auto=format&fit=crop",
}

# --- TRANSLATIONS DICTIONARY ---
TRANSLATIONS = {
    "english": {
        "title": "Weather Now - Smart Forecasting (Pro)",
        "tagline": "Real-time weather, maps, trends, UV, clothing tips and more.",
        "input_label": "📍 Enter City Name (e.g., Dehradun, Delhi, London)",
        "input_placeholder": "Enter City Name and press Enter",
        "press_enter": "Press Enter to search for the city's weather!",
        "welcome": "Welcome! Start by entering a city name above or use 'Detect My Location'.",
        "welcome_detail": "See forecast, map, UV, clothing tips, and save favourites.",
        "weather": "Weather",
        "landmark_unavailable": "Landmark image not available.",
        "feels_like": "Feels Like",
        "humidity": "Humidity",
        "wind_speed": "Wind Speed",
        "pressure": "Pressure",
        "severe_alert": "🚨 Severe Weather Alert! Take precautions.",
        "forecast_header": "📅 5-Day Forecast (Midday)",
        "hourly_header": "⏱ Next 24 Hours (Hourly Forecast)",
        "forecast_error": "Error: Could not fetch 5-day forecast. Check API configuration.",
        "city_not_found": "City '{}' not found! Please try again.",
        "error_fetching": "Error fetching weather data: {}",
        "theme_selector": "Interface Theme",
        "language_selector": "Select Language",
        "light_mode": "🌞 Light Mode",
        "dark_mode": "🌙 Dark Mode",
        "sunrise": "🌅 Sunrise",
        "sunset": "🌇 Sunset",
        "aqi": "💨 Air Quality Index (AQI)",
        "aqi_good": "Good (1)",
        "aqi_fair": "Fair (2)",
        "aqi_moderate": "Moderate (3)",
        "aqi_poor": "Poor (4)",
        "aqi_very_poor": "Very Poor (5)",
        "country_error": "Please enter a specific *city name*, not a country name.",
        "favourites_header": "⭐ Favourite Locations",
        "no_favourites": "No favourites added yet.",
        "add_to_fav": "💖 Add to Favourites",
        "remove_from_fav": "🗑 Remove from Favourites",
        "fav_added": "{} added to favourites!",
        "fav_removed": "{} removed from favourites!",
#        "detect_location": "🧭 Detect My Location",
        "show_map_favourites": "Show Favourites on Map",
        "about_header": "ℹ️ About This Project",
        "offline_notice": "Offline data used (cached).",
        "uv_low": "Low — minimal protection required.",
        "uv_moderate": "Moderate — wear sunglasses and SPF 30+.",
        "uv_high": "High — wear SPF 30+, hat, and avoid mid-day sun.",
        "uv_very_high": "Very High — extra precautions, avoid sun.",
        "uv_extreme": "Extreme — stay indoors if possible."
    },
    "hindi": {
        "title": "मौसम अब - स्मार्ट पूर्वानुमान (प्रो)",
        "tagline": "रीयल-टाइम मौसम, नक्शे, रुझान, UV, कपड़ों के सुझाव और बहुत कुछ।",
        "input_label": "📍 शहर का नाम दर्ज करें (उदाहरण: देहरादून, दिल्ली, लंदन)",
        "input_placeholder": "शहर का नाम दर्ज करें और Enter दबाएँ",
        "press_enter": "शहर के मौसम की खोज के लिए Enter दबाएँ!",
        "welcome": "स्वागत है! ऊपर शहर का नाम दर्ज करके या 'मेरा स्थान पता करें' का उपयोग करके शुरू करें।",
        "welcome_detail": "पूर्वानुमान, मानचित्र, UV, कपड़ों के सुझाव देखें और पसंदीदा सहेजें।",
        "weather": "मौसम",
        "landmark_unavailable": "पहचान चिह्न की तस्वीर उपलब्ध नहीं है।",
        "feels_like": "महसूस होता है",
        "humidity": "आर्द्रता",
        "wind_speed": "हवा की गति",
        "pressure": "दबाव",
        "severe_alert": "🚨 गंभीर मौसम चेतावनी! सावधानी बरतें।",
        "forecast_header": "📅 5-दिन का पूर्वानुमान (दोपहर)",
        "hourly_header": "⏱ अगले 24 घंटे (प्रति घंटा पूर्वानुमान)",
        "forecast_error": "त्रुटि: 5-दिन का पूर्वानुमान प्राप्त नहीं किया जा सका। एपीआई कॉन्फ़िगरेशन की जाँच करें।",
        "city_not_found": "शहर '{}' नहीं मिला! कृपया पुनः प्रयास करें।",
        "error_fetching": "मौसम डेटा प्राप्त करने में त्रुटि: {}",
        "theme_selector": "इंटरफ़ेस थीम",
        "language_selector": "भाषा चुनें",
        "light_mode": "🌞 हल्का मोड",
        "dark_mode": "🌙 गहरा मोड",
        "sunrise": "🌅 सूर्योदय",
        "sunset": "🌇 सूर्यास्त",
        "aqi": "💨 वायु गुणवत्ता सूचकांक (AQI)",
        "aqi_good": "अच्छा (1)",
        "aqi_fair": "ठीक (2)",
        "aqi_moderate": "मध्यम (3)",
        "aqi_poor": "खराब (4)",
        "aqi_very_poor": "बहुत खराब (5)",
        "country_error": "कृपया किसी देश का नाम नहीं, बल्कि एक विशिष्ट *शहर का नाम* दर्ज करें।",
        "favourites_header": "⭐ पसंदीदा स्थान",
        "no_favourites": "कोई पसंदीदा स्थान जोड़ा नहीं गया।",
        "add_to_fav": "💖 पसंदीदा में जोड़ें",
        "remove_from_fav": "🗑 पसंदीदा हटाएँ",
        "fav_added": "{} पसंदीदा में जोड़ा गया!",
        "fav_removed": "{} पसंदीदा से हटाया गया!",
#        "detect_location": "🧭 मेरा स्थान पता करें",
        "show_map_favourites": "नक्शे पर पसंदीदा दिखाएँ",
        "about_header": "ℹ️ इस परियोजना के बारे में",
        "offline_notice": "ऑफ़लाइन डेटा (कैश) का उपयोग किया गया।",
        "uv_low": "कम — न्यूनतम सुरक्षा आवश्यक।",
        "uv_moderate": "मध्यम — धूप का चश्मा और SPF 30+ लगाएँ।",
        "uv_high": "उच्च — SPF 30+, टोपी पहनें, मध्य-दिवस के सूरज से बचें।",
        "uv_very_high": "बहुत उच्च — अतिरिक्त सावधानी, सूरज से बचें।",
        "uv_extreme": "चरम — यदि संभव हो तो अंदर रहें।"
    }
}

# ---- INITIAL STATE SETUP (with favourites & cache persistence) ----
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'
if 'language' not in st.session_state:
    st.session_state['language'] = 'english'
if 'search_triggered' not in st.session_state:
    st.session_state['search_triggered'] = False
if 'current_weather_data' not in st.session_state:
    st.session_state['current_weather_data'] = None
if 'aqi_data' not in st.session_state:
    st.session_state['aqi_data'] = None

# load favourites from file (persistent across restarts)
if 'favourites' not in st.session_state:
    try:
        if os.path.exists(FAV_FILE):
            with open(FAV_FILE, 'r', encoding='utf-8') as f:
                st.session_state['favourites'] = json.load(f)
                if not isinstance(st.session_state['favourites'], list):
                    st.session_state['favourites'] = []
        else:
            st.session_state['favourites'] = []
    except Exception:
        st.session_state['favourites'] = []

# load cache dictionary
if 'cache' not in st.session_state:
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                st.session_state['cache'] = json.load(f)
                if not isinstance(st.session_state['cache'], dict):
                    st.session_state['cache'] = {}
        else:
            st.session_state['cache'] = {}
    except Exception:
        st.session_state['cache'] = {}

# --- UTILITY FUNCTIONS ---
def get_translation(key):
    lang = st.session_state.get('language', 'english')
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS['english'][key])

def set_search_triggered():
    st.session_state['search_triggered'] = True

def get_base64_image(image_path):
    try:
        if not os.path.exists(image_path):
            return None
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

def get_weather_background_url(main_condition):
    condition = main_condition.lower()
    if condition in ["haze", "fog", "smoke", "dust", "sand"]:
        return BACKGROUND_IMAGES.get("mist", None)
    return BACKGROUND_IMAGES.get(condition, None)

def fetch_unsplash_image_url(city_name):
    KNOWN_CITIES = {
        "amritsar": "https://images.pexels.com/photos/17798305/pexels-photo-17798305/free-photo-of-golden-temple-at-night.jpeg?auto=compress&cs=tinysrgb&w=800",
        "delhi": "https://images.pexels.com/photos/3476472/pexels-photo-3476472.jpeg?auto=compress&cs=tinysrgb&w=800",
        "mumbai": "https://images.pexels.com/photos/10203531/pexels-photo-10203531.jpeg?auto=compress&cs=tinysrgb&w=800",
        "london": "https://images.pexels.com/photos/460672/pexels-photo-460672.jpeg?auto=compress&cs=tinysrgb&w=800",
    }
    if not UNSPLASH_ACCESS_KEY:
        return KNOWN_CITIES.get(city_name.lower(), None)
    try:
        query = f"famous landmark in {city_name}"
        params = {"query": query, "per_page": 1, "client_id": UNSPLASH_ACCESS_KEY}
        response = requests.get(UNSPLASH_API_URL, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()
        if data.get('results'):
            return data['results'][0]['urls']['regular']
        else:
            return KNOWN_CITIES.get(city_name.lower(), None)
    except Exception:
        return KNOWN_CITIES.get(city_name.lower(), None)

def update_theme(theme_choice):
    st.session_state['theme'] = 'dark' if 'Dark' in theme_choice or 'गहरा' in theme_choice else 'light'

def get_temp_based_accent_color(temp, is_dark):
    try:
        temp = float(temp)
    except Exception:
        return "#6A5ACD" if not is_dark else "#4CAF50"
    if temp >= 30:
        return "#FF5733" if is_dark else "#E94E2C"
    elif temp >= 10:
        return "#4CAF50" if is_dark else "#00A896"
    else:
        return "#33AFFF" if is_dark else "#2C7ADF"

# ---- Favourites persistence helpers ----
def save_favourites_to_file():
    try:
        with open(FAV_FILE, "w", encoding='utf-8') as f:
            json.dump(st.session_state.get('favourites', []), f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def add_to_favourites(city_name):
    city_title = city_name.title()
    if city_title not in st.session_state['favourites']:
        st.session_state['favourites'].append(city_title)
        save_favourites_to_file()
        st.success(get_translation('fav_added').format(city_title))
    else:
        st.info(f"⭐ {city_title} is already in your favourites!")

def remove_from_favourites(city_name):
    city_title = city_name.title()
    if city_title in st.session_state['favourites']:
        st.session_state['favourites'].remove(city_title)
        save_favourites_to_file()
        st.success(get_translation('fav_removed').format(city_title))

# ---- Cache helpers (offline mode) ----
def save_cache():
    try:
        with open(CACHE_FILE, "w", encoding='utf-8') as f:
            json.dump(st.session_state.get('cache', {}), f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def cache_city_data(city, data):
    if not city or not data:
        return
    st.session_state.setdefault('cache', {})
    st.session_state['cache'][city.title()] = {
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    save_cache()

def load_cached_city(city):
    c = st.session_state.get('cache', {}).get(city.title())
    if c:
        return c.get('data')
    return None

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Weather Now", page_icon="☁", layout="wide")

# ---- GLOBAL ACCENT COLOR ----
def get_global_accent_color():
    return "#9E9E9E" if st.session_state.get("theme", "light") == "dark" else "#4F5D75"

accent_color = get_global_accent_color()

# ---- DYNAMIC CSS (keeps original appearance) ----
def apply_dynamic_css(dynamic_bg_style, accent_color):
    is_dark = st.session_state.theme == 'dark'
    bg_color_main = "#1e1e1e" if is_dark else "#333333"
    text_color = "#f0f2f6" if is_dark else "#333333"
    card_bg = "rgba(30, 30, 30, 0.75)" if is_dark else "rgba(255, 255, 255, 0.85)"
    input_bg = "rgba(50, 50, 50, 0.7)" if is_dark else "rgba(255, 255, 255, 0.6)"
    border_color = "rgba(255, 255, 255, 0.3)" if is_dark else "rgba(255, 255, 255, 0.8)"
    metric_bg = "rgba(50, 50, 50, 0.4)" if is_dark else "rgba(255, 255, 255, 0.6)"
    sidebar_bg = "#1f1f1f" if is_dark else "#f5f5f5"
    sidebar_text = "#f0f2f6" if is_dark else "#222222"
    sidebar_button_bg = "#2a2a2a" if is_dark else "#ffffff"
    sidebar_border = "#444444" if is_dark else "#cccccc"

    css = f"""
    <style>
    .stApp {{
        background: none !important;
        color: {bg_color_main};
    }}
    .stApp::before {{
        content: "";
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: {dynamic_bg_style} !important;
        background-size: cover !important; background-position: center !important;
        z-index: -1; 
        filter: brightness({0.9 if is_dark else 1.0});
    }}
    .stText, .stMarkdown, .stSubheader, .stTitle, h1, h2, h3, h4, p, label {{
        color: {text_color} !important;
    }}
    .card {{
        background: {card_bg}; backdrop-filter: blur(15px);
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.15); border:1px solid {border_color};
    }}
    .city-image {{ width:100%; max-height:350px; height:100%; border-radius:20px; object-fit:cover; }}
    div[data-testid="stMetric"] > div {{ background: {metric_bg}; border-radius: 15px; padding: 8px 10px; }}
    .main-weather-card h1 {{ font-size: 5rem; color: {text_color}; margin-bottom:-15px !important; margin-top:0px !important; }}
    /* ===== SIDEBAR FIX ===== */
    section[data-testid="stSidebar"] {{
    background: {sidebar_bg} !important;
}}



    section[data-testid="stSidebar"] * {{
        color: {sidebar_text} !important;
    }}

    section[data-testid="stSidebar"] button {{
        background: {sidebar_button_bg} !important;
        color: {sidebar_text} !important;
        border: 1px solid {sidebar_border} !important;
        border-radius: 10px !important;
    }}

    section[data-testid="stSidebar"] button:hover {{
        opacity: 0.85;
    }}

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---- LOCATION DETECTION ----
#def detect_location_ip():
#    """Detect approximate location using IP geolocation (ipapi.co)."""
# try:
#     res = requests.get("https://ipapi.co/json/", timeout=6).json()
#     city = res.get("city")
#     country = res.get("country_name")
#     lat = res.get("latitude") or res.get("lat")
#     lon = res.get("longitude") or res.get("lon")
#     if not (city and lat and lon):
#         # try ipinfo
#         r2 = requests.get("https://ipinfo.io/json", timeout=6).json()
#         loc = r2.get("loc")
#         if loc:
#             lat, lon = loc.split(",")
#         city = city or r2.get("city")
#         country = country or r2.get("country")
#     return {"city": city, "country": country, "lat": float(lat) if lat else None, "lon": float(lon) if lon else None}
# except Exception:
#     return {"city": None, "country": None, "lat": None, "lon": None}

# ---- WEATHER FETCHING FUNCTIONS ----
def fetch_weather_basic(city):
    """Fetch current weather (same as before). Returns JSON or None. Uses cache if offline."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=8).json()
        if res.get("cod") != 200:
            return None
        # cache
        cache_city_data(city, res)
        return res
    except Exception:
        # try cache
        cached = load_cached_city(city)
        if cached:
            st.warning(get_translation("offline_notice"))
            return cached
        return None

def fetch_onecall(lat, lon):
    """Fetch One Call data (daily, current) for UV, 7-day, etc."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={API_KEY}&units=metric"
        res = requests.get(url, timeout=8).json()
        if res:
            # optionally cache using latlon key
            key = f"{lat:.4f},{lon:.4f}"
            st.session_state.setdefault('cache', {})
            st.session_state['cache'][key] = {"timestamp": datetime.utcnow().isoformat(), "data": res}
            save_cache()
            return res
    except Exception:
        # try cached onecall by latlon key
        key = f"{lat:.4f},{lon:.4f}"
        cached = st.session_state.get('cache', {}).get(key)
        if cached:
            st.warning(get_translation("offline_notice"))
            return cached.get('data')
    return None

def fetch_aqi(lat, lon):
    try:
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        aqi_res = requests.get(aqi_url, timeout=8).json()
        if aqi_res.get("list"):
            aqi_val = aqi_res["list"][0]["main"]["aqi"]
            key_map = {1: 'aqi_good', 2: 'aqi_fair', 3: 'aqi_moderate', 4: 'aqi_poor', 5: 'aqi_very_poor'}
            aqi_description_key = key_map.get(aqi_val)
            return get_translation(aqi_description_key)
    except Exception:
        return None

# ---- Clothing suggestion & UV advice ----
def clothing_suggestion(temp_c, humidity, wind_speed):
    tips = []
    try:
        t = float(temp_c)
    except Exception:
        return "No suggestion available."

    if t <= 5:
        tips.append("Heavy winter jacket, gloves, warm hat.")
    elif t <= 15:
        tips.append("Jacket or sweater; layers recommended.")
    elif t <= 25:
        tips.append("Light jacket or long sleeves.")
    else:
        tips.append("T-shirt / light clothing; stay hydrated.")

    # humidity/wind modifiers
    try:
        h = float(humidity)
        w = float(wind_speed)
        if h >= 80 and t >= 20:
            tips.append("High humidity — breathable fabrics recommended.")
        if w >= 10 and t <= 15:
            tips.append("Windy — consider a windbreaker.")
    except Exception:
        pass

    return " ".join(tips)

def uv_advice(uvi):
    try:
        u = float(uvi)
    except Exception:
        return ""
    if u < 3:
        return get_translation("uv_low")
    elif u < 6:
        return get_translation("uv_moderate")
    elif u < 8:
        return get_translation("uv_high")
    elif u < 11:
        return get_translation("uv_very_high")
    else:
        return get_translation("uv_extreme")

# ---- MAP VIEW (folium) ----
def show_map(lat, lon, city_name=None, show_favourites=False):
    m = folium.Map(location=[lat, lon], zoom_start=10, tiles="OpenStreetMap")
    folium.Marker([lat, lon], popup=f"{city_name or 'Location'}").add_to(m)
    if show_favourites and st.session_state.get('favourites'):
        # try to geocode favourites using OpenWeather (simple approach)
        for fav in st.session_state['favourites']:
            try:
                r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={fav}&limit=1&appid={API_KEY}", timeout=6).json()
                if r:
                    latf = r[0].get('lat'); lonf = r[0].get('lon')
                    folium.CircleMarker(location=[latf, lonf], radius=6, color="red", fill=True, popup=fav).add_to(m)
            except Exception:
                continue
    st_data = st_folium(m, width=700, height=450)
    return st_data

# ---- HOURLY and 5-day render functions (kept similar) ----
def render_hourly_forecast(city):
    T = get_translation
    text_color = "#f0f2f6" if st.session_state.theme == 'dark' else "#333333"
    accent = accent_color

    try:
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        forecast_res = requests.get(forecast_url, timeout=8).json()
    except Exception:
        forecast_res = None

    if forecast_res and forecast_res.get("cod") == "200":
        hourly_data = forecast_res["list"][:8]  # next 8 entries
        st.markdown(f"<h2 style='color: {accent}; margin-top: 20px;'>{T('hourly_header')}</h2>", unsafe_allow_html=True)
        hourly_cols = st.columns(len(hourly_data))
        for i, info in enumerate(hourly_data):
            time_formatted = datetime.strptime(info["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I %p").lstrip('0')
            condition = info["weather"][0]["main"].lower()
            icon_map = {
                "clear": "☀", "clouds": "☁", "rain": "🌧", "thunderstorm": "⛈",
                "snow": "❄", "drizzle": "☔", "mist": "🌫", "haze": "🌫",
            }
            icon = icon_map.get(condition, "❓")
            translated_condition = info["weather"][0]["description"].title()
            with hourly_cols[i]:
                st.markdown(
                    f"""
                    <div class="card forecast-card" style="padding: 10px; text-align: center; height: 100%;">
                        <h4 style='margin-bottom: 0px; color: {accent};'>{time_formatted}</h4>
                        <p style='font-size: 1.5rem; margin-top: 5px; margin-bottom: 5px;'>{icon}</p>
                        <p style='font-size: 1.2rem; font-weight: bold; margin: 0; color: {text_color};'>{info["main"]["temp"]:.0f}°C</p>
                        <p style='font-size: 0.7rem; opacity: 0.8; margin-top: 5px; color: {text_color}; white-space: normal;'>{translated_condition}</p>
                    </div>
                    """, unsafe_allow_html=True
                )
        st.markdown("---")
    else:
        st.warning(get_translation("forecast_error"))

def render_5day_forecast(city):
    T = get_translation
    accent = accent_color
    text = "#f0f2f6" if st.session_state.theme == 'dark' else "#333333"
    try:
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        forecast_res = requests.get(forecast_url, timeout=8).json()
    except Exception:
        forecast_res = None

    st.markdown(f"<h2 style='color: {accent};'>{T('forecast_header')}</h2>", unsafe_allow_html=True)
    if forecast_res and forecast_res.get("cod") == "200":
        forecast_days = {}
        for entry in forecast_res["list"]:
            if "12:00:00" in entry["dt_txt"]:
                date = entry["dt_txt"].split(" ")[0]
                if len(forecast_days) < 5:
                    forecast_days[date] = entry
        forecast_cols = st.columns(min(len(forecast_days), 5))
        for i, (date, info) in enumerate(list(forecast_days.items())[:5]):
            date_formatted_day = datetime.strptime(date, "%Y-%m-%d").strftime("%a")
            date_formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%b %d")
            condition = info["weather"][0]["main"].lower()
            icon_map = {
                "clear": "☀", "clouds": "☁", "rain": "🌧", "thunderstorm": "⛈",
                "snow": "❄", "drizzle": "☔", "mist": "🌫", "haze": "🌫",
            }
            icon = icon_map.get(condition, "❓")
            with forecast_cols[i]:
                translated_condition = info["weather"][0]["description"].title()
                st.markdown(
                    f"""
                    <div class="card forecast-card" style="padding: 15px; text-align: center;">
                        <h4 style='margin-bottom: 0px; color: {accent};'>{date_formatted_day}</h4>
                        <p class="date-text">{date_formatted_date}</p>
                        <p style='font-size: 2rem; margin-top: 0; margin-bottom: 10px;'>{icon}</p>
                        <p style='font-size: 1.5rem; font-weight: bold; margin: 0; color: {text};'>{info["main"]["temp"]:.0f}°C</p>
                        <p style='font-size: 0.8rem; opacity: 0.8; margin-top: 5px; color: {text};'>{translated_condition}</p>
                    </div>
                    """, unsafe_allow_html=True
                )
    else:
        st.warning(get_translation("forecast_error"))

# ---- Climate trend graph (7-day) using One Call daily data ----
def render_7day_trend(onecall_data, city):
    if not onecall_data or 'daily' not in onecall_data:
        return
    daily = onecall_data['daily'][:7]
    dates = [datetime.utcfromtimestamp(d['dt']).strftime('%a %d') for d in daily]
    temps = [d['temp']['day'] for d in daily]
    plt.figure(figsize=(9,3))
    plt.plot(dates, temps, marker='o')
    plt.title(f"7-day temperature trend — {city.title()}")
    plt.xlabel("Day")
    plt.ylabel("Temp (°C)")
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

# ---- MAIN render weather results (integrates UV, clothing, map, graph) ----
def render_weather_results(city, current_res):
    T = get_translation
    if not current_res:
        st.error(T("city_not_found").format(city.title()))
        return

    is_dark = st.session_state.theme == 'dark'
    accent = get_temp_based_accent_color(current_res['main']['temp'], is_dark)
    text = "#f0f2f6" if is_dark else "#333333"

    image_url = fetch_unsplash_image_url(city)
    lat, lon = current_res['coord']['lat'], current_res['coord']['lon']
    aqi_text = fetch_aqi(lat, lon)

    # Try One Call for UV & daily
    onecall = fetch_onecall(lat, lon)
    uvi = None
    if onecall and 'current' in onecall:
        uvi = onecall['current'].get('uvi')

    # Convert timestamps
    sunrise_ts = current_res['sys']['sunrise'] + current_res['timezone']
    sunset_ts = current_res['sys']['sunset'] + current_res['timezone']
    sunrise_time = datetime.utcfromtimestamp(sunrise_ts).strftime('%I:%M %p').lstrip('0')
    sunset_time = datetime.utcfromtimestamp(sunset_ts).strftime('%I:%M %p').lstrip('0')

    left_col_main, right_col_main = st.columns([1.5, 3])

    with left_col_main:
        if image_url:
            st.markdown(f'<img class="city-image" src="{image_url}" alt="{city} landmark">', unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color: {accent};'>🏙 {city.title()} {T('weather')}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: {text};'>{T('landmark_unavailable')}</p>", unsafe_allow_html=True)

    with right_col_main:
        st.markdown('<div class="card main-weather-card">', unsafe_allow_html=True)
        if image_url:
            st.markdown(f"<h2 style='color: {accent}; margin-top: 0px;'>🏙 {city.title()} {T('weather')}</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <h1 class="main-temp">{current_res['main']['temp']:.0f} °C</h1>
            <h3 class="main-condition">{current_res['weather'][0]['description'].title()}</h3>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(T("feels_like"), f"{current_res['main']['feels_like']:.0f} °C")
        col2.metric(T("humidity"), f"{current_res['main']['humidity']} %")
        col3.metric(T("wind_speed"), f"{current_res['wind']['speed']} m/s")
        col4.metric(T("pressure"), f"{current_res['main']['pressure']} hPa")

        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)

        col5, col6, col7 = st.columns(3)
        col5.metric(T("sunrise"), sunrise_time)
        col6.metric(T("sunset"), sunset_time)
        col7.metric(T("aqi"), aqi_text if aqi_text else "N/A")

        # UV info
        if uvi is not None:
            st.markdown(f"**UV Index:** {uvi} — {uv_advice(uvi)}")

        st.markdown('</div>', unsafe_allow_html=True)

    main_condition = current_res['weather'][0]['main'].lower()
    if main_condition in ["thunderstorm", "rain", "snow"]:
        st.error(T("severe_alert"))

    # FAVOURITE BUTTON
    city_title = city.title()
    if city_title not in st.session_state['favourites']:
        if st.button(f"{get_translation('add_to_fav')}  {city_title}", key=f"addfav_{city_title}"):
            add_to_favourites(city_title)
    else:
        if st.button(f"{get_translation('remove_from_fav')}  {city_title}", key=f"remfav_{city_title}"):
            remove_from_favourites(city_title)

    # Clothing suggestion
    clothes = clothing_suggestion(current_res['main']['temp'], current_res['main'].get('humidity', 0), current_res['wind'].get('speed', 0))
    st.markdown(f"**Clothing suggestion:** {clothes}")

    # Map view
    st.markdown("### 🗺 Map View")
    # small controls
    map_col1, map_col2 = st.columns([1,3])
    with map_col1:
        show_favs_on_map = st.checkbox(get_translation("show_map_favourites"), value=False)
    with map_col2:
        # display map (centered at city)
        show_map(lat, lon, city_title, show_favourites=show_favs_on_map)

    # Hourly + 5-day
    render_hourly_forecast(city)
    render_5day_forecast(city)

    # 7-day trend graph using One Call
    if onecall:
        render_7day_trend(onecall, city)

# ---- fetch_weather_and_data (keeps country checks + caching fallback) ----
def fetch_weather_and_data(city):
    T = get_translation
    common_countries = [
        "india", "usa", "china", "canada", "brazil", "russia",
        "germany", "france", "japan", "australia", "uk", "italy",
        "spain", "mexico", "pakistan", "indonesia"
    ]
    if city.lower() in common_countries:
        st.error(T("country_error"))
        st.session_state['current_weather_data'] = None
        return False

    try:
        current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        current_res = requests.get(current_url, timeout=8).json()
        if current_res.get("cod") != 200:
            # fallback to cache
            cached = load_cached_city(city)
            if cached:
                st.warning(get_translation("offline_notice"))
                st.session_state['current_weather_data'] = cached
                return True
            st.error(T("city_not_found").format(city.title()))
            st.session_state['current_weather_data'] = None
            return False

        returned_name = current_res.get('name', '').lower()
        if len(city) <= 6 and city.lower() in common_countries and returned_name not in city.lower():
            st.error(T("country_error"))
            st.session_state['current_weather_data'] = None
            return False

        # cache and save
        st.session_state['current_weather_data'] = current_res
        cache_city_data(city, current_res)
        return True
    except Exception as e:
        # network error: try cache
        cached = load_cached_city(city)
        if cached:
            st.warning(get_translation("offline_notice"))
            st.session_state['current_weather_data'] = cached
            return True
        st.error(T("error_fetching").format(str(e)))
        st.session_state['current_weather_data'] = None
        return False

# ---- DISPLAY APP CONTENT (main UI) ----
def display_app_content():
    T = get_translation
    accent = accent_color
    text = "#f0f2f6" if st.session_state.theme == 'dark' else "#333333"

    col_left_pad, col_center_content, col_right_pad = st.columns([0.5, 6, 0.5])

    with col_center_content:
        st.markdown('<div class="centered-title">', unsafe_allow_html=True)
        st.title(T("title"))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div class='centered-tagline'>{T('tagline')}</div>",
            unsafe_allow_html=True
        )
        st.markdown("---")

        # Input & detection
        leftin, rightin = st.columns([3,1])
        with leftin:
            st.text_input(T("input_label"), key="city_input", on_change=set_search_triggered, placeholder=T("input_placeholder"))
        
#        with rightin:
#            if st.button(T("detect_location")):
#                loc = detect_location_ip()
#                if loc.get('city'):
#                    st.session_state['city_input'] = loc['city']
#                    st.session_state['search_triggered'] = True
#               else:
#                    st.warning("Could not detect location.")

        # small hint about favourites
        if st.session_state.get('favourites'):
            st.markdown(f"<small style='color: {accent};'>⭐ {T('favourites_header')}: {', '.join(st.session_state['favourites'][:5])}</small>", unsafe_allow_html=True)

        city = st.session_state.get('city_input')

        if city and st.session_state.get('search_triggered') and st.session_state['current_weather_data'] is None:
            st.info(T("press_enter"))
        elif st.session_state['current_weather_data'] is None:
            st.markdown(f'''
                <div class="card" style="text-align: center; padding: 50px;">
                    <h2 style="color: {accent};">{T('welcome')}</h2>
                    <p style="color: {text};">{T('welcome_detail')}</p>
                </div>
            ''', unsafe_allow_html=True)

    # Trigger API fetch if search requested
    if st.session_state.get('search_triggered', False) and city:
        if fetch_weather_and_data(city):
            st.session_state['search_triggered'] = False
        else:
            st.session_state['search_triggered'] = False

    # Render if data exists
    if st.session_state['current_weather_data'] and city:
        render_weather_results(city, st.session_state['current_weather_data'])

# ---- SIDEBAR (favourites, about, theme, language) ----
def sidebar_ui():
    st.sidebar.markdown(f"## {get_translation('favourites_header')}")
    if st.session_state.get('favourites'):
        for fav in st.session_state['favourites']:
            col1, col2 = st.sidebar.columns([3,1])
            with col1:
                if st.button(fav, key=f"fav_load_{fav}"):
                    if fetch_weather_and_data(fav):
                        st.session_state['search_triggered'] = False
                        st.session_state['city_input'] = fav
            with col2:
                if st.button("🗑", key=f"fav_rm_{fav}", help=get_translation('remove_from_fav')):
                    remove_from_favourites(fav)
    else:
        st.sidebar.info(get_translation('no_favourites'))

    st.sidebar.markdown("---")
    # Map toggle: show all favourites on map quickly
    if st.sidebar.button("Show My Favourites on Map"):
        # If there is at least one favourite, open a small map page
        if st.session_state.get('favourites'):
            st.sidebar.write("Opening map in main view...")
            # we will detect first favourite coords and show in main
            first = st.session_state['favourites'][0]
            # fetch location
            try:
                r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={first}&limit=1&appid={API_KEY}", timeout=6).json()
                if r:
                    lat = r[0].get('lat'); lon = r[0].get('lon')
                    show_map(lat, lon, first, show_favourites=True)
            except Exception:
                st.sidebar.warning("Unable to show favourites map right now.")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"## {get_translation('language_selector')}")
    st.sidebar.radio(" ", ['english', 'hindi'], key='language', index=0 if st.session_state.language == 'english' else 1, format_func=lambda k: 'English' if k=='english' else 'हिंदी (Hindi)')
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"## {get_translation('theme_selector')}")
    st.sidebar.radio(" ", [get_translation('light_mode'), get_translation('dark_mode')], key='theme_choice', index=0 if st.session_state.theme == 'light' else 1, on_change=lambda: update_theme(st.session_state.theme_choice))
    st.sidebar.markdown("---")
    # About / Project info
    with st.sidebar.expander(get_translation('about_header'), expanded=False):
        st.markdown("""
        **Weather Now - Pro**  
        Features:
        - Real-time current weather (OpenWeather)  
        - Hourly & 5-day forecast  
        - 7-day climate trend graph (One Call)  
        - Map view (folium) & detect location (IP)  
        - UV index and clothing suggestions  
        - Favourite locations (persistent)  
        - Offline cache for last successful results  
        
        **Tech stack:** Python, Streamlit, OpenWeather API, Folium, Matplotlib  
        **Files created:** favourites.json, cache.json (in app folder)
        """)
    st.sidebar.markdown("---")
    st.sidebar.caption("Made for PBL / Portfolio — customize keys & assets before publishing.")

# ---- APP ENTRY ----
# Determine accent and background (try to reuse logic from earlier)
local_image_path = "bright_day_light.jpg"
base64_image = get_base64_image(local_image_path)
if base64_image:
    default_bg = f"url('data:image/jpeg;base64,{base64_image}') no-repeat center center fixed"
else:
    default_bg = 'linear-gradient(135deg, #CFD8DC 0%, #B0BEC5 50%, #78909C 100%)' if st.session_state.theme=='light' else 'linear-gradient(135deg, #1C2833 0%, #2C3E50 50%, #4A637A 100%)'
dynamic_bg_style = default_bg


apply_dynamic_css(dynamic_bg_style, accent_color)

# render sidebar & main
sidebar_ui()
display_app_content()
