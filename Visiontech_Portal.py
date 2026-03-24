# =====================================================================
# 🟩 TAB 1: BOQ REPORT (FIXED WITH ALL YOUR REQUIREMENTS)
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
    
    # --- GENERATE NEW BOQ BOX / BUTTON (RESTORED) ---
    with r3:
        if st.button("📄 Generate New BOQ", use_container_width=True):
            if boq_date_pick:
                f_date = boq_date_pick.strftime('%d-%b-%Y')
                msg = f"Request for New BOQ Generation for Date: {f_date}"
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(msg)}">Click to Open WhatsApp</a>', unsafe_allow_html=True)
            else:
                st.warning("Please select a date first!")

    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        response = query.execute()
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 1. Qty Format & Merge (Removing .0)
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            if 'Item Code' in df.columns:
                agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col != 'Item Code'}
                df = df.groupby('Item Code', as_index=False).agg(agg_dict)

            # 2. Date Format Fix (24-Mar-2026)
            date_cols = ['Dispatch Date', 'BOQ Date']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')

            # 3. Clean and Display
            df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            final_cols = [c for c in mera_sequence if c in df.columns]
            df = df[final_cols + [c for c in df.columns if c not in final_cols]]
            
            st.dataframe(df, use_container_width=True, hide_index=True)
