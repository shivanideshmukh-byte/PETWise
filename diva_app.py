import streamlit as st
import requests
import json
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
    payload = {"email": email, "password": password, "returnSecureToken": True}
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
                st.experimental_rerun()
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
        st.experimental_rerun()

    st.title("🌿 Diva – AI Environmental Assistant")

    user_question = st.text_input("Ask Diva anything about PET, waste, or AQI:")

    if st.button("Ask"):
        if "plastic" in user_question.lower() or "aqi" in user_question.lower() or "waste" in user_question.lower():
            ans = "This question is environmental-related, and Diva will soon answer using verified PET & AQI datasets."
        else:
            ans = "❌ I am domain restricted. I only answer environmental questions."

        st.write("🧠 Diva:", ans)
        tts(ans)
        add_chat(user_question + " -> " + ans)

    st.subheader("🗂 Encrypted chat history (local session)")
    for c in get_chats():
        st.write("🔒", c)

# -------------------------------------------------------------------------------------
# 🚀 APP ROUTER
# -------------------------------------------------------------------------------------
if "user" not in st.session_state:
    login_page()
else:
    main_app()
