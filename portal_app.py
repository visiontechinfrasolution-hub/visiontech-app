import streamlit as st
from supabase import create_client

# Modular Pages Import
from pages_code import boq_report, po_report, site_detail, indus_data, wcc_tracker, data_entry, finance_entry, audit_portal, rfai_billing

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Visiontech Portal", layout="wide")

# CSS for App-like Buttons
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 100px;
        border-radius: 15px;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
        border: 2px solid #1E3A8A;
        background-color: white;
        color: #1E3A8A;
    }
    .stButton>button:hover {
        background-color: #1E3A8A;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation Logic
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- SIDEBAR (Always show Back to Dashboard) ---
if st.session_state.current_page != "Dashboard":
    if st.sidebar.button("🏠 Back to Dashboard"):
        navigate_to("Dashboard")
st.sidebar.divider()
st.sidebar.title("🧭 Visiontech Portal")

# --- MAIN PAGE LOGIC ---
if st.session_state.current_page == "Dashboard":
    st.markdown("<h2 style='text-align: center;'>🚀 Visiontech Main Dashboard</h2>", unsafe_allow_html=True)
    st.write("Click a button to open the module:")
    st.divider()

    # Grid Layout (3 Columns)
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

# --- PAGE ROUTING ---
elif st.session_state.current_page == "BOQ": boq_report.show(supabase)
elif st.session_state.current_page == "PO": po_report.show(supabase)
elif st.session_state.current_page == "Site": site_detail.show(supabase)
elif st.session_state.current_page == "Indus": indus_data.show(supabase)
elif st.session_state.current_page == "WCC": wcc_tracker.show(supabase)
elif st.session_state.current_page == "Data": data_entry.show(supabase, URL)
elif st.session_state.current_page == "Finance": finance_entry.show(supabase)
elif st.session_state.current_page == "Audit": audit_portal.show(supabase)
elif st.session_state.current_page == "RFAI": rfai_billing.show(supabase)
