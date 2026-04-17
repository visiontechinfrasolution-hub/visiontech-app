import streamlit as st
from supabase import create_client

# Modular Pages Import
# आपण इथे 'jms_generator' नवीन ॲड केला आहे
from pages_code import (
    boq_report, po_report, site_detail, indus_data, 
    wcc_tracker, data_entry, finance_entry, 
    audit_portal, rfai_billing, jms_generator
)

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide", initial_sidebar_state="collapsed")

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stApp { background-color: #F8FAFC; }
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 20px;
        border: none; background-color: white; color: #1E293B;
        font-size: 20px; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease; margin-bottom: 20px;
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; white-space: pre-wrap;
    }
    div.stButton > button:hover {
        transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        background-color: #1E3A8A; color: white;
    }
    .back-btn button {
        height: 50px !important; width: 120px !important;
        font-size: 16px !important; background-color: #64748B !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation Logic
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- HEADER (Back Button) ---
if st.session_state.current_page != "Dashboard":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Back"):
        navigate_to("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

# --- 4. MAIN DASHBOARD (BIG ICONS) ---
if st.session_state.current_page == "Dashboard":
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 30px;'>🚀 Visiontech Infra Solutions</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📦\nBOQ Report"): navigate_to("BOQ")
        if st.button("📊\nIndus Data"): navigate_to("Indus")
        if st.button("💰\nFinance Entry"): navigate_to("Finance")

    with col2:
        if st.button("🧾\nPO Report"): navigate_to("PO")
        if st.button("📡\nWCC Tracker"): navigate_to("WCC")
        if st.button("📝\nAudit Portal"): navigate_to("Audit")

    with col3:
        if st.button("🏗️\nSite Detail"): navigate_to("Site")
        if st.button("📁\nData Entry"): navigate_to("Data")
        if st.button("📢\nRFAI Billing"): navigate_to("RFAI")
        # 👇 हे नवीन बटण जे आपण ॲड केलं आहे
        if st.button("📄\nJMS Generator"): navigate_to("JMS")

# --- 5. PAGE ROUTING ---
elif st.session_state.current_page == "BOQ": boq_report.show(supabase)
elif st.session_state.current_page == "PO": po_report.show(supabase)
elif st.session_state.current_page == "Site": site_detail.show(supabase)
elif st.session_state.current_page == "Indus": indus_data.show(supabase)
elif st.session_state.current_page == "WCC": wcc_tracker.show(supabase)
elif st.session_state.current_page == "Data": data_entry.show(supabase, URL)
elif st.session_state.current_page == "Finance": finance_entry.show(supabase)
elif st.session_state.current_page == "Audit": audit_portal.show(supabase)
elif st.session_state.current_page == "RFAI": rfai_billing.show(supabase)
# 👇 हे महत्त्वाचे: नवीन JMS पेज इथून लोड होईल
elif st.session_state.current_page == "JMS": jms_generator.show(supabase)
