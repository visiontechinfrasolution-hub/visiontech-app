import streamlit as st
from supabase import create_client
import pandas as pd

# Modular Pages लोड करणे
from pages_code import boq_report, po_report, site_detail, indus_data, wcc_tracker, data_entry, finance_entry, audit_portal, rfai_billing

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS SETUP ---
tabs = st.tabs([
    "📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", 
    "📊 Indus Basic Data", "📡 WCC Tracker", "📁 Data Entry", 
    "💰 Finance Entry", "📝 Audit Portal", "📢 RFAI Billing Pending"
])

# --- 4. CALLING MODULES ---
with tabs[0]: boq_report.show(supabase)
with tabs[1]: po_report.show(supabase)
with tabs[2]: site_detail.show(supabase)
with tabs[3]: indus_data.show(supabase)
with tabs[4]: wcc_tracker.show(supabase)
with tabs[5]: data_entry.show(supabase, URL)
with tabs[6]: finance_entry.show(supabase)
with tabs[7]: audit_portal.show(supabase)
with tabs[8]: rfai_billing.show(supabase)
