import streamlit as st
from supabase import create_client
import os
import jms_generator # <--- ही फाईल तुमच्या portal_app.py च्या शेजारीच हवी

# Modular Pages Import
from pages_code import (
    boq_report, po_report, site_detail, indus_data, 
    wcc_tracker, data_entry, finance_entry, 
    audit_portal, rfai_billing
)

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. NAVIGATION LOGIC ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- 3. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide", initial_sidebar_state="collapsed")

# --- 4. MAIN DASHBOARD ---
if st.session_state.current_page == "Dashboard":
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🚀 Visiontech Infra Solutions</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    # ... तुमचे इतर बटन्स इथे असतीलच ...

    with col3:
        if st.button("🏗️\nSite Detail"): navigate_to("Site")
        if st.button("📁\nData Entry"): navigate_to("Data")
        if st.button("📢\nRFAI Billing"): navigate_to("RFAI")
        # 👇 तुमच्या फोटोप्रमाणे नाव 'JMS Generator' ठेवले आहे
        if st.button("📄\nJMS Generator"): navigate_to("JMS Generator")

# --- 5. PAGE ROUTING (फिक्स केलेला भाग) ---
elif st.session_state.current_page != "Dashboard":
    # बॅक बटन
    if st.button("⬅️ Back"): navigate_to("Dashboard")
    st.divider()

    # राउटिंग
    cp = st.session_state.current_page
    
    if cp == "BOQ": boq_report.show(supabase)
    elif cp == "PO": po_report.show(supabase)
    elif cp == "Site": site_detail.show(supabase)
    elif cp == "Indus": indus_data.show(supabase)
    elif cp == "WCC": wcc_tracker.show(supabase)
    elif cp == "Data": data_entry.show(supabase, URL)
    elif cp == "Finance": finance_entry.show(supabase)
    elif cp == "Audit": audit_portal.show(supabase)
    elif cp == "RFAI": rfai_billing.show(supabase)
    
    # 👇 आता फोटोमधील बटणाचं नाव 'JMS Generator' असल्याने इथेही तेच नाव मॅच होईल!
    elif cp == "JMS Generator":
        try:
            jms_generator.show(supabase)
        except Exception as e:
            st.error(f"JMS Generator फाईल लोड करताना अडचण आली: {e}")
