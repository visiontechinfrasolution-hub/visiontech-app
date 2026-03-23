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

# Header Section
st.markdown("<h2 style='text-align: center;'>🌐 Visiontech Industrial Solutions Portal</h2>", unsafe_allow_html=True)

# --- 3. HORIZONTAL TABS (Ek ke baaju me ek) ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT
# =====================================================================
with tab1:
    st.markdown("#### 🔍 BOQ Advanced Search & STN Tracker")
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Transporter']

    with st.form("boq_form"):
        c1, c2, c3, c4 = st.columns(4)
        with c1: project_query = st.text_input("📁 Project No.")
        with c2: site_query = st.text_input("📍 Site ID")
        with c3: boq_query = st.text_input("📄 BOQ")
        with c4: 
            st.write(""); submit_search = st.form_submit_button("🔍 Search BOQ", use_container_width=True)

    if submit_search:
        res = supabase.table("BOQ Report").select("*").ilike("Site ID", f"%{site_query}%").limit(100).execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            wa_msg = f"*Visiontech BOQ*\nSite: {site_query}\nItems: {len(df)}"
            encoded_msg = urllib.parse.quote(wa_msg)
            st.markdown(f'<a href="whatsapp://send?text={encoded_msg}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟦 TAB 2: PO REPORT
# =====================================================================
with tab2:
    st.markdown("#### 🧾 Purchase Order (PO) Report")
    if "po_unlocked" not in st.session_state: st.session_state.po_unlocked = False

    if not st.session_state.po_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="po_p")
        if st.button("Unlock PO 🔓"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
            else: st.error("❌ Galat Password!")
    else:
        s_po = st.text_input("📄 Enter PO Number")
        if st.button("Search PO"):
            res = supabase.table("PO Report").select("*").eq("PO Number", int(s_po)).execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                wa_msg = f"*Visiontech PO*\nNo: {s_po}\nItems: {len(res.data)}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟨 TAB 3: SITE DETAIL
# =====================================================================
with tab3:
    st.markdown("#### 🏗️ Site Detail Report")
    if "site_unlocked" not in st.session_state: st.session_state.site_unlocked = False

    if not st.session_state.site_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="site_p_lock")
        if st.button("Unlock Site Detail 🔓"):
            if pwd == "1234": st.session_state.site_unlocked = True; st.rerun()
    else:
        site_id_in = st.text_input("📍 Enter Site ID", key="site_detail_id")
        if st.button("Search Site Detail"):
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id_in}%").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
                wa_msg = f"*Visiontech Site Detail*\nID: {site_id_in}\nStatus: {res.data[0].get('SITE STATUS')}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA
# =====================================================================
with tab4:
    st.markdown("#### 📊 Indus Basic Data Report")
    with st.form("indus_form_tab"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID", key="in_sid_tab")
        with i2: in_nm = st.text_input("🏢 Site Name", key="in_snm_tab")
        with i3: in_cl = st.text_input("🗺️ Cluster", key="in_cl_tab")
        sub_i = st.form_submit_button("🔍 Search Indus", use_container_width=True)

    if sub_i:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id.strip()}%").execute()
        if res.data:
            for row in res.data:
                fse_name = row.get('FSE ', row.get('FSE', '-'))
                wa_msg = f"*VISPL AUTOMATION REPORT*\nSite ID: {row.get('Site ID')}\nSite Name: {row.get('Site Name')}\nFSE: {fse_name}\nLat-Long: {row.get('Lat')} {row.get('Long')}"
                st.markdown(f"--- \n**Site ID** :- {row.get('Site ID')} | **Site Name** :- {row.get('Site Name')}")
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send to VISPL Group</button></a>', unsafe_allow_html=True)
