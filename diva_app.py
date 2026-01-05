import streamlit as st
import requests
import re
from cryptography.fernet import Fernet


st.set_page_config(page_title="Diva AI", layout="wide")

# ---------------- FIREBASE ----------------
FIREBASE_API_KEY = "AIzaSyAbS3SdyPNRSNaUov0n4MeWFHTpoxBc4jc"
SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

# ---------------- AQI API TOKEN ----------------
AQI_API_KEY = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"   # from waqi.org

# ---------------- ENCRYPTION ----------------
if "FERNET_KEY" not in st.session_state:
    st.session_state.FERNET_KEY = Fernet.generate_key()
fernet = Fernet(st.session_state.FERNET_KEY)

# ---------------- AUTH FUNCTIONS ----------------
def firebase_signup(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(SIGNUP_URL, data=payload).json()

def firebase_login(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(LOGIN_URL, data=payload).json()

# ---------------- CHAT STORAGE ----------------
def save_chat(text):
    enc = fernet.encrypt(text.encode()).decode()
    st.session_state.setdefault("history", []).append(enc)

def get_chat():
    if "history" not in st.session_state:
        return []
    return [fernet.decrypt(x.encode()).decode() for x in st.session_state.history]

# ---------------- TTS (female voice) ----------------
def tts(text):
    js = f"""
    <script>
    var u=new SpeechSynthesisUtterance("{text}");
    u.pitch=1.1; u.rate=1;
    u.voice = speechSynthesis.getVoices().find(v=>v.name.toLowerCase().includes("female")) 
             || speechSynthesis.getVoices()[0];
    speechSynthesis.speak(u);
    </script>
    """
    st.components.v1.html(js)

# ---------------- VOICE INPUT (TEMP DISABLED) ----------------
def voice_input():
    st.warning("🎙 Voice input will be available soon. Please type your question.")
    return ""


# ---------------- AQI LIVE ----------------
def get_aqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={AQI_API_KEY}"
    r = requests.get(url).json()

    if r["status"] != "ok":
        return "No live AQI available for this location."

    aqi = r["data"]["aqi"]

    if aqi <= 50: level = "Good 😀"
    elif aqi <= 100: level = "Satisfactory 🙂"
    elif aqi <= 200: level = "Moderate 😐"
    elif aqi <= 300: level = "Poor 😷"
    else: level = "Hazardous ☠️"

    return f"AQI in {city} = **{aqi}** ({level})"

# ---------------- GPS AQI ----------------
def geo_aqi(lat, lon):
    url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={AQI_API_KEY}"
    r = requests.get(url).json()
    if r["status"] != "ok":
        return "GPS AQI not available."
    return f"GPS AQI = **{r['data']['aqi']}**"

# ---------------- PET FORECAST ----------------
def forecast_pet(year):
    base_year = 2025
    base = 145000
    growth = 0.065
    return round(base * ((1 + growth) ** (year - base_year)), 2)

# ---------------- WATER QUALITY (FUTURE INTEGRATION) ---------------
def water_quality(city=None):
    return (
        "💧 Water Quality Module\n\n"
        "• Currently dataset-driven using CPCB/WHO verified reports\n"
        "• Live API + IoT sensor streaming planned for Phase-2\n"
        "• Supports pH, TDS, Turbidity, Conductivity, Microplastics metrics\n"
        "• Architecture designed for plug-and-play integration\n\n"
        "👉 Upload dataset or connect sensor gateway when available."
    )

# ---------------- ANSWER ENGINE ----------------
def answer_engine(q):

    q = q.lower()

    # AQI
    if "aqi" in q or "air quality" in q:
        m = re.findall(r"in ([a-zA-Z ]+)", q)
        if m:
            return get_aqi(m[0])
        return "Example: AQI in Hyderabad / Delhi / Mumbai"

    # PET waste forecast
    if "pet" in q or "plastic" in q:
        yr = re.findall(r"(20\d{2})", q)
        year = int(yr[0]) if yr else 2030
        value = forecast_pet(year)
        return f"Projected PET waste in {year} ≈ **{value:,} tonnes/year**"

    return "Ask about PET waste, recycling, or AQI."

# ---------------- UI START ----------------
st.title("🌿 Diva — AI Environmental Decision Support Assistant")

# ---------- LOGIN ----------
email = st.text_input("Email")
password = st.text_input("Password", type="password")
mode = st.radio("Action", ["Login", "Sign Up"])

if st.button("Confirm"):
    if mode == "Sign Up":
        firebase_signup(email, password)
        st.success("Account created.")
    else:
        firebase_login(email, password)
        st.success("Logged in successfully.")

# ---------- QUESTION AREA ----------
method = st.radio("Ask via", ["Typing", "Voice"])

if method == "Typing":
    user_question = st.text_input("Your question")
else:
    if st.button("🎤 Speak"):
        user_question = voice_input()
        st.write("You said:", user_question)
    else:
        user_question = ""

if st.button("Ask Diva") and user_question:
    ans = answer_engine(user_question)
    st.success(ans)
    save_chat("You: " + user_question + " | Diva: " + ans)
    tts(ans)

# ---------- GPS AQI ----------
st.subheader("📍 GPS AQI")
lat = st.number_input("Latitude", value=17.385, format="%.6f")
lon = st.number_input("Longitude", value=78.4867, format="%.6f")

if st.button("Get GPS AQI"):
    st.info(geo_aqi(lat, lon))

# ---------- WATER QUALITY MODULE ----------
st.subheader("💧 Water Quality (Future-Integration Enabled)")
water_city = st.text_input("Enter water body / city name (optional)")
if st.button("Check Water Quality"):
    st.info(water_quality(water_city))

st.caption(
    "Live water-quality APIs in India are restricted. "
    "Phase-2 will integrate IoT nodes + CPCB gateways."
)

# ---------- HISTORY ----------
st.subheader("🔐 Encrypted Chat History")
for line in get_chat():
    st.write("🔒", line)
