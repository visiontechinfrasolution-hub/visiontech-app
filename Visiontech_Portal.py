import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
# Tab नावे तुमच्या सूचनेनुसार बदलली आहेत
tab1, tab2, tab3, tab4, tab_wcc, tab5, tab6 = st.tabs([
    "📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", 
    "📊 Indus Basic Data", "📡 WCC Tracker", "📁 Data Entry", "💰 Finance Entry"
])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (NO CHANGE IN LOGIC)
# =====================================================================
with tab1:
    st.markdown("""
        <style>
            div[data-testid="stDataTableBody"]::-webkit-scrollbar { width: 14px; height: 14px; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb { background: #888; border-radius: 10px; border: 2px solid #f1f1f1; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb:hover { background: #555; }
            .stDataFrame div::-webkit-scrollbar { width: 14px !important; height: 14px !important; }
            .stDataFrame div::-webkit-scrollbar-thumb { background-color: #007bff !important; border-radius: 10px !important; }
        </style>
    """, unsafe_allow_html=True)    
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    if 'cleared' not in st.session_state:
        st.session_state.cleared = False

    with st.form("search_form", clear_on_submit=st.session_state.cleared):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 1.2, 0.1])
        with c1: project_query = st.text_input("📁 Project No.", key="boq_p_v5")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v5")
        with c3: boq_query = st.text_input("📄 BOQ", key="boq_b_v5")
        with c4: dispatch_date_inp = st.date_input("📅 Date", value=None, key="boq_d_v5")
        with c5: transporter = st.selectbox("🚚 Transporter", ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"], key="boq_t_v5")
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"], key="boq_tsp_v5")
        
        with c7:
            st.write("") 
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_search = st.form_submit_button("🔍 Search")
                if submit_search: st.session_state.cleared = False
            with col_btn2:
                if st.form_submit_button("🗑️ Clear"):
                    st.session_state.cleared = True
                    st.session_state.pop('boq_df', None)
                    st.session_state.pop('wa_site_name', None)
                    st.rerun()

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
            except Exception as e: st.error(f"API Error: {e}")
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
                if col in df_res.columns: df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0).astype(int)
            
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
            current_site_name = "-"
            if site_id_for_wa:
                ind_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{site_id_for_wa}%").execute()
                if ind_res.data:
                    row_i = ind_res.data[0]
                    current_site_name = row_i.get('Site Name', '-')
                    indus_wa_block = f"\n📍 *INDUS SITE DATA*\n*Area* :- {row_i.get('Area Name','-')}\n*Tech Name* :- {row_i.get('Tech Name','-')}\n*Tech Number* :- {row_i.get('Tech Number','-')}\n*FSE* :- {row_i.get('FSE','-')}\n*FSE Number* :- {row_i.get('FSE Number','-')}\n*AOM Name* :- {row_i.get('AOM Name','-')}\n*AOM Number* :- {row_i.get('AOM Number','-')}\n*Lat Long* :- {row_i.get('Lat','')} {row_i.get('Long','')}\n"
            
            st.session_state['wa_indus_data'] = indus_wa_block
            st.session_state['wa_site_name'] = current_site_name

            if 'Sr. No.' in df_res.columns:
                df_res['Sr. No.'] = pd.to_numeric(df_res['Sr. No.'], errors='coerce')
                df_res = df_res.sort_values(by='Sr. No.')
            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df_res.columns: df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            df_res = df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            st.session_state['boq_df'] = df_res

    if 'boq_df' in st.session_state:
        df = st.session_state['boq_df']
        current_cols = st.session_state.get('display_cols', mera_sequence)
        final_cols = [c for c in current_cols if c in df.columns]
        st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

# =====================================================================
# 🧾 TAB 2: PO REPORT (NO CHANGE)
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
                res_po = q_po.execute()
                if res_po.data:
                    df_po = pd.DataFrame(res_po.data)
                    st.dataframe(df_po, use_container_width=True, hide_index=True)
            except Exception as e: st.error(f"❌ Error: {e}")

# =====================================================================
# 🏗️ TAB 3 & 4 (SITE DETAIL & INDUS DATA - NO CHANGE)
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)

# =====================================================================
# 📡 TAB 5: WCC TRACKER (NO CHANGE)
# =====================================================================
with tab_wcc:
    st.title("📡 WCC Status Tracker")
    # ... (Keep your existing WCC tracker logic here)

# =====================================================================
# 📁 TAB 6: DATA ENTRY (DOCUMENT CENTER INTEGRATED HERE)
# =====================================================================
with tab5:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Visiontech Document Center</h3>", unsafe_allow_html=True)
    st.divider()

    doc_sub1, doc_sub2, doc_sub3 = st.tabs(["📤 Manager Upload", "🔍 Team Search", "📊 Upload Status Tracker"])

    with doc_sub1:
        st.info("💡 एकापेक्षा जास्त फोटो असल्यास सर्व एकदाच निवडा.")
        with st.form("doc_upload_v2", clear_on_submit=True):
            c1, c2 = st.columns(2)
            u_proj = c1.text_input("📁 Project Number")
            u_indus = c2.text_input("📍 Indus ID")
            u_site = c1.text_input("🏢 Site Name")
            u_type = c2.selectbox("📄 Doc Type", ["Photo", "SRC", "DC", "STN", "REPORT", "OTHER"])
            u_files = st.file_uploader("फाईल्स निवडा", type=['pdf', 'jpg', 'png', 'jpeg'], accept_multiple_files=True)
            
            if st.form_submit_button("🚀 Upload All Files", use_container_width=True):
                if u_files and u_proj and u_indus:
                    try:
                        for i, f in enumerate(u_files):
                            fname = f"{u_proj}_{u_indus}_{u_site}_{u_type}_{i}.{f.name.split('.')[-1]}".replace("/", "-")
                            supabase.storage.from_("site_documents").upload(path=fname, file=f.getvalue(), file_options={"x-upsert": "true"})
                            
                            p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                            supabase.table("site_documents_master").upsert({
                                "project_number": u_proj, "indus_id": u_indus, "site_name": u_site,
                                "doc_type": u_type, "file_name": fname, "file_url": p_url
                            }, on_conflict="file_name").execute()
                        st.success("✅ यशस्वीरित्या अपलोड झाले!")
                    except Exception as e: st.error(f"❌ Error: {e}")

    with doc_sub2:
        q = st.text_input("🔍 सर्च (Project, Indus ID, Site)", key="doc_search")
        if q:
            res = supabase.table("site_documents_master").select("*").or_(f"project_number.ilike.%{q}%,indus_id.ilike.%{q}%,site_name.ilike.%{q}%").execute()
            if res.data:
                for row in res.data:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"📄 {row['file_name']}")
                    col2.info(row['doc_type'])
                    col3.markdown(f"[📥 View]({row['file_url']})")
                    st.divider()

    with doc_sub3:
        st.subheader("📊 Site-wise Status Tracker")
        res_t = supabase.table("site_documents_master").select("*").execute()
        if res_t.data:
            df_t = pd.DataFrame(res_t.data)
            summary = []
            for ind_id, gp in df_t.groupby('indus_id'):
                types = gp['doc_type'].str.upper().tolist()
                summary.append({
                    "Project ID": gp.iloc[0]['project_number'], "Indus ID": ind_id, "Site Name": gp.iloc[0]['site_name'],
                    "SRC": "✅" if "SRC" in types else "❌", "DC": "✅" if "DC" in types else "❌",
                    "STN": "✅" if "STN" in types else "❌", "Report": "✅" if "REPORT" in types else "❌",
                    "Photo": "✅" if "PHOTO" in types else "❌"
                })
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# =====================================================================
# 💰 TAB 7: FINANCE ENTRY (NEW PO ANALYZER INTEGRATED HERE)
# =====================================================================
with tab6:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>💰 Finance Entry (PO Analyzer)</h3>", unsafe_allow_html=True)
    st.divider()

    # PO Analyzer Styles
    st.markdown("""<style>[data-testid="stHeaderRowCell"] { text-align: center !important; background-color: #1E3A8A !important; color: white !important; font-weight: bold !important; }</style>""", unsafe_allow_html=True)

    po_file = st.file_uploader("Upload 'export.tsv'", type=['tsv', 'txt'], key="po_finance_upload")

    if po_file is not None:
        if st.button("🚀 Process & Sync 11 Columns to DB", use_container_width=True):
            try:
                content = po_file.getvalue().decode('ISO-8859-1').splitlines()
                h_idx = -1
                for i, line in enumerate(content):
                    if '"Line"' in line and '"Item Num"' in line:
                        h_idx = i; break
                
                if h_idx != -1:
                    po_file.seek(0)
                    df_h = pd.read_csv(po_file, sep='\t', nrows=1, encoding='ISO-8859-1')
                    po_no = str(df_h.columns[0]).replace('"', '').strip()
                    
                    po_file.seek(0)
                    df_raw = pd.read_csv(po_file, sep='\t', skiprows=h_idx, quoting=3, encoding='ISO-8859-1', engine='python')
                    df_raw.columns = [str(c).strip().replace('"', '') for c in df_raw.columns]

                    for c in ['Qty', 'Price', 'Amount']:
                        if c in df_raw.columns:
                            df_raw[c] = pd.to_numeric(df_raw[c].astype(str).str.replace('"', '').str.replace(',', '').strip(), errors='coerce').fillna(0)

                    df_clean = df_raw.dropna(subset=['Project Name', 'Amount'])
                    df_clean = df_clean[df_clean['Amount'] > 0]

                    # Database Sync (11 Columns)
                    items_payload = []
                    for _, r in df_clean.iterrows():
                        items_payload.append({
                            "po_number": po_no, "line_no": str(r.get('Line', '')), "item_number": str(r.get('Item Num', '')),
                            "description": str(r.get('Description', '')), "uom": str(r.get('UOM', '')), "qty": float(r.get('Qty', 0)),
                            "price": float(r.get('Price', 0)), "amount": float(r.get('Amount', 0)), "site_id": str(r.get('Site ID', '')),
                            "site_name": str(r.get('Site Name', '')), "project_name": str(r.get('Project Name', ''))
                        })
                    supabase.table("po_line_items").insert(items_payload).execute()
                    
                    st.success(f"✅ PO {po_no} Synced successfully!")
            except Exception as e: st.error(f"❌ Error: {e}")

    # Display Records
    s_term = st.text_input("🔍 Search Database (PO, Project, Site)", key="finance_search")
    f_tab1, f_tab2 = st.tabs(["📊 Summary", "📋 All Details"])
    
    with f_tab1:
        res_s = supabase.table("po_summaries").select("*").order("created_at", desc=True).execute()
        if res_s.data:
            st.dataframe(pd.DataFrame(res_s.data), use_container_width=True, hide_index=True)
    with f_tab2:
        res_d = supabase.table("po_line_items").select("*").order("created_at", desc=True).limit(500).execute()
        if res_d.data:
            st.dataframe(pd.DataFrame(res_d.data), use_container_width=True, hide_index=True)
