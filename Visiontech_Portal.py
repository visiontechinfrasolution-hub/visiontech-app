import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 Visiontech")
st.sidebar.caption("© 2026 Visiontech Industrial Solutions")

# =====================================================================
# 3. HORIZONTAL TABS (Ek ke baaju me ek)
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 PAGE 1: BOQ REPORT
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.")
        with c2: site_query = st.text_input("📍 Site ID")
        with c3: boq_query = st.text_input("📄 BOQ")
        with c4: dispatch_date = st.date_input("📅 Date", value=None)
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"])
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"])
        with c7: 
            st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty() 

    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        res = query.execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # WhatsApp Button
            wa_msg = f"*Visiontech BOQ Report*\nSite: {site_query or '-'}\nProject: {project_query or '-'}\nRecords: {len(df)}"
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send BOQ to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟦 PAGE 2: PO REPORT
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Purchase Order (PO) Report</h3>", unsafe_allow_html=True)
    if "po_unlocked" not in st.session_state: st.session_state.po_unlocked = False

    if not st.session_state.po_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="po_pass")
        if st.button("Unlock 🔓", key="po_unl"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
            else: st.error("❌ Galat Password!")
    else:
        with st.form("po_search_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: search_po = st.text_input("📄 PO Number")
            with col2: search_shipment = st.text_input("🚚 Shipment Number")
            with col3: search_receipt = st.text_input("🧾 Receipt Number")
            with col4: 
                st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                submit_po_search = st.form_submit_button("🔍 Search PO")

        if submit_po_search:
            q = supabase.table("PO Report").select("*")
            if search_po: q = q.eq("PO Number", int(search_po))
            res = q.execute()
            if res.data:
                po_df = pd.DataFrame(res.data)
                st.dataframe(po_df, use_container_width=True, hide_index=True)
                
                # --- PO SUMMARY (NO DUPLICATES) ---
                st.markdown("#### 📋 PO Summary (Unique)")
                unique_po = po_df[['PO Number', 'Shipment Number', 'Receipt Number']].drop_duplicates()
                for idx, row in unique_po.iterrows():
                    st.write(f"**PO Number:** {row['PO Number']} | **Shipment:** {row['Shipment Number']} | **Receipt:** {row['Receipt Number']}")
                
                # WhatsApp Button
                wa_msg = f"*Visiontech PO Report*\nPO: {search_po}\nUnique Lines: {len(unique_po)}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send PO to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟨 PAGE 3: SITE DETAIL
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)
    if "site_unlocked" not in st.session_state: st.session_state.site_unlocked = False

    if not st.session_state.site_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="sd_pass")
        if st.button("Unlock 🔓", key="sd_unl"):
            if pwd == "1234": st.session_state.site_unlocked = True; st.rerun()
    else:
        with st.form("site_search_form"):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: search_proj_id = st.text_input("📁 Project ID")
            with col2: search_site_id = st.text_input("📍 Site ID")
            with col3: st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_site_search = st.form_submit_button("🔍 Search Site")

        if submit_site_search:
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{search_site_id}%").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True, hide_index=True)
                # WhatsApp Button
                wa_msg = f"*Visiontech Site Detail*\nSite ID: {search_site_id}\nProject: {search_proj_id}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send Detail to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    with st.form("indus_search_form"):
        col1, col2, col3 = st.columns(3)
        with col1: s_id = st.text_input("📍 Site ID", key="ind_id")
        with col2: s_nm = st.text_input("🏢 Site Name", key="ind_nm")
        with col3: s_cl = st.text_input("🗺️ Cluster", key="ind_cl")
        submit_indus = st.form_submit_button("🔍 Search Indus Data")

    if submit_indus:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{s_id.strip()}%").execute()
        if res.data:
            for row in res.data:
                fse_name = row.get('FSE ', row.get('FSE', '-'))
                lat_long = f"{row.get('Lat', '')} {row.get('Long', '')}"
                wa_message = f"*VISPL AUTOMATION REPORT*\nSite ID: {row.get('Site ID')}\nSite Name: {row.get('Site Name')}\nFSE: {fse_name}\nLat-Long: {lat_long}"
                
                st.markdown(f"--- \n**Site ID** :- {row.get('Site ID')} | **Site Name** :- {row.get('Site Name')}\n**FSE** :- {fse_name} | **Lat-Long** :- {lat_long}")
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_message)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send to VISPL Group</button></a>', unsafe_allow_html=True)
