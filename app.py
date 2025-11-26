 import streamlit as st
import json
import os
import pickle
import numpy as np
import hashlib

# --------------------------
# Load CSS
# --------------------------
def load_css():
    st.markdown("""
    <style>

    .stApp {
       background-image: url("assets/bg/bg.jpg");
        background-size: cover;
    }

    .card {
        padding: 30px;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }

    .title {
        font-size: 40px;
        font-weight: 900;
        color: #d62828;
        text-align: center;
        text-shadow: 2px 2px #ffffff;
    }

    .stButton>button {
        width: 100%;
        padding: 12px;
        border-radius: 10px;
        background-color: #d62828;
        color: white;
        border: none;
        font-size: 18px;
    }

    .stButton>button:hover {
        background-color: #a30000;
        transform: scale(1.05);
    }

    </style>
    """, unsafe_allow_html=True)


# --------------------------
# Authentication Logic
# --------------------------

USER_DB = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f)
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def signup_user(email, password):
    users = load_users()
    if email in users:
        return False
    users[email] = hash_password(password)
    save_users(users)
    return True

def login_user(email, password):
    users = load_users()
    hashed = hash_password(password)
    return email in users and users[email] == hashed


# --------------------------
# Model
# --------------------------

model = pickle.load(open("model.pkl", "rb"))


def prediction_page():
    st.markdown("<h1 class='title'>❤️ Heart Disease Prediction</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        age = st.number_input("Age", 1, 120, 45)
        sex = st.selectbox("Sex (0 = Female, 1 = Male)", [0, 1])
        cp = st.selectbox("Chest Pain Type (0–3)", [0,1,2,3])
        trestbps = st.number_input("Resting Blood Pressure", 80, 200, 120)
        chol = st.number_input("Cholesterol Level", 100, 600, 200)
        fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl (1 = Yes, 0 = No)", [0,1])
        restecg = st.selectbox("Resting ECG Results (0–2)", [0,1,2])
        thalach = st.number_input("Max Heart Rate Achieved", 60, 220, 150)
        exang = st.selectbox("Exercise Induced Angina", [0,1])
        oldpeak = st.number_input("Oldpeak Value", 0.0, 10.0, 1.0)
        slope = st.selectbox("Slope (0–2)", [0,1,2])
        ca = st.selectbox("Major Vessels (0–3)", [0,1,2,3])
        thal = st.selectbox("Thal (1=Normal,2=Fixed,3=Reversible)", [1,2,3])

        if st.button("Predict"):
            data = np.array([[age, sex, cp, trestbps, chol, fbs,
                              restecg, thalach, exang, oldpeak,
                              slope, ca, thal]])

            prediction = model.predict(data)[0]

            if prediction == 1:
                st.error("⚠️ High Risk of Heart Disease")
            else:
                st.success("✅ Low Risk of Heart Disease")

        st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# Login & Signup UI
# --------------------------

def login_page():
    st.markdown("<h1 class='title'>🔐 Login</h1>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if login_user(email, password):
                st.session_state["logged_in"] = True
                st.session_state["email"] = email
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with col2:
        if st.button("Create Account"):
            st.session_state["signup_mode"] = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def signup_page():
    st.markdown("<h1 class='title'>📝 Create Account</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm:
            st.error("Passwords do not match!")
        else:
            if signup_user(email, password):
                st.success("Account created! Please login.")
                st.session_state["signup_mode"] = False
                st.rerun()
            else:
                st.error("Email already exists.")

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# APP FLOW
# --------------------------

load_css()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "signup_mode" not in st.session_state:
    st.session_state["signup_mode"] = False

if not st.session_state["logged_in"]:
    if st.session_state["signup_mode"]:
        signup_page()
    else:
        login_page()
else:
    prediction_page()
