import streamlit as st
import requests
import pyttsx3
import plotly.express as px
import folium
from streamlit_folium import st_folium
import pandas as pd
from reportlab.pdfgen import canvas
from io import BytesIO


# ------------------ LOGIN ------------------
USERS = {"admin":"1234","user":"diva123"}

if "login" not in st.session_state:
    st.session_state.login=False

if not st.session_state.login:
    st.title("🔐 Login to DIVA – Environmental Assistant")
    u = st.text_input("Username")
    p = st.text_input("Password",type="password")
    if st.button("Login"):
        if u in USERS and USERS[u]==p:
            st.session_state.login=True
            st.success("Logged in successfully ✓")
        else:
            st.error("Invalid credentials")
    st.stop()



# ------------------ TITLE ------------------
st.title("🌍 DIVA — AI Environmental Assistant")


# ------------------ TEXT TO SPEECH ------------------
engine=pyttsx3.init()
voices=engine.getProperty("voices")
for v in voices:
    if "zira" in v.name.lower() or "hazel" in v.name.lower():
        engine.setProperty("voice",v.id)
        break


def speak(text):
    engine.say(text)
    engine.runAndWait()


# ------------------ INTELLIGENCE ENGINE ------------------

def diva_brain(q):

    q=q.lower()

    sources = {
        "unep":"UNEP Global Plastics Outlook 2024",
        "oecd":"OECD Global Plastics 2023",
        "cpcb":"CPCB India Report 2023"
    }

    # intent detection
    if "increase" in q or "growth" in q or "last 5 years" in q:
        ans = """📈 PET waste increased **~23–28% in last 5 years**.

Trend is verified from UNEP + OECD.

Status: Verified trend, PET share estimated
Sources: UNEP 2024, OECD 2023"""
        return ans

    if "current" in q or "now" in q or "today" in q or "2025" in q:
        ans = """🌍 Current global plastic waste (2025):

Total Plastic ≈ **430–450 million tonnes/year**
PET Component ≈ **75–85 million tonnes/year**

Status: Total is verified, PET estimated
Source: UNEP Global Plastics Outlook 2024"""
        return ans

    if "forecast" in q or "2030" in q or "future" in q or "prediction" in q:
        ans = """🔮 PET waste will nearly double by **2040** without policies.

Baseline growth: 3–4% yearly
Reduction possible: 40–45% with regulation

Status: Model forecast
Source: UNEP 2024"""
        return ans

    if "aqi" in q:
        return "Type → AQI cityname (example: AQI Delhi)"

    if not any(w in q for w in ["pet","plastic","aqi","pollution","waste","recycle"]):
        return "Sorry, I am currently trained only for environmental topics."

    return "I understood your question but I need more context."


# ------------------ CHAT ------------------

question=st.text_input("Ask DIVA anything 🌱")
if st.button("Ask"):
    reply=diva_brain(question)
    st.write(f"**Diva:** {reply}")
    speak(reply)



# ------------------ LIVE AQI ------------------
st.subheader("🫁 Check Live AQI")

city=st.text_input("Enter city")
if st.button("Get AQI"):
    try:
        url=f"https://api.waqi.info/feed/{city}/?token=demo"
        data=requests.get(url).json()
        aqi=data["data"]["aqi"]
        st.success(f"Current AQI in {city} = {aqi}")
    except:
        st.error("AQI unavailable currently")


# ------------------ PET TREND CHART ------------------
st.subheader("📊 PET Waste Trend")

years=[2015,2018,2020,2023,2025]
values=[60,68,72,81,87]

df=pd.DataFrame({"Year":years,"PET Million Tonnes":values})

fig=px.line(df,x="Year",y="PET Million Tonnes",markers=True)
st.plotly_chart(fig)



# ------------------ MAP DEMO ------------------
st.subheader("🗺️ Example Pollution Map")

m=folium.Map(location=[17.4,78.4],zoom_start=6)
folium.Marker([28.6,77.2],popup="Delhi AQI High").add_to(m)
folium.Marker([19.0,72.8],popup="Mumbai AQI Moderate").add_to(m)
st_folium(m,width=700)



# ------------------ PDF DOWNLOAD ------------------
st.subheader("📄 Download Answer as PDF")

pdf_buffer = BytesIO()
c = canvas.Canvas(pdf_buffer)
c.drawString(100,800,"DIVA Environmental Report")
c.save()

st.download_button("Download Sample PDF",pdf_buffer,"diva.pdf")
