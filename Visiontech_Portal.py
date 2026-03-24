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
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (STRICTLY AS PER YOUR CODE)
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_v5")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v5")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_v5")
        with c4: dispatch_date_inp = st.date_input("📅 Date", value=None, key="boq_d_v5")
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"], key="boq_t_v5")
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"], key="boq_tsp_v5")
        with c7: 
            st.write(""); submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty() 

    st.divider()
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_pick = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_v5")
    
    # --- Generate New BOQ Logic ---
    generate_boq_trigger = False
    with r3:
        if st.button("📄 Generate New BOQ", use_container_width=True):
            if boq_date_pick:
                generate_boq_trigger = True # Trigger to filter table below
                f_date = boq_date_pick.strftime('%d-%b-%Y')
                msg = f"Request for New BOQ Generation for Date: {f_date}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(msg)}">Click to Open WhatsApp</a>', unsafe_allow_html=True)
            else: st.warning("Select Date!")

    if submit_search or stn_pending_btn or generate_boq_trigger:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        # SEARCH LOGIC
        if not stn_pending_btn and not generate_boq_trigger:
            if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
            if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
            if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        # If Generate New BOQ is clicked, we filter by the selected BOQ Date
        if generate_boq_trigger:
             query = query.eq("BOQ Date", boq_date_pick.strftime('%Y-%m-%d'))
        
        response = query.execute()
        if response.data:
            df = pd.DataFrame(response.data)
            
            # --- STN PENDING SPECIFIC FILTERS ---
            if stn_pending_btn:
                df = df[
                    (df['Product'] == 'Capex') & 
                    (df['Issue From'] == 'Warehouse') & 
                    (df['Parent/Child'] == 'Parent')
                ]
                df['Qty A'] = pd.to_numeric(df['Qty A'], errors='coerce').fillna(0)
                df['Qty B'] = pd.to_numeric(df['Qty B'], errors='coerce').fillna(0)
                df['Qty C'] = pd.to_numeric(df['Qty C'], errors='coerce').fillna(0)
                df = df[(df['Qty A'] > 0) & (df['Qty B'] > 0) & (df['Qty C'] == 0)]

            # --- COMMON FORMATTING & MERGE ---
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            if 'Item Code' in df.columns:
                agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col != 'Item Code'}
                df = df.groupby('Item Code', as_index=False).agg(agg_dict)
            
            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            final_cols = [c for c in mera_sequence if c in df.columns]
            st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

# =====================================================================
# 🟦 TABS 2, 3, 4 (RESTORED AS PER PREVIOUS WORKING CODE)
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        if st.text_input("Password:", type="password", key="p_pwd_fix") == "1234":
            st.session_state.po_unlocked = True; st.rerun()
    else:
        with st.form("po_f"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: s_po = st.text_input("📄 PO Number")
            with c2: s_sh = st.text_input("🚚 Shipment No")
            with c3: s_re = st.text_input("🧾 Receipt No")
            with c4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        if sub_po:
            q = supabase.table("PO Report").select("*")
            if s_po: q = q.eq("PO Number", int(s_po))
            res = q.execute()
            if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    if st.session_state.get('site_unlocked', False):
        with st.form("sd_f"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            if st.form_submit_button("🔍 Search"):
                res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id}%").execute()
                if res.data:
                    for r in res.data:
                        t = f"*Site ID* :- {r.get('SITE ID')}\n*Site Name* :- {r.get('Site Name')}"
                        st.text(t)
                        st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(t)}">WhatsApp</a>', unsafe_allow_html=True)
    else:
        if st.text_input("Password Site", type="password", key="s_pwd_fix") == "1234": st.session_state.site_unlocked = True; st.rerun()

with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_f"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID")
        if st.form_submit_button("🔍 Search Indus"):
            res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
            if res.data:
                for r in res.data:
                    it = f"*Site ID* :- {r.get('Site ID')}\n*District* :- {r.get('District')}"
                    st.text(it)
