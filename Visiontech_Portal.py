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
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (NO CHANGE)
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_v5")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v5")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_v5")
        with c4: dispatch_date = st.date_input("📅 Date", value=None, key="boq_d_v5")
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"], key="boq_t_v5")
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"], key="boq_tsp_v5")
        with c7: 
            st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty() 

    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        response = query.execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL'], '')
            st.dataframe(df, use_container_width=True, hide_index=True)

# =====================================================================
# 🟦 TAB 2: PO REPORT (NO CHANGE)
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        pwd = st.text_input("Password:", type="password", key="p_pwd")
        if st.button("Unlock 🔓"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
    else:
        with st.form("po_f_new"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: s_po = st.text_input("📄 PO Number")
            with c2: s_ship = st.text_input("🚚 Shipment No")
            with c3: s_rec = st.text_input("🧾 Receipt No")
            with c4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        
        if sub_po:
            query = supabase.table("PO Report").select("*")
            if s_po: query = query.eq("PO Number", int(s_po))
            if s_ship: query = query.ilike("Shipment Number", f"%{s_ship.strip()}%")
            if s_rec: query = query.ilike("Receipt Number", f"%{s_rec.strip()}%")
            res = query.execute()
            if res.data:
                po_df = pd.DataFrame(res.data).fillna('').astype(str)
                st.dataframe(po_df, use_container_width=True, hide_index=True)

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL (FIXED VERTICAL FORMAT + WHATSAPP)
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    if st.session_state.get('site_unlocked', False):
        with st.form("sd_v5_new"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            sub_sd = st.form_submit_button("🔍 Search")
        if sub_sd:
            query = supabase.table("Site Detail").select("*")
            if p_id: query = query.ilike("Project Number", f"%{p_id}%")
            if site_id: query = query.ilike("SITE ID", f"%{site_id}%")
            res = query.execute()
            if res.data:
                for row in res.data:
                    # Vertical formatting with no extra spaces
                    site_txt = (
                        f"*Project Number* :- {row.get('Project Number','-')}\n"
                        f"*SITE ID* :- {row.get('SITE ID','-')}\n"
                        f"*Site Name* :- {row.get('Site Name','-')}\n"
                        f"*District* :- {row.get('District','-')}\n"
                        f"*Lat-Long* :- {row.get('Latitude','')} , {row.get('Longitude','')}"
                    )
                    st.markdown("---")
                    st.text(site_txt) # Preserves one-below-another format
                    wa_site = f"🏗️ *SITE DETAIL*\n{site_txt}"
                    st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_site)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold;">🚀 Send to WhatsApp</button></a>', unsafe_allow_html=True)
    else:
        if st.text_input("Password Site", type="password", key="s_pwd") == "1234": st.session_state.site_unlocked = True; st.rerun()

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (FIXED VERTICAL FORMAT)
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_v5_new"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID", key="ind_id")
        with i2: in_nm = st.text_input("🏢 Site Name", key="ind_nm")
        with i3: in_cl = st.text_input("🗺️ Cluster", key="ind_cl")
        sub_in = st.form_submit_button("🔍 Search Indus")
    
    if sub_in:
        query = supabase.table("Indus Data").select("*")
        if in_id: query = query.ilike("Site ID", f"%{in_id.strip()}%")
        if in_nm: query = query.ilike("Site Name", f"%{in_nm.strip()}%")
        if in_cl: query = query.ilike("Cluster", f"%{in_cl.strip()}%")
        res = query.execute()
        
        if res.data:
            for row in res.data:
                ind_txt = (
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
                st.text(ind_txt)
                wa_ind = f"📊 *INDUS DATA*\n{ind_txt}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_ind)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold;">🚀 Send to WhatsApp</button></a>', unsafe_allow_html=True)
