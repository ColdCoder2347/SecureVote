import streamlit as st
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import json
import os
from collections import Counter

st.set_page_config(page_title="Tally Votes", page_icon="📊")
st.title("📊 Tally Votes")

file_path = "votes.json"

# --- Check for required keys ---
if "authority_key" not in st.session_state or "voter_public_key" not in st.session_state:
    st.error("❌ Required keys not found in session. Please cast at least one vote first.")
    st.stop()

# --- Load votes file ---
if not os.path.exists(file_path):
    st.warning("⚠️ No votes file found.")
    st.stop()

with open(file_path, "r") as f:
    try:
        votes_data = json.load(f)
    except json.JSONDecodeError:
        st.error("❌ Error reading votes file. It might be corrupted.")
        st.stop()

if not votes_data:
    st.info("ℹ️ No votes to tally.")
    st.stop()

# --- Process and verify each vote ---
st.markdown("### 🔍 Verifying and Decrypting Votes...")

valid_votes = []
invalid_votes = []

for entry in votes_data:
    try:
        # Decode base64 data
        encrypted_vote = base64.b64decode(entry["encrypted_vote"])
        signature = base64.b64decode(entry["signature"])

        # Decrypt vote using authority's private key
        cipher = PKCS1_OAEP.new(st.session_state.authority_key)
        decrypted_vote = cipher.decrypt(encrypted_vote)
        vote_text = decrypted_vote.decode()

        # Verify signature using voter's public key
        h = SHA256.new(decrypted_vote)
        pkcs1_15.new(st.session_state.voter_public_key).verify(h, signature)

        valid_votes.append(vote_text)

    except Exception as e:
        invalid_votes.append({
            "error": str(e),
            "raw_vote": entry
        })

# --- Display results ---
st.success(f"✅ Valid votes: {len(valid_votes)}")
if invalid_votes:
    st.error(f"❌ Invalid votes: {len(invalid_votes)}")

# Tally votes
vote_counts = Counter(valid_votes)

if vote_counts:
    st.markdown("### 🗳️ Final Tally")
    st.bar_chart(vote_counts)

    for candidate, count in vote_counts.items():
        st.markdown(f"- **{candidate}**: {count} vote{'s' if count != 1 else ''}")

# Optional: Show details of invalid votes
if invalid_votes:
    with st.expander("🔍 See Details of Invalid Votes"):
        for i, item in enumerate(invalid_votes, 1):
            st.write(f"{i}. Error: {item['error']}")
