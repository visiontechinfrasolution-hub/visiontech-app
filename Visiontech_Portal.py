import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import urllib.parse
import io

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
# 🟩 TAB 1: BOQ REPORT
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
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_pick = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_v5")
    
    gen_new_boq = False
    if st.button("📄 Generate New BOQ", use_container_width=True):
        if boq_date_pick:
            gen_new_boq = True
        else:
            st.warning("Select Date!")

    if submit_search or stn_pending_btn or gen_new_boq:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        if gen_new_boq:
            query = query.eq("BOQ Date", boq_date_pick.strftime('%Y-%m-%d'))
        elif not stn_pending_btn:
            if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
            if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
            if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        response = query.execute()
        if response.data:
            df_res = pd.DataFrame(response.data)
            
            # --- FETCH INDUS DATA ---
            site_id_for_wa = df_res['Site ID'].iloc[0] if not df_res.empty else None
            indus_wa_block = ""
            site_name_from_indus = "-"
            if site_id_for_wa:
                ind_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{site_id_for_wa}%").execute()
                if ind_res.data:
                    row_i = ind_res.data[0]
                    site_name_from_indus = row_i.get('Site Name', '-')
                    lat_v = row_i.get('Lat', '-')
                    long_v = row_i.get('Long', '-')
                    indus_wa_block = (
                        f"\n📍 *INDUS SITE DATA*\n"
                        f"*Area Name* :- {row_i.get('Area Name','-')}\n"
                        f"*Tech Name* :- {row_i.get('Tech Name','-')}\n"
                        f"*Tech Number* :- {row_i.get('Tech Number','-')}\n"
                        f"*FSE* :- {row_i.get('FSE','-')}\n"
                        f"*FSE Number* :- {row_i.get('FSE Number','-')}\n"
                        f"*AOM Name* :- {row_i.get('AOM Name','-')}\n"
                        f"*AOM Number* :- {row_i.get('AOM Number','-')}\n"
                        f"*Lat Long* :- {lat_v} {long_v}\n"
                    )
            st.session_state['wa_indus_data'] = indus_wa_block
            st.session_state['wa_site_name'] = site_name_from_indus

            if 'Item Code' in df_res.columns:
                df_res['Item Code'] = df_res['Item Code'].fillna('').astype(str).str.strip()
            
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df_res.columns:
                    df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0)
            
            # --- NEW RULE: No Grouping for "Generate New BOQ" ---
            if not gen_new_boq:
                if 'Item Code' in df_res.columns:
                    df_res['TempGroupKey'] = df_res.apply(lambda x: x['Sr. No.'] if x['Item Code'] == '' else x['Item Code'], axis=1)
                    agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['TempGroupKey']}
                    df_res = df_res.groupby('TempGroupKey', as_index=False).agg(agg_dict)
            # --------------------------------------------------
            
            if 'Sr. No.' in df_res.columns:
                df_res['Sr. No.'] = pd.to_numeric(df_res['Sr. No.'], errors='coerce')
                df_res = df_res.sort_values(by='Sr. No.')
            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df_res.columns:
                    df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
            for col in qty_cols:
                if col in df_res.columns:
                    df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0).astype(int)
            df_res = df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            
            st.session_state['boq_df'] = df_res

    if 'boq_df' in st.session_state:
        df = st.session_state['boq_df']
        final_cols = [c for c in mera_sequence if c in df.columns]
        st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

        st.markdown("### 📤 Export & Share")
        btn_col1, btn_col2 = st.columns([1, 4])
        
        p_val = df['Project Number'].iloc[0] if not df.empty else "NA"
        s_id = df['Site ID'].iloc[0] if not df.empty else "NA"
        s_nm = st.session_state.get('wa_site_name', '-')

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df[final_cols].to_excel(writer, index=False, sheet_name='BOQ_Report')
        processed_data = output.getvalue()
        
        with btn_col1:
            st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        with btn_col2:
            wa_msg = f"📦 *BOQ REPORT: {p_val}*\n"
            wa_msg += f"*Project Number* - {p_val}\n"
            wa_msg += f"*Site ID* - {s_id}\n"
            wa_msg += f"*Site Name* - {s_nm}\n\n"
            
            df_whatsapp = df[df['Parent/Child'].astype(str).str.lower() == 'parent']
            
            count = 1
            for i, row in df_whatsapp.iterrows():
                wa_msg += (
                    f"*{count}.*\n"
                    f"*Transaction Type* - {row.get('Transaction Type', '-')}\n"
                    f"*BOQ Number* - {row.get('BOQ', '-')}\n"
                    f"*Item Code* - {row.get('Item Code', '-')}\n"
                    f"*Item Description* - {row.get('Item Description', '-')}\n"
                    f"*BOQ Qty* - {row.get('Qty A', '0')}\n"
                    f"*Dispatched Qty* - {row.get('Qty B', '0')}\n"
                    f"*STN Qty* - {row.get('Qty C', '0')}\n"
                    f"*Parent* - {row.get('Parent/Child', '-')}\n"
                    f"*Dispatched Date* - {row.get('Dispatch Date', '-')}\n"
                    f"*Transporter Name* - {row.get('Transporter', '-')}\n"
                    f"*TSP Name* - {row.get('TSP Partner Name', '-')}\n"
                    f"--------------------\n"
                )
                count += 1
            
            wa_msg += st.session_state.get('wa_indus_data', "")
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">🚀 Share Full Report with Site Name</button></a>', unsafe_allow_html=True)

# (Tab 2, 3, 4 remain unchanged)
with tab2:
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        if st.text_input("Password PO:", type="password", key="p_lock") == "1234":
            st.session_state.po_unlocked = True; st.rerun()
    else:
        with st.form("po_form"):
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
    if not st.session_state.get('site_unlocked', False):
        if st.text_input("Password Site:", type="password", key="s_lock") == "1234":
            st.session_state.site_unlocked = True; st.rerun()
    else:
        with st.form("sd_form"):
            s1, s2 = st.columns(2)
            with s1: p_id = st.text_input("📁 Project ID")
            with s2: site_id = st.text_input("📍 Site ID")
            if st.form_submit_button("🔍 Search"):
                res = supabase.table("Site Detail").select("*").ilike("SITE ID", f"%{site_id}%").execute()
                if res.data:
                    for row in res.data:
                        txt = f"*Project Number* :- {row.get('Project Number','-')}\n*SITE ID* :- {row.get('SITE ID','-')}\n*Site Name* :- {row.get('Site Name','-')}\n*District* :- {row.get('District','-')}\n*Lat-Long* :- {row.get('Latitude','')} , {row.get('Longitude','')}"
                        st.markdown("---")
                        st.text(txt)
                        st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(txt)}"><button style="background-color: #25D366; color: white; border: none; padding: 8px 15px; border-radius: 5px;">🚀 WhatsApp</button></a>', unsafe_allow_html=True)

with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID")
        with i2: in_nm = st.text_input("🏢 Site Name")
        with i3: in_cl = st.text_input("🗺️ Cluster")
        if st.form_submit_button("🔍 Search Indus"):
            q = supabase.table("Indus Data").select("*")
            if in_id: q = q.ilike("Site ID", f"%{in_id}%")
            res = q.execute()
            if res.data:
                for row in res.data:
                    ind_txt = f"*Site ID* :- {row.get('Site ID','-')}\n*Site Name* :- {row.get('Site Name','-')}\n*District* :- {row.get('District','-')}\n*Area Name* :- {row.get('Area Name','-')}\n*Tech Name* :- {row.get('Tech Name','-')}\n*Tech Number* :- {row.get('Tech Number','-')}\n*FSE* :- {row.get('FSE','-')}\n*FSE Number* :- {row.get('FSE Number','-')}\n*AOM Name* :- {row.get('AOM Name','-')}\n*AOM Number* :- {row.get('AOM Number','-')}\n*Lat-Long* :- {row.get('Lat','')} , {row.get('Long','')}"
                    st.markdown("---")
                    st.text(ind_txt)
                    st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(ind_txt)}"><button style="background-color: #25D366; color: white; border: none; padding: 8px 15px; border-radius: 5px;">🚀 WhatsApp</button></a>', unsafe_allow_html=True)
