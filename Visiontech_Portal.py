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

# --- 2. UI SETUP & SIDEBAR MENU ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 Main Menu")
menu_selection = st.sidebar.radio("Apna Module Chunein:", ["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Industrial Solutions")

# =====================================================================
# 🟩 PAGE 1: BOQ REPORT
# =====================================================================
if menu_selection == "📦 BOQ Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Transporter']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1])
        with c1: project_query = st.text_input("📁 Project No.")
        with c2: site_query = st.text_input("📍 Site ID")
        with c3: boq_query = st.text_input("📄 BOQ")
        with c4: dispatch_date = st.date_input("📅 Date", value=None)
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics"])
        with c6: 
            st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")

    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(100)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        res = query.execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # WhatsApp for BOQ
            wa_msg = f"*Visiontech BOQ Report*\nSite: {site_query or 'Multiple'}\nProject: {project_query or '-'}\nTotal Items: {len(df)}"
            encoded_msg = urllib.parse.quote(wa_msg)
            st.markdown(f'<a href="whatsapp://send?text={encoded_msg}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share BOQ to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟦 PAGE 2: PO REPORT
# =====================================================================
elif menu_selection == "🧾 PO Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Purchase Order (PO) Report</h3>", unsafe_allow_html=True)
    if "po_unlocked" not in st.session_state: st.session_state.po_unlocked = False

    if not st.session_state.po_unlocked:
        pwd = st.text_input("Enter Password:", type="password")
        if st.button("Unlock 🔓"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
            else: st.error("❌ Galat Password!")
    else:
        with st.form("po_search"):
            col1, col2 = st.columns(2)
            with col1: s_po = st.text_input("📄 PO Number")
            with col2: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        
        if sub_po:
            res = supabase.table("PO Report").select("*").eq("PO Number", int(s_po)).execute()
            if res.data:
                df = pd.DataFrame(res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # WhatsApp for PO
                wa_msg = f"*Visiontech PO Report*\nPO No: {s_po}\nOrg: {res.data[0].get('Organization')}\nItems: {len(df)}"
                encoded_msg = urllib.parse.quote(wa_msg)
                st.markdown(f'<a href="whatsapp://send?text={encoded_msg}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share PO to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟨 PAGE 3: SITE DETAIL
# =====================================================================
elif menu_selection == "🏗️ Site Detail":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)
    if "site_unlocked" not in st.session_state: st.session_state.site_unlocked = False

    if not st.session_state.site_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="s_pwd")
        if st.button("Unlock 🔓", key="s_btn"):
            if pwd == "1234": st.session_state.site_unlocked = True; st.rerun()
    else:
        with st.form("site_form"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            sub_s = st.form_submit_button("🔍 Search Site")
        
        if sub_s:
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id}%").execute()
            if res.data:
                df = pd.DataFrame(res.data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # WhatsApp for Site Detail
                wa_msg = f"*Visiontech Site Detail*\nSite ID: {site_id}\nStatus: {res.data[0].get('SITE STATUS')}\nTeam: {res.data[0].get('TEAM NAME')}"
                encoded_msg = urllib.parse.quote(wa_msg)
                st.markdown(f'<a href="whatsapp://send?text={encoded_msg}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share Detail to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA
# =====================================================================
elif menu_selection == "📊 Indus Basic Data":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    with st.form("indus_form"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID")
        with i2: in_nm = st.text_input("🏢 Site Name")
        with i3: in_cl = st.text_input("🗺️ Cluster")
        sub_i = st.form_submit_button("🔍 Search Indus")
    
    if sub_i:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id.strip()}%").execute()
        if res.data:
            for row in res.data:
                fse_name = row.get('FSE ', row.get('FSE', '-'))
                wa_msg = f"*VISPL AUTOMATION REPORT*\nSite ID: {row.get('Site ID')}\nSite Name: {row.get('Site Name')}\nFSE: {fse_name}\nLat-Long: {row.get('Lat')} {row.get('Long')}"
                encoded_msg = urllib.parse.quote(wa_msg)
                
                st.markdown(f"--- \n**Site ID** :- {row.get('Site ID')} | **Site Name** :- {row.get('Site Name')}")
                st.markdown(f'<a href="whatsapp://send?text={encoded_msg}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send to VISPL Group</button></a>', unsafe_allow_html=True)
