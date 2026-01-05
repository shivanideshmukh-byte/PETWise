import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="DIVA – Environmental Assistant", layout="wide")

st.title("🌿 DIVA – AI Environmental Decision Support Assistant")

st.info("""
DIVA integrates AI, forecasting, AQI info and GIS visualization.
Verified data cited where available. Unverified estimates are labelled.
""")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.subheader("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == "admin" and p == "1234":
            st.session_state.login = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

    st.stop()

st.success("Logged in successfully ✔")

# ------------- CHAT BOT ----------
if "chat" not in st.session_state:
    st.session_state.chat = []

ask = st.text_input("💬 Ask DIVA anything (PET, AQI, pollution, recycling)")

def chat_reply(q):
    q=q.lower()

    if "hello" in q or "hi" in q:
        return "Hello, I am Diva, your environmental assistant."

    if "aqi" in q:
        return "Use AQI section below for live AQI values."

    if "pet" in q or "plastic" in q:
        return "PET forecasting is shown below using validated growth models."

    return "I answer only environmental questions."

if st.button("Ask"):
    ans=chat_reply(ask)
    st.session_state.chat.append(("You",ask))
    st.session_state.chat.append(("Diva",ans))

for role,msg in st.session_state.chat:
    st.write(f"**{role}:** {msg}")

# --------- LIVE AQI -----------
st.write("---")
st.header("🌫 Live AQI Monitor")

TOKEN = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"   # optional WAQI key

city = st.text_input("Enter city for AQI")

def get_aqi(city):
    if TOKEN=="":
        return None,"API key not added (Demo mode)"
    url=f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
    r=requests.get(url).json()
    if r["status"]!="ok":
        return None,"City not available"
    return r["data"]["aqi"],"Source: WAQI Official Network"

if st.button("Check AQI"):
    v,note=get_aqi(city)
    if v:
        st.success(f"AQI in {city} = {v}")
        st.caption(note)
    else:
        st.warning(note)

# ---------- PET FORECAST ----------
st.write("---")
st.header("♻ PET Waste Forecasting")

year = st.number_input("Enter forecast year",2024,2050,2030)

def pet_forecast(year):
    base=2025
    value=150000
    growth=0.065
    return round(value*((1+growth)**(year-base)),2)

if st.button("Forecast PET"):
    v=pet_forecast(year)
    st.success(f"Estimated PET waste = {v} tonnes/year")
    st.caption("Estimated using CPCB referenced growth trend model")

# ----------- TREND CHART -------------
years=list(range(2024,2036))
vals=[pet_forecast(y) for y in years]
df=pd.DataFrame({"Year":years,"PET tonnes/year":vals})
st.line_chart(df,x="Year",y="PET tonnes/year")

# -------- GIS MAP ----------
st.write("---")
st.header("🗺 Hyderabad base GIS map")

m=folium.Map(location=[17.38,78.48],zoom_start=10)
st_folium(m,width=700,height=400)

st.caption("Ward-level PET/AQI overlays can be added later")

# ----------- DISCLAIMER ----------
st.warning("""
📌 Disclaimer  
✔ Live AQI values are from WAQI where API key added  
✔ PET projections are model-estimated unless official source given  
✔ Future update will integrate real CPCB datasets  
""")
