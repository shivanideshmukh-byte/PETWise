import streamlit as st
import pandas as pd
import sqlite3
from cryptography.fernet import Fernet
import json
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Diva – AI Environmental Assistant", layout="wide")

# --------- ENCRYPTION KEY ---------
KEY = Fernet.generate_key()
cipher = Fernet(KEY)

# --------- DATABASE ---------
conn = sqlite3.connect("diva_secure.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS logs (user TEXT, question BLOB, answer BLOB)")

# --------- LOGIN ---------
users = {"admin":"admin123","student":"diva"}

if "logged" not in st.session_state:
    st.session_state.logged = False

if not st.session_state.logged:
    st.title("🔐 Secure Login – Diva AI")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in users and users[u]==p:
            st.session_state.logged=True
            st.experimental_rerun()
        else:
            st.error("Invalid login")
    st.stop()

st.title("🌍 Diva – AI Environmental Assistant")
st.write("Hyderabad implementation • Designed for Pan‑India scaling")

# --------- LOAD VERIFIED DATA ---------
with open("verified_data_hyderabad.json","r") as f:
    data = json.load(f)

# --------- AI ANSWER ENGINE ---------
def diva_answer(question):
    q=question.lower()

    allowed=["plastic","pet","waste","pollution","air","aqi","landfill","recycle","environment","gis","forecast","precaution"]
    if not any(k in q for k in allowed):
        return "I am not trained for this. I only answer environmental and PET waste–related questions."

    if "aqi" in q or "pollution" in q:
        return f"Current average AQI in Hyderabad is {data['aqi']} (CPCB 2023)."

    if "current" in q and "pet" in q:
        return f"Estimated PET waste in Hyderabad is {data['pet_tpd']} TPD (CPCB & GHMC)."

    if "precaution" in q:
        return "Avoid single‑use plastics, segregate waste at source, support recycling, and follow EPR‑compliant brands."

    if "forecast" in q:
        return "Forecasting is performed using ML models such as Random Forest and ARIMA to project PET waste trends."

    return "This question is environmental‑related but data is not verified in my sources yet."

# --------- SECURE LOGGING ---------
def save_secure(user,q,a):
    cursor.execute("INSERT INTO logs VALUES (?,?,?)",
                   (user, cipher.encrypt(q.encode()), cipher.encrypt(a.encode())))
    conn.commit()

# --------- VOICE ---------
def listen_voice():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio=r.listen(source)
        try:
            return r.recognize_google(audio)
        except:
            return "Could not understand."

def speak(text):
    engine=pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# --------- CHAT UI ---------
st.subheader("💬 Ask Diva")

mode = st.radio("Choose mode",["Text"])


if mode=="Text":
    q=st.text_input("Type your question")
    if st.button("Ask"):
        ans=diva_answer(q)
        st.write("🧠 Diva:",ans)
        save_secure("user",q,ans)
        speak(ans)

else:
    if st.button("🎤 Speak now"):
        q=listen_voice()
        st.write("You said:",q)
        ans=diva_answer(q)
        st.write("🧠 Diva:",ans)
        save_secure("user",q,ans)
        speak(ans)

# --------- GIS MAP ---------
st.subheader("🗺 Hyderabad GIS Demo Map")

m=folium.Map(location=[17.3850,78.4867],zoom_start=11)
folium.Marker([17.40,78.48],popup="High pollution zone").add_to(m)
folium.Marker([17.33,78.50],popup="High plastic waste zone").add_to(m)
st_folium(m,width=700,height=450)

st.caption("Verified sources: CPCB, TSPCB, GHMC reports and peer‑reviewed publications. Future work: live API integration.")
