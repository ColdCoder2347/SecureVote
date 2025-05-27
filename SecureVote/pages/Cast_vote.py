import streamlit as st
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import json
import os
from datetime import datetime

st.set_page_config(page_title="Secure E-Voting", page_icon="🗳️")
st.title("🗳️ Cast Your Vote")

# Check if the user is authenticated
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.error("❌ You must be logged in to cast a vote.")
    st.stop()

# --- Key Setup ---
if "voter_key" not in st.session_state:
    voter_key = RSA.generate(2048)
    authority_key = RSA.generate(2048)
    
    st.session_state.voter_key = voter_key
    st.session_state.voter_public_key = voter_key.publickey()
    st.session_state.authority_key = authority_key
    st.session_state.authority_public_key = authority_key.publickey()

# --- Candidate Selection ---
st.subheader("Vote for your candidate")
candidates = ["Alice", "Bob", "Charlie"]
vote = st.radio("Choose a candidate:", candidates)

# Function to save vote to file
def save_vote_to_file(encrypted_b64, signature_b64):
    vote_entry = {
        "encrypted_vote": encrypted_b64,
        "signature": signature_b64,
        "timestamp": datetime.utcnow().isoformat()
    }

    file_path = "votes.json"

    # Load existing votes or create new list
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(vote_entry)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Button for casting vote
if st.button("Cast Vote"):
    try:
        # Encrypt vote with authority's public key
        cipher = PKCS1_OAEP.new(st.session_state.authority_public_key)
        encrypted_vote = cipher.encrypt(vote.encode())
        encrypted_b64 = base64.b64encode(encrypted_vote).decode()

        # Sign with voter's private key
        h = SHA256.new(vote.encode())
        signature = pkcs1_15.new(st.session_state.voter_key).sign(h)
        signature_b64 = base64.b64encode(signature).decode()

        # Save to file
        save_vote_to_file(encrypted_b64, signature_b64)

        st.success("✅ Vote cast and saved successfully!")

        st.markdown("### 🔒 Encrypted Vote (Base64):")
        st.code(encrypted_b64)

        st.markdown("### 🖋️ Digital Signature (Base64):")
        st.code(signature_b64)

    except Exception as e:
        st.error(f"❌ Error during voting: {e}")
