import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

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

    mera_sequence = [
        'Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ',
        'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child',
        'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number',
        'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment'
    ]

    with st.form("search_form"):
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

    st.markdown("#### 📊 Quick Reports & Downloads")
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])

    with r1:
        stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2:
        boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed")
    with r3:
        new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)

    if stn_pending_btn:
        status_placeholder.empty()
        st.info("⏳ Visiontech ka STN Pending data nikal rahe hain...")
        try:
            response = supabase.table("BOQ Report").select("*").ilike("Transporter", "%visiontech%").limit(50000).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                qty_cols = ['Qty A', 'Qty B', 'Qty C']
                for col in qty_cols:
                    if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                if 'Project Number' in df.columns and 'Item Code' in df.columns:
                    agg_funcs = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col not in ['Project Number', 'Item Code']}
                    items_df = df.groupby(['Project Number', 'Item Code'], as_index=False).agg(agg_funcs)

                    if 'Product' in items_df.columns and 'Issue From' in items_df.columns and 'Parent/Child' in items_df.columns:
                        pending_mask = (
                            (items_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & 
                            (items_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & 
                            (items_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent') &
                            (items_df['Qty A'] > 0) & 
                            (items_df['Qty B'] > 0) & 
                            (items_df['Qty C'] == 0)
                        )
                        pending_df = items_df[pending_mask]
                        if not pending_df.empty:
                            st.error(f"🚨 {pending_df['Project Number'].nunique()} Sites mein items ka STN Pending hai!")
                            for col in qty_cols: pending_df[col] = pending_df[col].astype(int)
                            final_cols = [c for c in mera_sequence if c in pending_df.columns]
                            bache_hue_cols = [c for c in pending_df.columns if c not in final_cols]
                            pending_df = pending_df[final_cols + bache_hue_cols]
                            st.dataframe(pending_df, use_container_width=True, hide_index=True)
                            csv = convert_df_to_csv(pending_df)
                            st.download_button(label="📥 Download Excel File", data=csv, file_name="STN_Pending_Sites.csv", mime="text/csv")
                        else:
                            st.success("✅ Wah! Visiontech ka koi bhi STN Pending nahi hai. Sab DONE hai!")
        except Exception as e: st.error(f"Error: {e}")

    elif new_boq_btn:
        if boq_date_input is None: st.warning("⚠️ Kripya Date select karein!")
        else:
            iso_date = boq_date_input.strftime("%Y-%m-%d")
            try:
                res = supabase.table("BOQ Report").select("*").eq("Dispatch Date", iso_date).execute()
                if res.data:
                    df = pd.DataFrame(res.data)
                    st.success(f"✅ Record Mil Gaya! ({len(df)} Lines)")
                    st.dataframe(df, use_container_width=True)
            except Exception as e: st.error(f"Error: {e}")

    elif submit_search:
        query = supabase.table("BOQ Report").select("*")
        if project_query: query = query.ilike("Project Number", f"%{project_query}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query}%")
        # ... baaki filters ...
        res = query.execute()
        if res.data:
            st.dataframe(pd.DataFrame(res.data), use_container_width=True)

# =====================================================================
# 🟦 PAGE 2: PO REPORT
# =====================================================================
elif menu_selection == "🧾 PO Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Purchase Order (PO) Report</h3>", unsafe_allow_html=True)
    if "po_unlocked" not in st.session_state: st.session_state.po_unlocked = False

    if not st.session_state.po_unlocked:
        pwd = st.text_input("Enter Password:", type="password")
        if st.button("Unlock 🔓"):
            if pwd == "1234":
                st.session_state.po_unlocked = True
                st.rerun()
    else:
        with st.form("po_search"):
            p1, p2 = st.columns(2)
            with p1: po_no = st.text_input("PO Number")
            submit_po = st.form_submit_button("Search")
        if submit_po:
            res = supabase.table("PO Report").select("*").eq("PO Number", po_no).execute()
            if res.data: st.dataframe(pd.DataFrame(res.data))

# =====================================================================
# 🟨 PAGE 3: SITE DETAIL
# =====================================================================
elif menu_selection == "🏗️ Site Detail":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)
    if "site_unlocked" not in st.session_state: st.session_state.site_unlocked = False

    if not st.session_state.site_unlocked:
        pwd = st.text_input("Enter Password:", type="password", key="s_pwd")
        if st.button("Unlock 🔓", key="s_btn"):
            if pwd == "1234":
                st.session_state.site_unlocked = True
                st.rerun()
    else:
        site_id_in = st.text_input("📍 Site ID")
        if st.button("Search Site"):
            res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id_in}%").execute()
            if res.data: st.dataframe(pd.DataFrame(res.data))

# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA (NEW)
# =====================================================================
elif menu_selection == "📊 Indus Basic Data":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    with st.form("indus_form"):
        i1, i2, i3 = st.columns(3)
        with i1: s_id = st.text_input("📍 Site ID")
        with i2: s_nm = st.text_input("🏢 Site Name")
        with i3: s_cl = st.text_input("🗺️ Cluster")
        sub_i = st.form_submit_button("Search Indus")
    
    if sub_i:
        q = supabase.table("Indus Data").select("*")
        if s_id: q = q.ilike("Site ID", f"%{s_id}%")
        if s_nm: q = q.ilike("Site Name", f"%{s_nm}%")
        if s_cl: q = q.ilike("Area Name", f"%{s_cl}%")
        res = q.execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
