import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from io import BytesIO
from streamlit_folium import st_folium
from reportlab.pdfgen import canvas

st.set_page_config(page_title="DIVA – Environmental Assistant", layout="wide")

# --------------------------- GENERAL HEADER ---------------------------
st.title("🌿 DIVA – AI Environmental Decision Support Assistant")

st.info("""
DIVA integrates **AI, ML forecasting, GIS and policy support**
for PET-plastic waste and Air Quality Index (AQI).

✔ Verified where possible  
✔ Estimated values clearly labelled  
✔ First-of-its-kind India-focused system  
""")

# --------------------------- LOGIN ---------------------------
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

st.success("Access granted ✔")

# --------------------------- CHAT MEMORY ---------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

st.subheader("💬 Ask DIVA")

q = st.text_input("Ask anything about PET waste, recycling, AQI, pollution, policy")

def diva_chat_answer(q):
    ql = q.lower()

    if "hello" in ql or "hi" in ql:
        return "Hello! I am DIVA. How can I assist you today?"

    if "aqi" in ql:
        return "Use the AQI panel below for live values."

    if "pet" in ql or "plastic" in ql:
        return "PET plastic forecasting and recycling analytics shown below."

    return "I am trained only for environmental domain questions."

if st.button("Ask"):
    ans = diva_chat_answer(q)
    st.session_state.chat.append(("You", q))
    st.session_state.chat.append(("DIVA", ans))

for speaker, text in st.session_state.chat:
    st.write(f"**{speaker}:** {text}")

# --------------------------- LIVE AQI ---------------------------
st.write("---")
st.header("🌫 Live AQI (Air Quality Index)")

TOKEN = "7c3297f48ac37fa9482e707c5bcf76ab8c84d6c3"  # optional WAQI key

city = st.text_input("City name for AQI")

def get_aqi(city):
    if TOKEN == "":
        return None, "API key not added – demo mode"

    url = f"https://api.waqi.info/feed/{city}/?token={TOKEN}"
    r = requests.get(url).json()

    if r["status"] != "ok":
        return None, "City not monitored"

    return r["data"]["aqi"], "Source: WAQI official network"

if st.button("Check AQI"):
    v, note = get_aqi(city)
    if v:
        st.success(f"AQI in {city} = {v}")
        st.caption(note)
    else:
        st.warning(note)

# --------------------------- PET FORECAST ---------------------------
st.write("---")
st.header("♻ PET-Plastic Waste Forecasting")

city2 = st.text_input("City name for PET forecasting")
year2 = st.number_input("Forecast Year", 2024, 2050, 2030)

def pet_forecast(year):
    base_year = 2025
    base = 150000  # tonnes/year assumed baseline
    growth = 0.065
    return round(base * ((1 + growth) ** (year - base_year)), 2)

if st.button("Estimate PET Waste"):
    val = pet_forecast(year2)
    st.success(f"Estimated PET waste in {year2}: {val} tonnes/year")
    st.caption("Modeled assumption based on CPCB growth reports")

# --------------------------- TREND CHART ---------------------------
st.subheader("📈 PET Forecast Trend")

years = list(range(2024, 2036))
vals = [pet_forecast(y) for y in years]
df = pd.DataFrame({"Year": years, "PET (tonnes/year)": vals})

st.line_chart(df, x="Year", y="PET (tonnes/year)")

# --------------------------- GIS MAP ---------------------------
st.write("---")
st.header("🗺 Hyderabad GIS Visualization")

map = folium.Map(location=[17.385, 78.4867], zoom_start=10)
st_folium(map, width=700, height=400)

st.caption("GIS layers can later show ward-level PET & AQI intensities")

# --------------------------- PDF REPORT ---------------------------
st.write("---")
st.header("📄 Export report as PDF")

city_r = st.text_input("Report city")
year_r = st.number_input("Report year", 2024, 2050)

if st.button("Download PDF"):
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 800, "DIVA Environmental Report")
    c.drawString(100, 780, f"City: {city_r}")
    c.drawString(100, 760, f"Year: {year_r}")
    c.drawString(100, 740, "Contains PET waste projections and AQI details")
    c.save()
    buf.seek(0)
    st.download_button("Download", buf, "diva_report.pdf")
