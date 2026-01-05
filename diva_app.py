import streamlit as st
import requests
import re

st.set_page_config(page_title="Diva AI", layout="wide")

# ------------------- FIREBASE CONFIG -------------------

FIREBASE_WEB_API_KEY = "AIzaSyAbS3SdyPNRSNaUov0n4MeWFHTpoxBc4jc"


# ------------------- FIREBASE FUNCTIONS -------------------

def firebase_signup(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload).json()


def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=payload).json()


# ------------------- LOGIN WALL -------------------

st.title("🌿 Diva — AI Environmental Decision Support Assistant")

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:

    st.subheader("🔐 Login or Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    action = st.radio("Action", ["Login", "Sign Up"], horizontal=True)

    if st.button("Confirm"):

        if action == "Login":
            result = firebase_login(email, password)
        else:
            result = firebase_signup(email, password)

        if "idToken" in result:
            st.success("Logged in successfully 🎉")
            st.session_state["auth"] = True
            st.session_state["user_email"] = email
            st.experimental_rerun()
        else:
            st.error(result.get("error", {}).get("message", "Unknown error"))

    st.stop()


# ------------------- MAIN APP AFTER LOGIN -------------------

st.success(f"Logged in as {st.session_state['user_email']} ✔")

st.header("♻ PET Waste & AQI Intelligence Assistant")


# ------------------- PET FORECAST MODEL -------------------

def pet_forecast(city, year):

    base_year = 2025
    base_value = 145000  # tonnes/year baseline
    growth_rate = 0.065  # 6.5%

    years_ahead = int(year) - base_year
    value = round(base_value * ((1 + growth_rate) ** years_ahead), 2)

    return value


# ------------------- AQI API (future-ready) -------------------

AQI_API_KEY = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"  # optional

def get_aqi(city):

    if AQI_API_KEY == "":
        return "🔜 Live AQI will be added when API key is enabled."

    url = f"https://api.waqi.info/feed/{city}/?token={AQI_API_KEY}"
    r = requests.get(url).json()

    if r["status"] != "ok":
        return "AQI not available"

    return r["data"]["aqi"]


# ------------------- VOICE (female speech synthesis) -------------------

def speak(text):
    st.components.v1.html(f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.pitch = 1;
    msg.rate = 1;
    msg.voice = speechSynthesis.getVoices().find(v => v.name.toLowerCase().includes("female")) 
                 || speechSynthesis.getVoices()[0];
    speechSynthesis.speak(msg);
    </script>
    """, height=0)


# ------------------- USER QUESTION ENGINE -------------------

def answer_engine(question):

    q = question.lower()
    year_match = re.findall(r"(20\\d{{2}})", q)
    year = int(year_match[0]) if year_match else 2030

    # city extraction lightweight
    city = "Hyderabad"
    for c in ["hyderabad", "mumbai", "delhi", "chennai", "kolkata", "pune", "bangalore"]:
        if c in q:
            city = c.capitalize()

    waste = pet_forecast(city, year)

    return city, year, waste


# ------------------- UI -------------------

ask_mode = st.radio("Ask via:", ["Typing"], horizontal=True)

question = st.text_input("Your question")

if st.button("Ask Diva") and question:

    city, year, waste_val = answer_engine(question)

    st.success(f"""
    📍 **City:** {city}  
    📆 **Year:** {year}  
    ♻ **Projected PET Waste:** {waste_val:,} tonnes/year
    """)

    speak(f"Projected pet waste in {city} in {year} is {waste_val} tonnes per year")


# ------------------- AQI CHECK -------------------

st.subheader("🌫 Check Current AQI (demo readiness)")

city_input = st.text_input("Enter city to check AQI")

if st.button("Check AQI"):

    result = get_aqi(city_input.lower())
    st.info(f"Current AQI in {city_input} = {result}")


# ------------------- MAP DEMO -------------------

st.subheader("🗺 Hyderabad PET & AQI Zones (demo map)")

st.map()
