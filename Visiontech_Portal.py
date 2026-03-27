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
# Yahan apne naye project ki details daalein
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
# 🟩 TAB 1: BOQ REPORT (Exact Same as Your Original Code)
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
            st.write(""); st.empty() 

    st.divider()
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 2])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_pick = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_v5")
    
    gen_new_boq = False
    with r3:
        if st.button("📄 Generate New BOQ", use_container_width=True):
            if boq_date_pick: gen_new_boq = True
            else: st.warning("Select Date!")

    with r4:
        update_click = st.button("🔄 Update", use_container_width=True)

    if submit_search or stn_pending_btn or gen_new_boq or update_click:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        if update_click:
            try:
                sd_res = supabase.table("Site Data").select("*").execute()
                if sd_res.data:
                    p_list = list(set([str(x.get('Project Number', '')).strip() for x in sd_res.data if x.get('Project Number')]))
                    if p_list:
                        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                        query = query.in_("Project Number", p_list).eq("Dispatch Date", yesterday_str)
            except Exception as e:
                st.error(f"API Error: {e}")
        elif gen_new_boq:
            formatted_date_str = boq_date_pick.strftime('%d-%b-%Y')
            query = query.eq("BOQ Date", formatted_date_str)
        elif not stn_pending_btn:
            if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
            if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
            if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        response = query.execute()
        if response.data:
            df_res = pd.DataFrame(response.data)
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df_res.columns:
                    df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0).astype(int)

            if update_click: display_sequence = ['Project Number', 'Dispatch Date']
            else:
                display_sequence = mera_sequence
                if 'Item Code' in df_res.columns:
                    df_res['TempGroupKey'] = df_res.apply(lambda x: x['Sr. No.'] if str(x['Item Code']).strip() == '' else x['Item Code'], axis=1)
                    agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['TempGroupKey']}
                    df_res = df_res.groupby('TempGroupKey', as_index=False).agg(agg_dict)
            
            st.session_state['display_cols'] = display_sequence

            site_id_for_wa = df_res['Site ID'].iloc[0] if not df_res.empty and 'Site ID' in df_res.columns else None
            indus_wa_block = ""
            if site_id_for_wa:
                ind_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{site_id_for_wa}%").execute()
                if ind_res.data:
                    row_i = ind_res.data[0]
                    indus_wa_block = f"\n📍 *INDUS SITE DATA*\n*Area* :- {row_i.get('Area Name','-')}\n*Lat Long* :- {row_i.get('Lat','')} {row_i.get('Long','')}\n"
            st.session_state['wa_indus_data'] = indus_wa_block

            if 'Sr. No.' in df_res.columns:
                df_res['Sr. No.'] = pd.to_numeric(df_res['Sr. No.'], errors='coerce')
                df_res = df_res.sort_values(by='Sr. No.')

            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df_res.columns:
                    df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            df_res = df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            st.session_state['boq_df'] = df_res

    if 'boq_df' in st.session_state:
        df = st.session_state['boq_df']
        current_cols = st.session_state.get('display_cols', mera_sequence)
        final_cols = [c for c in current_cols if c in df.columns]
        st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

        st.markdown("### 📤 Export & Share")
        btn_col1, btn_col2 = st.columns([1, 4])
        p_val = df['Project Number'].iloc[0] if not df.empty and 'Project Number' in df.columns else "NA"
        s_id = df['Site ID'].iloc[0] if not df.empty and 'Site ID' in df.columns else "NA"
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='BOQ_Report')
        processed_data = output.getvalue()
        
        with btn_col1: st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", use_container_width=True)
        with btn_col2:
            wa_msg = f"📦 *BOQ REPORT: {p_val}*\n*Site ID* - {s_id}\n\n"
            wa_msg += st.session_state.get('wa_indus_data', "")
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">🚀 Share Full Report</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🧾 TAB 2: PO REPORT (Fixed with Left-Aligned Summary Table)
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
                    st.write("📋 **Full PO Details**")
                    st.dataframe(df_po, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    st.write("📌 **Unique Summary (Single Entry)**")
                    col_left, col_spacer = st.columns([0.4, 0.6]) # Left alignment
                    with col_left:
                        summary_df = df_po[['PO Number', 'Shipment Number', 'Receipt Number']].drop_duplicates()
                        st.dataframe(summary_df, use_container_width=True, hide_index=True)
                else: st.info("No PO data found.")
            except Exception as e: st.error(f"❌ API Error: {e}")

# =====================================================================
# TAB 3 TO 6 (Existing logic for Site, Indus, Data Entry, Finance)
# =====================================================================
# (Yahan aapka baaki code rahega...)
