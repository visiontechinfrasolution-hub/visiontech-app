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

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. HORIZONTAL TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (BLANK BOXES FIXED)
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_infra_v3")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_infra_v3")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_infra_v3")
        with c4: dispatch_date = st.date_input("📅 Date", value=None, key="boq_d_infra_v3")
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"], key="boq_t_infra_v3")
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"], key="boq_tsp_infra_v3")
        with c7: 
            st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty() 

    st.divider()
    st.markdown("#### 📊 Quick Reports & Downloads")
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_infra_v3")
    with r3: new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)

    if submit_search:
        has_filter = False
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        if project_query: query, has_filter = query.ilike("Project Number", f"%{project_query.strip()}%"), True
        if site_query: query, has_filter = query.ilike("Site ID", f"%{site_query.strip()}%"), True
        if boq_query: query, has_filter = query.ilike("BOQ", f"%{boq_query.strip()}%"), True
        if dispatch_date: query, has_filter = query.eq("Dispatch Date", dispatch_date.strftime("%Y-%m-%d")), True
        if transporter: query, has_filter = query.ilike("Transporter", f"%{transporter.strip()}%"), True
        if tsp_partner: query, has_filter = query.ilike("TSP Partner Name", f"%{tsp_partner.strip()}%"), True

        if has_filter:
            try:
                response = query.execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    
                    # --- BLANK HANDLING ---
                    qty_cols = ['Qty A', 'Qty B', 'Qty C']
                    for col in qty_cols:
                        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    if 'Item Code' in df.columns:
                        agg_funcs = {c: 'sum' if c in qty_cols else 'first' for c in df.columns if c != 'Item Code'}
                        df = df.groupby('Item Code', as_index=False).agg(agg_funcs)

                    # --- STN STATUS LOGIC ---
                    stn_df = df.copy()
                    if 'Product' in stn_df.columns and 'Issue From' in stn_df.columns and 'Parent/Child' in stn_df.columns:
                        stn_df = stn_df[(stn_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & (stn_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & (stn_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent')]
                    
                    total_a, total_b, total_c = int(stn_df['Qty A'].sum()), int(stn_df['Qty B'].sum()), int(stn_df['Qty C'].sum())
                    if total_a > 0:
                        if total_a == total_b and total_c > 0: status_placeholder.markdown("<div style='background-color: #d4edda; color: #155724; border: 1px solid #28a745; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold;'>✅ STN DONE</div>", unsafe_allow_html=True)
                        else: status_placeholder.markdown("<div style='background-color: #f8d7da; color: #721c24; border: 1px solid #dc3545; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold;'>❌ STN PENDING</div>", unsafe_allow_html=True)

                    # --- FINAL CLEANUP (Replace nulls with Blanks) ---
                    for col in df.columns:
                        if 'date' in col.lower(): df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
                    
                    df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                    
                    final_cols = [c for c in mera_sequence if c in df.columns]
                    df = df[final_cols + [c for c in df.columns if c not in final_cols]]

                    st.success(f"✅ Record Mil Gaya! ({len(df)} Unique Items)")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else: st.warning("❌ Data nahi mila.")
            except Exception as e: st.error(f"Error detail: {e}")

# =====================================================================
# 🟦 TAB 2: PO REPORT (BLANK BOXES FIXED)
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Visiontech Infra - PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        pwd = st.text_input("Enter Password:", type="password", key="p_pwd_v3")
        if st.button("Unlock 🔓", key="p_u_v3"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
    else:
        with st.form("po_form_v3"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: s_po = st.text_input("📄 PO Number")
            with col2: s_ship = st.text_input("🚚 Shipment No")
            with col3: s_rec = st.text_input("🧾 Receipt No")
            with col4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        
        if sub_po:
            res = supabase.table("PO Report").select("*").eq("PO Number", int(s_po)).execute()
            if res.data:
                po_df = pd.DataFrame(res.data).fillna('').astype(str).replace(['None', 'nan', 'NULL'], '')
                st.dataframe(po_df, use_container_width=True, hide_index=True)
                
                summary_df = po_df[['Shipment Number', 'Receipt Number']].drop_duplicates().reset_index(drop=True)
                summary_df.index = summary_df.index + 1
                st.markdown("---")
                st.markdown(f"📄 **PO Number :- {s_po}**")
                st.table(summary_df)

# =====================================================================
# 🟨 TAB 3: SITE DETAIL (BLANK BOXES FIXED)
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Visiontech Infra Site Detail</h3>", unsafe_allow_html=True)
    if st.session_state.get('site_unlocked', False):
        with st.form("sd_form_v3"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            sub_sd = st.form_submit_button("🔍 Search Site")
        if sub_sd:
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id}%").execute()
            if res.data:
                site_df = pd.DataFrame(res.data).fillna('').astype(str).replace(['None', 'nan', 'NULL'], '')
                st.dataframe(site_df, use_container_width=True)
    else:
        pwd = st.text_input("Enter Password:", type="password", key="s_pwd_v3")
        if st.button("Unlock Site 🔓", key="s_u_v3"):
            if pwd == "1234": st.session_state.site_unlocked = True; st.rerun()

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (EK KE NICHE EK)
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_v3"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID", key="ind_id_v3")
        with i2: in_nm = st.text_input("🏢 Site Name", key="ind_nm_v3")
        with i3: in_cl = st.text_input("🗺️ Cluster", key="ind_cl_v3")
        sub_in = st.form_submit_button("🔍 Search Indus")
    
    if sub_in:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id.strip()}%").execute()
        if res.data:
            for row in res.data:
                fse_name = row.get('FSE ', row.get('FSE', '-'))
                st.markdown(f"--- \n**Site ID** :- {row.get('Site ID', '-')}  \n**Site Name** :- {row.get('Site Name', '-')}  \n**FSE** :- {fse_name}  \n**Lat-Long** :- {row.get('Lat', '')} {row.get('Long', '')}")
