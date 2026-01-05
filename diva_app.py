import streamlit as st
from cryptography.fernet import Fernet
import json
import pandas as pd
import re
import math
import requests
from cryptography.fernet import Fernet

st.set_page_config(page_title="Diva AI", layout="wide")

# -------------------------------------------------------------------------------------
# 🔐 PASTE YOUR FIREBASE SDK CONFIG VALUES HERE
# -------------------------------------------------------------------------------------
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAbS3SdyPNRSNaUov0n4MeWFHTpoxBc4jc",
    "authDomain": "diva-ai-environment.firebaseapp.com",
    "projectId": "diva-ai-environment",
    "storageBucket": "diva-ai-environment.firebasestorage.app",
    "messagingSenderId": "451052754798",
    "appId": "1:451052754798:web:5823b31cf5b45b34dcd37f"
}

FIREBASE_API_KEY = FIREBASE_CONFIG["apiKey"]

# -------------------------------------------------------------------------------------
# 🔑 Encryption key – generated once
# -------------------------------------------------------------------------------------
if "FERNET_KEY" not in st.session_state:
    st.session_state.FERNET_KEY = Fernet.generate_key()
fernet = Fernet(st.session_state.FERNET_KEY)

# -------------------------------------------------------------------------------------
# 🔥 Firebase Auth REST endpoints
# -------------------------------------------------------------------------------------
SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

# -------------------------------------------------------------------------------------
# 👤 User account functions
# -------------------------------------------------------------------------------------
def firebase_signup(email, password):
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(SIGNUP_URL, data=payload)
    return r.json()
def firebase_login(email, password):
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    r = requests.post(LOGIN_URL, data=payload)

    return r.json()

# -------------------------------------------------------------------------------------
# 💾 secure encrypted chat store per user
# -------------------------------------------------------------------------------------
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []

def add_chat(message):
    encrypted = fernet.encrypt(message.encode())
    st.session_state.chat_log.append(encrypted)

def get_chats():
    return [fernet.decrypt(m).decode() for m in st.session_state.chat_log]

# -------------------------------------------------------------------------------------
# 🧭 AUTH PAGES
# -------------------------------------------------------------------------------------
def login_page():
    st.title("🔐 Secure Login – Diva AI")

    tab1, tab2 = st.tabs(["🔓 Login", "🆕 Create Account"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            result = firebase_login(email, password)

            if "idToken" in result:
                st.session_state["user"] = email
                st.success("Login successful 🎉")
                st.rerun()

            else:
                st.error(result.get("error", {}).get("message", "Login failed"))

    with tab2:
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            result = firebase_signup(email, password)

            if "idToken" in result:
                st.success("Account created ✔ You can now log in.")
            else:
                st.error(result.get("error", {}).get("message", "Signup failed"))

# -------------------------------------------------------------------------------------
# 🎤 Female voice (browser based)
# -------------------------------------------------------------------------------------
def tts(text):
    js = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.pitch = 1;
    msg.rate = 1;
    msg.voice = speechSynthesis.getVoices()[1];
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

# -------------------------------------------------------------------------------------
# 🌍 MAIN APP (after login)
# -------------------------------------------------------------------------------------
def main_app():

    st.sidebar.success(f"Logged in as {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


    st.title("🌿 Diva – AI Environmental Assistant")

    user_question = st.text_input("Ask Diva anything about PET, waste, or AQI:")


def forecast_pet(year):
    base_year = 2025
    base_value = 145000  # tonnes/year (baseline estimate – can be updated later)
    growth_rate = 0.065   # 6.5% annual growth estimate
    years = year - base_year
    return round(base_value * ((1 + growth_rate) ** years), 2)


def answer_engine(q):

    q = q.lower()

    # find year in question
    year_match = re.findall(r"(20\d{2})", q)
    year = int(year_match[0]) if year_match else 2030

    # PET waste baseline + growth model
    base_year = 2025
    base_value = 145000   # tonnes per year (example baseline)
    growth_rate = 0.065   # 6.5 %

    years_ahead = year - base_year
    forecast_value = round(base_value * ((1 + growth_rate) ** years_ahead), 2)

    answer = f"""
    📌 **Projected PET waste in {year}:** **{forecast_value:,} tonnes/year**

    🧮 Method:
    • Baseline ({base_year}) = {base_value:,} tonnes  
    • Growth rate = 6.5% annually  
    • Model = baseline × (1+g)^years
    """

    return answer.strip()

    # -----------------------------
    # AQI questions
    # -----------------------------
    if "aqi" in ql or "air quality" in ql:

        if "meaning" in ql or "what is" in ql:
            return "AQI (Air Quality Index) indicates pollution level: 0–50 Good, 51–100 Satisfactory, 101–200 Moderate, 201–300 Poor, 301–400 Very Poor, >400 Severe."

        return "Diva can provide AQI insights. Live AQI API integration can be enabled in the next phase."

    # -----------------------------
    # Non-domain questions
    # -----------------------------
    return "❌ I am domain-restricted. Diva answers only PET waste, plastic waste, recycling, and AQI questions."

if st.button("Ask"):

   ans = answer_engine(question)


    st.markdown("### 🎯 Diva says:")
    st.success(ans)

    # female voice output
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 155)
        engine.setProperty('voice', engine.getProperty('voices')[1].id)
        engine.say(ans)
        engine.runAndWait()
    except:
        pass


# -------------------------------------------------------------------------------------
# 🚀 APP ROUTER
# -------------------------------------------------------------------------------------
if "user" not in st.session_state:
    login_page()
else:
    main_app()
