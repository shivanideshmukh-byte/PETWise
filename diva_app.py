import streamlit as st
import requests
import re
import json
from math import ceil

# ------------------ SESSION STATE -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ------------------ FIREBASE AUTH -------------------
# 👉 paste your Firebase details below
FIREBASE_API_KEY = "AIzaSyAbS3SdyPNRSNaUov0n4MeWFHTpoxBc4jc"

SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
LOGIN_URL  = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"


def firebase_signup(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(SIGNUP_URL, data=payload)
    return r.json()


def firebase_login(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(LOGIN_URL, data=payload)
    return r.json()


# ---------------- LOGIN PAGE ----------------
def login_page():

    st.title("🔐 Login / Sign Up")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    action = st.radio("Action", ["Login", "Sign Up"])

    if st.button("Confirm"):

        if action == "Login":
            result = firebase_login(email, password)
        else:
            result = firebase_signup(email, password)

        if "idToken" in result:
            st.session_state.logged_in = True
            st.success("Logged in successfully")
        else:
            st.error(result.get("error", {}).get("message", "Failed"))


# ---------------- PET FORECAST ENGINE ----------------
def pet_forecast_answer(q):

    q = q.lower()

    # extract city
    m = re.search(r"in ([a-zA-Z\s]+)", q)
    city = m.group(1).strip().title() if m else "Hyderabad"

    # extract year
    year_match = re.findall(r"(20\d{2})", q)
    year = int(year_match[0]) if year_match else 2030

    # Model constants (placeholder CPCB-style baseline assumption)
    base_year = 2025
    base_value = 145000  # tonnes/year baseline
    growth_rate = 0.065  # 6.5% annual

    years_ahead = year - base_year
    forecast_value = round(base_value * ((1 + growth_rate) ** years_ahead), 2)

    return f"""
📍 **City:** {city}
📅 **Year:** {year}

♻ **Projected PET waste:**  
👉 **{forecast_value:,} tonnes/year**

📌 Model = Baseline ({base_year}) × (1 + 6.5%) ^ years
"""


# ---------------- AQI LIVE API ----------------
# optional — works only if user adds a free key
AQI_API_KEY = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"   # << paste WAQI API key here

def get_aqi(city):

    if AQI_API_KEY == "":
        return "🔌 Live AQI will be enabled after API key integration."

    url = f"https://api.waqi.info/feed/{city}/?token={AQI_API_KEY}"
    d = requests.get(url).json()

    if d["status"] != "ok":
        return "AQI not available"

    aqi = d["data"]["aqi"]
    return f"🌫 Current AQI in {city} = **{aqi}**"


# ---------------- GIS MAP (Hyderabad demo) ----------------
def show_hyd_map():

    st.subheader("🗺 Hyderabad PET & AQI Zones (demo map)")

    st.map(
        data = {
            "lat": [17.3850, 17.4500, 17.3000],
            "lon": [78.4867, 78.5000, 78.4000],
        },
        zoom=10
    )

    st.info("This is demo GIS layer. Live CPCB shapefiles can be added later.")


# ---------------- ASSISTANT APP ----------------
def diva_app():

    st.title("🌿 Diva — AI Environmental Decision Support Assistant")

    # input mode
    mode = st.radio("Ask via:", ["Typing"], horizontal=True)

    q = st.text_input("Your question")

    if st.button("Ask Diva"):

        ans = pet_forecast_answer(q)

        st.success(ans)

        st.markdown("""
<script>
var u=new SpeechSynthesisUtterance(`Diva says """ + ans + """`);
u.pitch=1.3; u.rate=1.0;
u.voice=speechSynthesis.getVoices().find(v=>v.name.toLowerCase().includes("female"))
      || speechSynthesis.getVoices()[0];
speechSynthesis.speak(u);
</script>
""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🌍 Live AQI (India cities)")

    city = st.text_input("City name for AQI lookup")
    if st.button("Check AQI"):
        st.info(get_aqi(city))

    st.divider()
    show_hyd_map()

    st.caption("🇮🇳 India scope ready • APIs and CPCB verified datasets can be plugged in")


# ---------------- ROUTER ----------------
if not st.session_state.logged_in:
    login_page()
else:
    diva_app()
