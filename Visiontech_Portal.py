import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import urllib.parse

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

# Sidebar
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (FIXED BUTTONS)
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b")
        with c4: dispatch_date = st.date_input("📅 Date", value=None)
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery"])
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Ericsson", "Nokia"])
        with c7: 
            st.write(""); submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty()

    st.divider()
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])
    
    # --- FUNCTIONAL BUTTONS ---
    with r1:
        if st.button("🚨 STN Pending Sites", use_container_width=True):
            st.info("Searching Pending Sites...")
            res = supabase.table("BOQ Report").select("*").execute()
            if res.data:
                df_stn = pd.DataFrame(res.data)
                # Filter Logic for STN Pending
                df_stn = df_stn[(df_stn['Product'].astype(str).str.contains('capex', case=False, na=False)) & (df_stn['Qty A'] != df_stn['Qty B'])]
                st.dataframe(df_stn, use_container_width=True)

    with r2: boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed")
    
    with r3:
        if st.button("📄 Generate New BOQ", use_container_width=True):
            msg = "Request for New BOQ Generation"
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(msg)}">Click to WhatsApp</a>', unsafe_allow_html=True)

    if submit_search:
        query = supabase.table("BOQ Report").select("*")
        if project_query: query = query.ilike("Project Number", f"%{project_query}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query}%")
        
        res = query.execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df = df.fillna('').astype(str)
            st.dataframe(df, use_container_width=True, hide_index=True)

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL (VERTICAL + PROJECT ID SEARCH + WHATSAPP)
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    if st.session_state.get('site_unlocked', False):
        with st.form("sd_form"):
            s1, s2 = st.columns(2)
            with s1: p_id_search = st.text_input("📁 Project ID")
            with s2: s_id_search = st.text_input("📍 Site ID")
            sub_sd = st.form_submit_button("🔍 Search Site")
        
        if sub_sd:
            query = supabase.table("Site Detail").select("*")
            if p_id_search: query = query.ilike("Project Number", f"%{p_id_search}%")
            if s_id_search: query = query.ilike("SITE ID", f"%{s_id_search}%")
            
            res = query.execute()
            if res.data:
                for row in res.data:
                    site_text = (
                        f"*Project Number* :- {row.get('Project Number', '-')}\n"
                        f"*SITE ID* :- {row.get('SITE ID', '-')}\n"
                        f"*Site Name* :- {row.get('Site Name', '-')}\n"
                        f"*District* :- {row.get('District', '-')}\n"
                        f"*Lat-Long* :- {row.get('Latitude', '')} , {row.get('Longitude', '')}"
                    )
                    st.markdown("---")
                    st.markdown(site_text)
                    wa_site = f"🏗️ *SITE DETAIL*\n{site_text}"
                    st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_site)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">🚀 Send to WhatsApp</button></a>', unsafe_allow_html=True)
    else:
        if st.text_input("Password", type="password", key="pwd_site") == "1234":
            st.session_state.site_unlocked = True
            st.rerun()

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (STRICTLY VERTICAL)
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_f"):
        i1 = st.text_input("📍 Site ID")
        sub_in = st.form_submit_button("🔍 Search")
    
    if sub_in:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{i1}%").execute()
        if res.data:
            for row in res.data:
                indus_text = (
                    f"*Site ID* :- {row.get('Site ID', '-')}\n"
                    f"*Site Name* :- {row.get('Site Name', '-')}\n"
                    f"*District* :- {row.get('District', '-')}\n"
                    f"*Area Name* :- {row.get('Area Name', '-')}\n"
                    f"*Tech Name* :- {row.get('Tech Name', '-')}\n"
                    f"*Tech Number* :- {row.get('Tech Number', '-')}\n"
                    f"*FSE* :- {row.get('FSE', '-')}\n"
                    f"*FSE Number* :- {row.get('FSE Number', '-')}\n"
                    f"*AOM Name* :- {row.get('AOM Name', '-')}\n"
                    f"*AOM Number* :- {row.get('AOM Number', '-')}\n"
                    f"*Lat-Long* :- {row.get('Lat', '')} , {row.get('Long', '')}"
                )
                st.markdown("---")
                st.markdown(indus_text)
                wa_indus = f"📊 *INDUS DATA*\n{indus_text}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_indus)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px; border-radius: 5px;">🚀 Send to WhatsApp</button></a>', unsafe_allow_html=True)

# (Note: PO Report logic remains same as per your original file)
