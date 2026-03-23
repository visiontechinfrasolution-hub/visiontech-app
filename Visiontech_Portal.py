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

# --- SIDEBAR UPDATED (AS REQUESTED) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group") # <--- Changed here
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions") # <--- Changed here

# --- 3. HORIZONTAL TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (NO LOGIC CHANGES)
# =====================================================================
with tab1:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    with st.form("search_form"):
        # Wahi aapke 8 Columns
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_infra")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_infra")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_infra")
        with c4: dispatch_date = st.date_input("📅 Date", value=None, key="boq_d_infra")
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"], key="boq_t_infra")
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"], key="boq_tsp_infra")
        with c7: 
            st.write(""); st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")
        with c8:
            st.write(""); status_placeholder = st.empty() 

    st.divider()
    st.markdown("#### 📊 Quick Reports & Downloads")
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_infra")
    with r3: new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)

    if submit_search:
        res = supabase.table("BOQ Report").select("*").ilike("Site ID", f"%{site_query}%").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df, use_container_width=True)
            wa_msg = f"📦 *VISIONTECH INFRA BOQ*\n📍 *Site:* {site_query}\n🚀 _Visiontech Infra_"
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">📲 Share BOQ</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟦 TAB 2: PO REPORT (PO NUMBER LEFT & CENTERED TABLE)
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Visiontech Infra - PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        pwd = st.text_input("Enter Password:", type="password", key="p_pwd_infra")
        if st.button("Unlock 🔓", key="p_u_infra"):
            if pwd == "1234": st.session_state.po_unlocked = True; st.rerun()
    else:
        with st.form("po_form_infra"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: s_po = st.text_input("📄 PO Number")
            with col2: s_ship = st.text_input("🚚 Shipment No")
            with col3: s_rec = st.text_input("🧾 Receipt No")
            with col4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        
        if sub_po:
            res = supabase.table("PO Report").select("*").eq("PO Number", int(s_po)).execute()
            if res.data:
                po_df = pd.DataFrame(res.data)
                st.dataframe(po_df, use_container_width=True, hide_index=True)
                
                summary_df = po_df[['Shipment Number', 'Receipt Number']].drop_duplicates().reset_index(drop=True)
                summary_df.index = summary_df.index + 1
                
                st.markdown("---")
                st.markdown(f"📄 **PO Number :- {s_po}**")
                
                c_l, c_m, c_r = st.columns([1, 2, 1])
                with c_m:
                    st.markdown("""<style>div[data-testid="stTable"] table {text-align: center;} th {text-align: center !important;} td {text-align: center !important;}</style>""", unsafe_allow_html=True)
                    st.table(summary_df)

                wa_msg = f"🧾 *VISIONTECH INFRA PO*\n📄 *PO Number :-* {s_po}\n"
                for i, r in summary_df.iterrows():
                    wa_msg += f"🔹 {r['Shipment Number']} | {r['Receipt Number']}\n"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">📲 Send to Group</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟨 TAB 3: SITE DETAIL (ORIGINAL)
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Visiontech Infra Site Detail</h3>", unsafe_allow_html=True)
    if st.session_state.get('site_unlocked', False):
        with st.form("sd_form_infra"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            sub_sd = st.form_submit_button("🔍 Search Site")
        if sub_sd:
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id}%").execute()
            if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
    else:
        pwd = st.text_input("Enter Password:", type="password", key="s_pwd_infra")
        if st.button("Unlock Site 🔓", key="s_u_infra"):
            if pwd == "1234": st.session_state.site_unlocked = True; st.rerun()

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (EK KE NICHE EK)
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_infra"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID", key="ind_id_infra")
        with i2: in_nm = st.text_input("🏢 Site Name", key="ind_nm_infra")
        with i3: in_cl = st.text_input("🗺️ Cluster", key="ind_cl_infra")
        sub_in = st.form_submit_button("🔍 Search Indus")
    
    if sub_in:
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id.strip()}%").execute()
        if res.data:
            for row in res.data:
                fse_name = row.get('FSE ', row.get('FSE', '-'))
                st.markdown(f"""
                ---
                **Site ID** :- {row.get('Site ID', '-')}  
                **Site Name** :- {row.get('Site Name', '-')}  
                **FSE** :- {fse_name}  
                **Lat-Long** :- {row.get('Lat')} {row.get('Long')}
                """)
                wa_msg = f"📊 *VISIONTECH INFRA*\n📍 *Site ID:* {row.get('Site ID')}\n👷 *FSE:* {fse_name}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Send to VISPL Group</button></a>', unsafe_allow_html=True)
