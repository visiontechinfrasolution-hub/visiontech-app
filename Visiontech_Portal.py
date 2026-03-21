import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# Excel Download Function
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")
st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

# 🎯 AAPKA EXACT TABLE SEQUENCE (Global)
mera_sequence = [
    'Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ',
    'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child',
    'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number',
    'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment'
]

# --- 3. MAIN SEARCH BOXES (LINE 1) ---
with st.form("search_form"):
    # Ab 8 columns hain taaki UI clean dikhe
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
    
    with c1: project_query = st.text_input("📁 Project No.")
    with c2: site_query = st.text_input("📍 Site ID")
    with c3: boq_query = st.text_input("📄 BOQ")
    with c4: dispatch_date = st.date_input("📅 Date", value=None)
    
    transporter_list = ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"]
    with c5: transporter = st.selectbox("🚚 Transporter", transporter_list)
    
    tsp_list = ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"]
    with c6: tsp_partner = st.selectbox("🤝 TSP Partner", tsp_list)
    
    with c7:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        submit_search = st.form_submit_button("🔍 Search")
        
    with c8:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        status_placeholder = st.empty() 

st.divider()

# --- 4. QUICK REPORTS SECTION (LINE 2) ---
st.markdown("#### 📊 Quick Reports & Downloads")
r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])

with r1:
    stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
with r2:
    boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed")
with r3:
    new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)


# --- LOGIC 1: STN PENDING SITES REPORT ---
if stn_pending_btn:
    status_placeholder.empty()
    st.info("⏳ Visiontech ka STN Pending data nikal rahe hain...")
    try:
        response = supabase.table("BOQ Report").select("*").ilike("Transporter", "%visiontech%").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # 🔥 NEW STRICT LOGIC: Capex + Warehouse + Parent
            if 'Product' in df.columns and 'Issue From' in df.columns and 'Parent/Child' in df.columns:
                df = df[
                    (df['Product'].astype(str).str.contains('capex', case=False, na=False)) & 
                    (df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & 
                    (df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent')
                ]

            if not df.empty and 'Project Number' in df.columns and 'Item Code' in df.columns:
                agg_funcs = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col not in ['Project Number', 'Item Code']}
                items_df = df.groupby(['Project Number', 'Item Code'], as_index=False).agg(agg_funcs)

                project_totals = items_df.groupby('Project Number', as_index=False)[qty_cols].sum()
                
                # 🔥 STRICT QTY LOGIC: Qty A > 0 AND Qty B > 0 AND Qty C == 0
                pending_mask = (project_totals['Qty A'] > 0) & (project_totals['Qty B'] > 0) & (project_totals['Qty C'] == 0)
                pending_projects = project_totals[pending_mask]['Project Number']
                
                pending_df = items_df[items_df['Project Number'].isin(pending_projects)]
                
                if not pending_df.empty:
                    st.error(f"🚨 {len(pending_projects)} Sites aisi hain jinka STN Pending hai!")
                    for col in qty_cols:
                        pending_df[col] = pending_df[col].astype(int)
                    
                    final_cols = [c for c in mera_sequence if c in pending_df.columns]
                    bache_hue_cols = [c for c in pending_df.columns if c not in final_cols]
                    pending_df = pending_df[final_cols + bache_hue_cols]

                    st.dataframe(pending_df, use_container_width=True, hide_index=True)
                    
                    # Excel Download Button
                    csv = convert_df_to_csv(pending_df)
                    st.download_button(label="📥 Download Excel File", data=csv, file_name="STN_Pending_Sites.csv", mime="text/csv")
                else:
                    st.success("✅ Wah! Visiontech ka koi bhi STN Pending nahi hai
