import streamlit as st
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

st.set_page_config(page_title="Verify Vote", page_icon="🔍")
st.title("🔍 Verify Vote")

st.markdown("Paste the **Base64-encoded encrypted vote** and the **digital signature** to verify.")

encrypted_vote_b64 = st.text_area("🔒 Encrypted Vote (Base64)")
signature_b64 = st.text_area("🖋️ Digital Signature (Base64)")

if st.button("Verify"):
    if "authority_key" not in st.session_state or "voter_public_key" not in st.session_state:
        st.error("❗ Authority or voter keys not found. Please cast a vote first.")
    else:
        try:
            # Decode input
            encrypted_vote = base64.b64decode(encrypted_vote_b64.strip())
            signature = base64.b64decode(signature_b64.strip())

            # Decrypt vote using authority's private key
            cipher = PKCS1_OAEP.new(st.session_state.authority_key)
            decrypted_vote = cipher.decrypt(encrypted_vote)
            vote_text = decrypted_vote.decode()

            # Verify signature using voter's public key
            h = SHA256.new(decrypted_vote)
            pkcs1_15.new(st.session_state.voter_public_key).verify(h, signature)

            st.success("✅ Signature Verified!")
            st.markdown(f"🗳️ The decrypted vote is: **{vote_text}**")

        except (ValueError, TypeError, Exception) as e:
            st.error(f"❌ Verification failed: {e}")
