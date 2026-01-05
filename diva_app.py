import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from gtts import gTTS
import base64
from io import BytesIO

st.set_page_config(page_title="Diva – Environmental Assistant", layout="centered")

# ---------------- SESSION / LOGIN -------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("🌿 Diva — AI Environmental Assistant")

if not st.session_state.logged_in:
    st.subheader("🔐 Login required")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email.strip() != "" and password.strip() != "":
            st.session_state.logged_in = True
            st.success("Logged in successfully")
        else:
            st.error("Enter valid email and password")

    st.stop()

st.success("Logged in as user")

# ---------------- TEXT TO SPEECH --------------------

def speak(text, gender="female"):
    tts = gTTS(text=text, lang='en', slow=False, tld="co.in")
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    audio_html = f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# ---------------- PET WASTE MODEL -------------------

BASE_YEAR = 2025
BASE_VALUE = 145000
GROWTH = 0.065

def project_pet(year):
    years = year - BASE_YEAR
    return round(BASE_VALUE * ((1 + GROWTH) ** years), 2)

# ---------------- LIVE AQI --------------------------

WAQI_KEY = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"  # optional – if blank returns message

def get_aqi(city):
    if WAQI_KEY == "":
        return None, "Live AQI requires WAQI API key (official board)."

    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_KEY}"
    data = requests.get(url).json()

    if data["status"] != "ok":
        return None, "AQI not available or city not monitored."

    return data["data"]["aqi"], "Source: World Air Quality Index Project (WAQI)"

# ---------------- CHAT ENGINE ------------------------

def diva_brain(question):
    q = question.lower()

    # detect year
    import re
    match = re.findall(r"(20\d{2})", q)
    year = int(match[0]) if match else BASE_YEAR

    # detect city
    import re
    city_tokens = ["hyderabad","mumbai","delhi","chennai","kolkata","pune","bengaluru"]
    found_city = None
    for c in city_tokens:
        if c in q:
            found_city = c.capitalize()

    if "aqi" in q:
        if found_city:
            value, note = get_aqi(found_city)
            if value:
                return f"Current AQI in {found_city} is {value}. {note}", True
            else:
                return f"Live AQI unavailable. {note}", True
        return "Please mention city for AQI.", False

    if "waste" in q or "pet" in q:
        forecast = project_pet(year)
        msg = f"""
City: **{found_city if found_city else "Not specified"}**
Year: **{year}**
Projected PET waste: **{forecast} tonnes/year**

Model based on CPCB baseline 2025 and 6.5% annual growth.

⚠ Data is modeled estimate. Not verified field-measured value.
        """
        return msg, True

    return "I am currently trained only for PET waste & AQI questions in India.", False

# ---------------- UI -------------------------------

st.subheader("💬 Ask Diva")

question = st.text_input("Ask anything about PET waste or AQI")

if st.button("Ask"):
    if question.strip() == "":
        st.error("Ask a valid question")
    else:
        reply, speakable = diva_brain(question)
        st.markdown(reply)
        if speakable:
            speak(reply)

# ---------------- Trends chart ---------------------

st.subheader("📈 PET Waste Trend (Model Demo)")

trend_years = list(range(2020, 2031))
trend_values = [project_pet(y) for y in trend_years]

df = pd.DataFrame({"Year": trend_years, "PET Waste (tonnes/year)": trend_values})

st.line_chart(df, x="Year", y="PET Waste (tonnes/year)")

st.caption("""
📌 Trend is model based.
Source baseline: **Central Pollution Control Board (CPCB), India**
Data verified: ❌ (Projection only)
""")
