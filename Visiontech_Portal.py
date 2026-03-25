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
    with r3:
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
            df = pd.DataFrame(response.data)
            
            if 'Item Code' in df.columns:
                df['Item Code'] = df['Item Code'].fillna('').astype(str).str.strip()
            
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            if 'Item Code' in df.columns:
                df['TempGroupKey'] = df.apply(lambda x: x['Sr. No.'] if x['Item Code'] == '' else x['Item Code'], axis=1)
                agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col not in ['TempGroupKey', 'Item Code']}
                df = df.groupby('TempGroupKey', as_index=False).agg(agg_dict)
            
            if 'Sr. No.' in df.columns:
                df['Sr. No.'] = pd.to_numeric(df['Sr. No.'], errors='coerce')
                df = df.sort_values(by='Sr. No.')

            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            final_cols = [c for c in mera_sequence if c in df.columns]
            
            # Table Display
            st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

            # --- NAYI SHARE LOGIC: WHATSAPP (SINGLE MSG) + EXCEL ---
            st.divider()
            s_col1, s_col2 = st.columns([1, 4])
            
            # Fetch common data for header
            p_val = df['Project Number'].iloc[0] if not df.empty else "-"
            s_id = df['Site ID'].iloc[0] if not df.empty else "-"
            # Logic for Site Name (if available in your data)
            s_nm = df.get('Site Name', pd.Series(['-'])).iloc[0] 

            # 1. Download Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df[final_cols].to_excel(writer, index=False, sheet_name='BOQ')
            processed_data = output.getvalue()
            
            with s_col1:
                st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            with s_col2:
                # 2. Building Single WhatsApp Message
                wa_msg = f"📦 *BOQ REPORT: {p_val}*\n*Project Number* - {p_val}\n*Site ID* - {s_id}\n\n"
                
                for i, row in df.iterrows():
                    wa_msg += (
                        f"*{i+1}.*\n"
                        f"*BOQ Number* - {row.get('BOQ', '-')}\n"
                        f"*Item Code* - {row.get('Item Code', '-')}\n"
                        f"*Item Description* - {row.get('Item Description', '-')}\n"
                        f"*BOQ Qty* - {row.get('Qty A', '0')}\n"
                        f"*Dispatched Qty* - {row.get('Qty B', '0')}\n"
                        f"*STN Qty* - {row.get('Qty C', '0')}\n"
                        f"*Parent* - {row.get('Parent/Child', '-')}\n"
                        f"*Line Status* - {row.get('Line Status', '-')}\n"
                        f"*Dispatched Date* - {row.get('Dispatch Date', '-')}\n"
                        f"*Transporter Name* - {row.get('Transporter', '-')}\n"
                        f"*TSP Name* - {row.get('TSP Partner Name', '-')}\n"
                        f"*Source Of Fulfilment* - {row.get('Source Of Fulfilment', '-')}\n"
                        f"--------------------\n"
                    )
                
                st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">🚀 Share Full Table on WhatsApp</button></a>', unsafe_allow_html=True)

# =====================================================================
# 🟦 TAB 2, 3, 4 (No Changes)
# =====================================================================
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
