import os
os.system("pip install plotly")

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import re
from reportlab.pdfgen import canvas

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Diva – AI Environmental Assistant",
                   layout="wide")

# ------------------ GLOBAL DISCLAIMER ------------------
DISCLAIMER = """
### ⚠ Data Transparency Notice

• Live AQI values are retrieved from **WAQI.org official network**  
• PET waste numbers are **model-based estimates** using CPCB + FICCI growth values  
• City-level PET validation is **ongoing** – values should not be treated as municipal figures  
• All estimates are clearly labelled as such  

Diva always states whether data is:
✔ LIVE verified  
✔ Model-based estimate  
✔ Not available  
"""

# ------------------ FIREBASE LOGIN ------------------
API_KEY = "AIzaSyAbS3SdyPNRSNaUov0n4MeWFHTpoxBc4jc"

def firebase_auth(endpoint, email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={API_KEY}"
    return requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    }).json()

def login_screen():
    st.title("🔐 Secure Login – Diva")

    action = st.radio("Action", ["Login", "Create Account"], horizontal=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Continue"):
        if action == "Login":
            result = firebase_auth("signInWithPassword", email, password)
        else:
            result = firebase_auth("signUp", email, password)

        if "idToken" in result:
            st.session_state.logged = True
            st.session_state.user = email
            st.success("Login successful ✨")
            st.rerun()
        else:
            st.error("Authentication failed")

# ------------------ VOICE OUTPUT ------------------
def speak(text):
    st.components.v1.html(f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{text}");
        msg.pitch=1; msg.rate=1;
        msg.voice = speechSynthesis.getVoices().find(v=>v.name.toLowerCase().includes("female"))
                   || speechSynthesis.getVoices()[0];
        speechSynthesis.speak(msg);
    </script>
    """, height=0)

# ------------------ VOICE INPUT ------------------
def mic_input():
    st.components.v1.html("""
    <button onclick="record()" style="padding:10px;border-radius:10px;background:#e74c3c;color:white;">
    🎤 Speak to Diva</button>

    <script>
    function record(){
        var rec = new webkitSpeechRecognition();
        rec.lang="en-IN";
        rec.start();
        rec.onresult=function(e){
            var t=e.results[0][0].transcript;
            var tb=window.parent.document.querySelector("textarea");
            tb.value=t;
            tb.dispatchEvent(new Event('input',{bubbles:true}));
        }
    }
    </script>
    """, height=80)

# ------------------ PET FORECAST ------------------
def pet_forecast(city, year):
    base_year = 2020
    india_mt = 3.47
    growth = 0.065

    population = {
        "hyderabad": 10.5,
        "mumbai": 20.5,
        "delhi": 19,
        "chennai": 11.5,
        "bangalore": 13.2
    }

    if city not in population:
        return None

    share = population[city] / 1400
    baseline = share * india_mt * 1e6
    years = year - base_year

    return round(baseline * ((1 + growth) ** years), 2)

# ------------------ LIVE AQI ------------------
AQI_KEY = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"

def get_live_aqi(city):
    try:
        url = f"https://api.waqi.info/feed/{city}/?token={AQI_KEY}"
        r = requests.get(url).json()

        if r["status"] != "ok":
            return None

        data = r["data"]
        aqi = data["aqi"]
        dom = data.get("dominentpol", "NA")
        time = data["time"]["s"]

        if aqi <= 50: status = "Good"
        elif aqi <= 100: status = "Moderate"
        elif aqi <= 150: status = "Unhealthy for Sensitive Groups"
        elif aqi <= 200: status = "Unhealthy"
        elif aqi <= 300: status = "Very Unhealthy"
        else: status = "Hazardous"

        return aqi, dom, status, time

    except:
        return None

# ------------------ ENV TOPIC FILTER ------------------
ENV_WORDS = [
    "aqi","air","pollution","waste","plastic","pet","recycling",
    "environment","water","noise","soil","climate","carbon"
]

def is_environment(q):
    return any(k in q.lower() for k in ENV_WORDS)

# ------------------ MAIN ASSISTANT APP ------------------
def diva_app():

    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged = False
        st.rerun()

    st.title("🌿 Diva — AI Environmental Assistant")
    st.info(DISCLAIMER)

    mode = st.radio("Ask via:", ["Typing","Voice"], horizontal=True)
    if mode == "Voice":
        mic_input()

    question = st.text_input("Ask Diva…")

    if st.button("Ask Diva") and question:

        q = question.lower()

        if not is_environment(q):
            msg = "I am trained only on environmental topics such as AQI, PET waste, plastic pollution and climate. I cannot answer this question yet."
            st.warning(msg); speak(msg); return

        if "aqi" in q or "air" in q or "pollution" in q:

            city="hyderabad"
            for c in ["hyderabad","mumbai","delhi","chennai","bangalore","pune","kolkata"]:
                if c in q: city=c

            data = get_live_aqi(city)

            if data:
                aqi, pm, status, time = data

                msg=f"""
📍 City: **{city.title()}**
🌫 Live AQI: **{aqi}**
🧪 Dominant pollutant: **{pm}**
📊 Category: **{status}**
⏱ Last updated: **{time}**

✔ Source: **WAQI.org monitoring network**
"""
                st.success(msg)
                speak(f"Live air quality in {city.title()} is {aqi}, categorized as {status}, dominated by {pm}.")
            else:
                st.error("Live AQI temporarily unavailable")
                speak("Live AQI unavailable at the moment")

            return

        words=q.split()
        city=None; year=None
        for w in words:
            if w in ["hyderabad","mumbai","delhi","bangalore","chennai"]:
                city=w
            if w.isdigit() and len(w)==4:
                year=int(w)

        if city and year:
            val=pet_forecast(city,year)

            msg=f"""
📍 City: **{city.title()}**
📅 Year: **{year}**
♻ Estimated PET waste: **{val/1000:.2f} thousand tonnes/year**

⚠ Model-based estimate using:
• CPCB plastic waste report  
• FICCI plastic growth outlook  
"""
            st.success(msg)
            speak(f"Estimated PET waste in {city.title()} in {year} is {val/1000:.2f} thousand tonnes per year.")
            return

        speak("I do not have validated data for that yet.")

    # ---------- Trend Charts ----------
    st.subheader("📈 PET Waste Forecast Trend")
    ct = st.selectbox("Select city",["hyderabad","mumbai","delhi","bangalore","chennai"])
    endy = st.slider("Forecast until year",2025,2045,2035)

    years=list(range(2024,endy+1))
    vals=[pet_forecast(ct,y)/1000 for y in years]

    df=pd.DataFrame({"Year":years,"PET (thousand tonnes)":vals})
    st.plotly_chart(px.line(df,x="Year",y="PET (thousand tonnes)",markers=True))

    # ---------- PDF Report ----------
    st.subheader("📄 Generate PDF Report")
    if st.button("Create report"):
        filename="diva_report.pdf"
        c=canvas.Canvas(filename)
        c.drawString(40,800,"DIVA — Environmental Report")
        c.drawString(40,780,f"City: {ct}")
        c.drawString(40,760,f"Forecast up to {endy}")
        c.save()
        with open(filename,"rb") as f:
            st.download_button("Download PDF",f,file_name=filename)

    # ---------- GIS MAP ----------
    st.subheader("🗺 Hyderabad Ward Map (upload GeoJSON)")
    upl=st.file_uploader("Upload GHMC GeoJSON",type=["geojson","json"])
    if upl:
        import json
        gj=json.load(upl)
        m=folium.Map([17.385,78.4867],zoom_start=10)
        folium.GeoJson(gj).add_to(m)
        st_folium(m,width=700,height=450)
    else:
        st.info("Upload geojson to enable real heatmap")

# ------------------ ROUTER ------------------
if "logged" not in st.session_state:
    st.session_state.logged=False

if not st.session_state.logged:
    login_screen()
else:
    diva_app()
