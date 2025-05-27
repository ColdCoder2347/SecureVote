import streamlit as st
import json
import os
from hashlib import sha256

# Set up page configuration
st.set_page_config(page_title="Secure E-Voting System", page_icon="🗳️", layout="centered")
st.title("🗳️ Welcome to the Secure E-Voting System")

# File path to store users
users_file = "users.json"

# --- Function to Load Registered Users ---
def load_users():
    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            return json.load(f)
    else:
        return {}

# --- Function to Register New User ---
def register_user(email, password):
    users = load_users()
    
    # Check if user already exists
    if email in users:
        return False  # User already registered
    
    # Hash the password for security
    password_hash = sha256(password.encode()).hexdigest()
    
    # Add new user to the users dictionary
    users[email] = {"password": password_hash}
    
    # Save updated users back to file
    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)
    
    return True

# --- Function to Authenticate User ---
def authenticate_user(email, password):
    users = load_users()
    
    # Check if user exists and password matches
    if email in users:
        password_hash = sha256(password.encode()).hexdigest()
        if users[email]["password"] == password_hash:
            return True
    return False

# --- User Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- Login or Registration ---
if not st.session_state.authenticated:
    st.subheader("Login or Register")

    action = st.radio("Choose an option:", ("Login", "Register"))

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if action == "Register":
        if st.button("Register"):
            if email and password:
                if register_user(email, password):
                    st.success("✅ Registration successful! Please log in.")
                else:
                    st.error("❌ User already registered with this email.")
            else:
                st.error("❌ Please enter both email and password.")

    elif action == "Login":
        if st.button("Login"):
            if email and password:
                if authenticate_user(email, password):
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.success(f"✅ Welcome {email}! You are now logged in.")
                else:
                    st.error("❌ Invalid email or password.")
            else:
                st.error("❌ Please enter both email and password.")
else:
    st.success(f"✅ You are logged in as {st.session_state.email}")
    st.markdown("""
    ### Now you can:
    - Cast your vote
    - Verify your vote later
    """)
    
    # Function to navigate to cast vote page
    def navigate_to_cast_vote():
        st.session_state.page = "cast_vote"

    # Button to navigate to vote casting page
    if st.button("Cast Vote", on_click=navigate_to_cast_vote):
        st.session_state.page = "cast_vote"
