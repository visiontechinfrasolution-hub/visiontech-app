import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

def show(supabase):
    st.title("📡 WCC Status Tracker")
    
    if "wcc_role" not in st.session_state: st.session_state.wcc_role = None
    
    if not st.session_state.wcc_role:
        pwd_input = st.text_input("Enter Password:", type="password", key="wcc_login_pwd_v2")
        if st.button("🔓 Unlock Tracker"):
            if pwd_input == "Vision@321": st.session_state.wcc_role = "requester"
            elif pwd_input == "Account@321": st.session_state.wcc_role = "accountant"
            else: st.error("❌ Wrong Password!")
            st.rerun()
    else:
        # तुमची पूर्ण WCC Tracker ची लॉजिक इथे येईल (जी तुम्ही आधी वापरत होतात)
        st.info(f"Logged in as: {st.session_state.wcc_role}")
        # ... (मी दिलेला पूर्ण WCC कोड इथे पेस्ट करा)
