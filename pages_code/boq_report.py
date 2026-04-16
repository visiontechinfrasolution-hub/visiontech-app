import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>🔍 BOQ Report</h3>", unsafe_allow_html=True)
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    if 'cleared' not in st.session_state: st.session_state.cleared = False

    with st.form("search_form", clear_on_submit=st.session_state.cleared):
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 1.2])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_v5")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v5")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_v5")
        with c4: dispatch_date_inp = st.date_input("📅 Date", value=None, key="boq_d_v5")
        with c5: transporter = st.selectbox("🚚 Transp.", ["", "visiontech", "Safexpress", "Delhivery", "VRL", "TCI", "Gati"])
        with c6: tsp_partner = st.selectbox("🤝 Partner", ["", "visiontech", "Ericsson", "Nokia"])
        submit_search = c7.form_submit_button("🔍 Search")

    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(5000)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        res = query.execute()
        if res.data: st.session_state['boq_df'] = pd.DataFrame(res.data)

    if 'boq_df' in st.session_state:
        st.dataframe(st.session_state['boq_df'], use_container_width=True, hide_index=True)
