import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# Naya Project Connection (Alag rakhne ke liye)
NEW_URL = "https://your-new-project-id.supabase.co" 
NEW_KEY = "your-new-anon-key-here"
supabase_new = create_client(NEW_URL, NEW_KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", 
    "📊 Indus Basic Data", "📁 Data Entry", "💰 Finance Entry"
])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (Existing Logic - Unchanged)
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
        with c7: submit_search = st.form_submit_button("🔍 Search")
    
    # ... (Rest of Tab 1 Logic remains exactly same as your provided snippet)
    # (Existing BOQ logic goes here...)

# =====================================================================
# 🧾 TAB 2: PO REPORT (Fixed with Unique Summary Table)
# =====================================================================
with tab2:
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report Search</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        if st.text_input("Password PO:", type="password", key="p_lock_v5") == "1234":
            st.session_state.po_unlocked = True
            st.rerun()
    else:
        with st.form("po_form_v5"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: s_po = st.text_input("📄 PO Number")
            with c2: s_sh = st.text_input("🚚 Shipment Number")
            with c3: s_re = st.text_input("🧾 Receipt Number")
            with c4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        
        if sub_po:
            try:
                q_po = supabase.table("PO Report").select("*")
                if s_po.strip():
                    if s_po.strip().isdigit(): q_po = q_po.eq("PO Number", int(s_po.strip()))
                    else: q_po = q_po.ilike("PO Number", f"%{s_po.strip()}%")
                if s_sh.strip():
                    if s_sh.strip().isdigit(): q_po = q_po.eq("Shipment Number", int(s_sh.strip()))
                    else: q_po = q_po.ilike("Shipment Number", f"%{s_sh.strip()}%")
                if s_re.strip(): q_po = q_po.ilike("Receipt Number", f"%{s_re.strip()}%")
                
                res_po = q_po.execute()
                if res_po.data:
                    df_po = pd.DataFrame(res_po.data)
                    # 1. Main Table (Duplicates allowed)
                    st.write("📋 **Full Details**")
                    st.dataframe(df_po, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # 2. Unique Summary Table (Left Side, No Duplicates)
                    st.write("📌 **Unique Summary (Single Entry)**")
                    col_left, col_spacer = st.columns([0.4, 0.6]) # Left aligned
                    with col_left:
                        # Sirf zaroori columns nikaal kar duplicate hata diye
                        summary_df = df_po[['PO Number', 'Shipment Number', 'Receipt Number']].drop_duplicates()
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No PO data found.")
            except Exception as e:
                st.error(f"❌ API Error: {e}")

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    with st.form("sd_form_v5"):
        s1, s2 = st.columns(2)
        with s1: p_id_sd = st.text_input("📁 Project Number Search")
        with s2: site_id_sd = st.text_input("📍 Site ID Search")
        if st.form_submit_button("🔍 Search Detail"):
            res_sd = supabase.table("Site Data").select("*").ilike("SITE ID", f"%{site_id_sd}%").execute()
            if res_sd.data:
                for row in res_sd.data:
                    st.markdown(f"**Project**: {row.get('Project Number','-')} | **SITE ID**: {row.get('SITE ID','-')} | **Site Name**: {row.get('Site Name','-')}")

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_v5"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID")
        with i2: in_nm = st.text_input("🏢 Site Name")
        with i3: st.write(""); sub_ind = st.form_submit_button("🔍 Search Indus")
    if sub_ind:
        res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
        if res_ind.data: st.dataframe(pd.DataFrame(res_ind.data), use_container_width=True, hide_index=True)

# =====================================================================
# 📁 TAB 5: DATA ENTRY (New Project)
# =====================================================================
with tab5:
    st.subheader("📁 Site Data Entry Form")
    with st.form("site_entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            p_no_in = st.text_input("Project Number")
            s_id_in = st.text_input("Site ID")
        with c2:
            d_dt_in = st.date_input("Dispatch Date", value=datetime.now())
            qty_in = st.number_input("Qty A", min_value=0, step=1)
        if st.form_submit_button("🚀 Save Data"):
            if p_no_in and s_id_in:
                try:
                    supabase_new.table("Site_Data_Entry").insert({
                        "Project Number": p_no_in, "Site ID": s_id_in, 
                        "Dispatch Date": d_dt_in.strftime('%d-%b-%Y'), "Qty A": qty_in
                    }).execute()
                    st.success("✅ Saved to New Project!")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# =====================================================================
# 💰 TAB 6: FINANCE ENTRY (New Project)
# =====================================================================
with tab6:
    st.subheader("💰 Finance & Billing Entry")
    with st.form("fin_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1:
            fin_p_no = st.text_input("Project Number (Finance)")
            t_bill = st.number_input("Team Billing", min_value=0)
        with f2:
            t_paid = st.number_input("Team Paid Amt", min_value=0)
            fin_dt = st.date_input("Entry Date", value=datetime.now())
        if st.form_submit_button("💵 Record Finance"):
            if fin_p_no:
                v_bal = t_bill - t_paid
                try:
                    supabase_new.table("Finance_Entry").insert({
                        "Project Number": fin_p_no, "Team Billing": t_bill,
                        "Team Paid Amt": t_paid, "VIS Balance": v_bal,
                        "Date": fin_dt.strftime('%d-%b-%Y')
                    }).execute()
                    st.success(f"✅ Saved! Auto-Balance: ₹{v_bal}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
