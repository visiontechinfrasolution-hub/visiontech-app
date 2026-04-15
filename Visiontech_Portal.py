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

# --- 3. TABS (Added "📝 Audit Portal") ---
tab1, tab2, tab3, tab4, tab_wcc, tab5, tab6, tab_audit = st.tabs([
    "📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", 
    "📊 Indus Basic Data", "📡 WCC Tracker", "📁 Data Entry", "💰 Finance Entry", "📝 Audit Portal"
])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (RESTORED ORIGINAL SEARCH LOGIC)
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
        with c8: st.empty()

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

    # --- RESTORED API SEARCH LOGIC ---
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

            if not update_click:
                if 'Item Code' in df_res.columns:
                    df_res['TempGroupKey'] = df_res.apply(lambda x: x['Sr. No.'] if str(x['Item Code']).strip() == '' else x['Item Code'], axis=1)
                    agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['TempGroupKey']}
                    df_res = df_res.groupby('TempGroupKey', as_index=False).agg(agg_dict)
            
            # Formatting Dates for Display
            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df_res.columns: df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            df_res = df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            st.session_state['boq_df'] = df_res

    if 'boq_df' in st.session_state:
        df = st.session_state['boq_df']
        final_cols = [c for c in mera_sequence if c in df.columns]
        st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

# =====================================================================
# 🧾 TAB 2: PO REPORT
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
            res_po = supabase.table("PO Report").select("*").ilike("PO Number", f"%{s_po}%").execute()
            if res_po.data: st.dataframe(pd.DataFrame(res_po.data), use_container_width=True)

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL
# =====================================================================
with tab3:
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    with st.form("sd_form_v5"):
        site_id_sd = st.text_input("📍 Site ID Search")
        if st.form_submit_button("🔍 Search Detail"):
            res_sd = supabase.table("Site Data").select("*").ilike("SITE ID", f"%{site_id_sd}%").execute()
            if res_sd.data: st.write(res_sd.data)

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_v5"):
        in_id = st.text_input("📍 Site ID Search")
        if st.form_submit_button("🔍 Search Indus"):
            res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
            if res_ind.data: st.dataframe(pd.DataFrame(res_ind.data))

# =====================================================================
# 📡 TAB 5: WCC TRACKER (SIMPLE FETCH & COMPACT FORMAT)
# =====================================================================
with tab_wcc:
    st.markdown("""
        <style>
            .site-badge { 
                background-color: #E0F2FE; color: #0369A1; padding: 2px 8px; 
                border-radius: 12px; font-weight: 600; font-size: 11px; border: 1px solid #BAE6FD; 
            }
            .wa-btn { 
                background-color: #25D366; color: white !important; padding: 4px 8px; 
                border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px;
            }
            [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
        </style>
    """, unsafe_allow_html=True)

    def fetch_wcc_data_simple():
        try: 
            # Simple select bina kisi order ke taaki agar column missing ho toh crash na ho
            res = supabase.table("WCC Status").select("*").execute()
            return res.data
        except Exception as e:
            st.error(f"Fetch Error: {e}")
            return []

    def update_wcc_record(payload):
        try: return supabase.table("WCC Status").upsert(payload).execute()
        except: return None

    st.title("📡 WCC Status Tracker")
    
    if "wcc_role" not in st.session_state: st.session_state.wcc_role = None
    
    if not st.session_state.wcc_role:
        pwd_input = st.text_input("Enter Password:", type="password", key="wcc_login_pwd_v2")
        if st.button("🔓 Unlock Tracker"):
            if pwd_input == "Vision@321": st.session_state.wcc_role = "requester"
            elif pwd_input == "Account@321": st.session_state.wcc_role = "accountant"
            else: st.error("❌ Wrong Password!")
            st.rerun()
    else:
        role = st.session_state.wcc_role
        
        @st.dialog("📝 WCC Details Form", width="large")
        def wcc_edit_modal(row_data=None):
            is_edit = row_data is not None
            with st.form("wcc_form_v25"):
                if role == "requester":
                    c1, c2 = st.columns(2)
                    v_proj = c1.text_input("Project", value=str(row_data.get("Project", "")) if is_edit else "")
                    v_pid = c2.text_input("Project ID *", value=str(row_data.get("Project ID", "")) if is_edit else "", disabled=is_edit)
                    c3, c4 = st.columns(2)
                    v_sid = c3.text_input("Site ID", value=str(row_data.get("Site ID", "")) if is_edit else "")
                    v_snm = c4.text_input("Site Name", value=str(row_data.get("Site Name", "")) if is_edit else "")
                    c5, c6 = st.columns(2)
                    v_po = c5.text_input("PO Number", value=str(row_data.get("PO Number", "")) if is_edit else "")
                    v_dt = st.date_input("Request Date", value=datetime.now().date())
                    v_sts = st.selectbox("WCC Status", ["Creation Pending", "Pending for Approval", "Proceed", "Rejected", "Cancel"], 
                                         index=0 if not is_edit else ["Creation Pending", "Pending for Approval", "Proceed", "Rejected", "Cancel"].index(row_data.get("WCC Status", "Creation Pending")))
                    v_wno = row_data.get("WCC Number") if is_edit else None 
                else:
                    v_pid = row_data.get('Project ID')
                    v_wno = st.text_input("Enter WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    def clean_id(v): return ''.join(filter(str.isdigit, str(v))) if v else None
                    payload = {"Project ID": v_pid, "WCC Number": clean_id(v_wno)}
                    if role == "requester": 
                        payload.update({"Project": v_proj, "Site ID": v_sid, "Site Name": v_snm, "PO Number": clean_id(v_po), "Reqeust Date": str(v_dt), "WCC Status": v_sts})
                    if update_wcc_record(payload): st.rerun()

        data_list = fetch_wcc_data_simple()
        df_wcc = pd.DataFrame(data_list) if data_list else pd.DataFrame()
        
        if role == "requester":
            if st.button("➕ Add New Site Request", type="primary"): wcc_edit_modal()
        
        st.divider()

        if not df_wcc.empty:
            # --- TABLE HEADER ---
            h_cols = st.columns([1, 0.5, 1.2, 1.5, 1, 1.2, 1, 1.2])
            cols_names = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "Status"]
            for col, name in zip(h_cols, cols_names):
                col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:13px; text-align:center;'>{name}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0px; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

           # --- TABLE ROWS (DATE FORMAT & BLANK LOGIC FIXED) ---
            for i, row in df_wcc.iterrows():
                r_cols = st.columns([1, 0.5, 1.2, 1.5, 1, 1.2, 1, 1.2])
                
                # Date Formatting: 15-Apr-2026
                raw_date = row.get('Reqeust Date', '')
                try:
                    formatted_date = pd.to_datetime(raw_date).strftime('%d-%b-%Y') if raw_date and str(raw_date).lower() != 'none' else ""
                except:
                    formatted_date = str(raw_date) if str(raw_date).lower() != 'none' else ""

                # Function to remove 'None' from display
                def clean_none(val):
                    return str(val) if val and str(val).lower() != 'none' else ""

                with r_cols[0]:
                    b1, b2 = st.columns(2)
                    if b1.button("✏️", key=f"edit_{row['Project ID']}_{i}"): wcc_edit_modal(row)
                    if role == 'requester':
                        msg = (
                            f"Hello Prkash Ji,\nRaise WCC urgently...\n\n"
                            f"*Project* :- {clean_none(row.get('Project'))}\n"
                            f"*Project ID* :- {clean_none(row.get('Project ID'))}\n"
                            f"*Site ID* :- {clean_none(row.get('Site ID'))}\n"
                            f"*Site Name* :- {clean_none(row.get('Site Name'))}\n"
                            f"*PO Number* :- {clean_none(row.get('PO Number'))}\n"
                            f"*Reqeust Date* :- {formatted_date}\n"
                            f"*WCC Number* :- {clean_none(row.get('WCC Number'))}\n"
                            f"*WCC Status* :- {clean_none(row.get('WCC Status'))}\n\n"
                            f"Thanks,\nMayur Patil\n7350533473"
                        )
                        wa_url = f"whatsapp://send?text={urllib.parse.quote(msg)}"
                        b2.markdown(f'<a href="{wa_url}" class="wa-btn">💬</a>', unsafe_allow_html=True)
                
                r_cols[1].markdown(f"<p style='font-size:12px; text-align:center;'>{i+1}</p>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('Project'))}</p>", unsafe_allow_html=True)
                r_cols[3].markdown(f"<p style='font-size:12px; text-align:center; font-weight:bold;'>{clean_none(row.get('Project ID'))}</p>", unsafe_allow_html=True)
                r_cols[4].markdown(f"<div style='text-align:center;'><span class='site-badge'>{clean_none(row.get('Site ID'))}</span></div>", unsafe_allow_html=True)
                r_cols[5].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('Site Name'))}</p>", unsafe_allow_html=True)
                r_cols[6].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('PO Number'))}</p>", unsafe_allow_html=True)
                r_cols[7].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('WCC Status'))}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0px; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
# =====================================================================
# 📁 TAB 6: DATA ENTRY (DOCUMENT CENTER)
# =====================================================================
with tab5:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
    doc_sub1, doc_sub2, doc_sub3 = st.tabs(["📤 Manager Upload", "🔍 Team Search", "📊 Tracker"])
    with doc_sub1:
        with st.form("doc_upload_final_v1", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            u_proj, u_indus = col_u1.text_input("📁 Project Number"), col_u2.text_input("📍 Indus ID")
            u_site, u_type = col_u1.text_input("🏢 Site Name"), col_u2.selectbox("📄 Doc Type", ["Photo", "SRC", "DC", "STN", "REPORT", "OTHER"])
            u_files = st.file_uploader("Select Files", accept_multiple_files=True)
            if st.form_submit_button("🚀 Upload All Files"):
                if u_files and u_proj:
                    for i, f in enumerate(u_files):
                        clean_p = u_proj.replace("/", "-").strip()
                        fname = f"{clean_p}_{u_indus}_{u_type}_{i}.{f.name.split('.')[-1]}"
                        supabase.storage.from_("site_documents").upload(path=fname, file=f.getvalue(), file_options={"x-upsert": "true"})
                        p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                        supabase.table("site_documents_master").upsert({"project_number": u_proj, "indus_id": u_indus, "site_name": u_site, "doc_type": u_type, "file_name": fname, "file_url": p_url}, on_conflict="file_name").execute()
                    st.success("✅ Files Uploaded!")

    with doc_sub2:
        q_s = st.text_input("🔍 Search Documents (Project, Indus, Site)")
        if q_s:
            res_db = supabase.table("site_documents_master").select("*").or_(f"project_number.ilike.%{q_s}%,indus_id.ilike.%{q_s}%,site_name.ilike.%{q_s}%").execute()
            if res_db.data:
                for row in res_db.data:
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(row['file_name']); c2.info(row['doc_type']); c3.markdown(f'[📥 View]({row["file_url"]})')
                    st.divider()

    with doc_sub3:
        res_t = supabase.table("site_documents_master").select("*").execute()
        if res_t.data:
            df_t = pd.DataFrame(res_t.data)
            site_groups = df_t.groupby('indus_id')
            summary = []
            for ind_id, gp in site_groups:
                types = gp['doc_type'].str.upper().tolist()
                summary.append({"Project ID": gp.iloc[0]['project_number'], "Indus ID": ind_id, "Site Name": gp.iloc[0]['site_name'], "SRC": "✅" if "SRC" in types else "❌", "DC": "✅" if "DC" in types else "❌", "STN": "✅" if "STN" in types else "❌", "Report": "✅" if "REPORT" in types else "❌", "Photo": "✅" if "PHOTO" in types else "❌"})
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

# =====================================================================
# 💰 TAB 7: FINANCE ENTRY (FIXED PO ANALYZER)
# =====================================================================
with tab6:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>💰 Finance Entry (PO Analyzer)</h3>", unsafe_allow_html=True)
    def clean_num_fixed(val):
        try:
            if val is None or str(val).strip().lower() in ['nan', 'none', '']: return 0.0
            n = str(val).replace('"', '').replace(',', '').strip()
            num = pd.to_numeric(n, errors='coerce')
            return float(num) if pd.notnull(num) else 0.0
        except: return 0.0

    with st.form("fin_upload_fixed", clear_on_submit=True):
        c1, c2 = st.columns([1, 2])
        u_po = c1.text_input("📄 Enter PO Number")
        p_file = c2.file_uploader("Upload 'export.tsv'", type=['tsv', 'txt'])
        if st.form_submit_button("🚀 Process & Overwrite Data", use_container_width=True):
            if u_po and p_file:
                try:
                    content = p_file.getvalue().decode('ISO-8859-1').splitlines()
                    h_idx = next((i for i, line in enumerate(content) if "Project Name" in line), -1)
                    if h_idx != -1:
                        p_file.seek(0)
                        df_r = pd.read_csv(p_file, sep='\t', skiprows=h_idx, quoting=3, encoding='ISO-8859-1', engine='python')
                        df_r.columns = [str(c).replace('"', '').strip() for c in df_r.columns]
                        for col in df_r.columns: df_r[col] = df_r[col].astype(str).str.replace('"', '').str.strip()
                        df_r['qty_tmp'] = df_r['Qty'].apply(clean_num_fixed)
                        df_cln = df_r[df_r['qty_tmp'] > 0].copy()
                        if not df_cln.empty:
                            supabase.table("po_line_items").delete().eq("po_number", str(u_po)).execute()
                            supabase.table("po_summaries").delete().eq("po_number", str(u_po)).execute()
                            items = []
                            for _, r in df_cln.iterrows():
                                items.append({"po_number": str(u_po), "line_no": str(r.get('Line', '')), "item_number": str(r.get('Item Num', '')), "description": str(r.get('Description', '')), "uom": str(r.get('UOM', '')), "qty": clean_num_fixed(r.get('Qty')), "price": clean_num_fixed(r.get('Price')), "amount": clean_num_fixed(r.get('Amount')), "site_id": str(r.get('Site ID', '')), "site_name": str(r.get('Site Name', '')), "project_name": str(r.get('Project Name', ''))})
                            supabase.table("po_line_items").insert(items).execute()
                            df_cln['amt_tmp'] = df_cln['Amount'].apply(clean_num_fixed)
                            sums = df_cln.groupby('Project Name')['amt_tmp'].sum().reset_index()
                            summary_list = [{"po_number": str(u_po), "project_name": str(sr['Project Name']), "total_amount": float(sr['amt_tmp'])} for _, sr in sums.iterrows()]
                            supabase.table("po_summaries").insert(summary_list).execute()
                            st.success(f"PO {u_po} Synced!")
                            st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    g_search = st.text_input("🔍 Search Database...", key="fin_g_search")
    f_t1, f_t2 = st.tabs(["📊 Summaries", "📋 Detailed Items"])
    with f_t1:
        res_s = supabase.table("po_summaries").select("*").order("created_at", desc=True).execute()
        if res_s.data:
            df_s = pd.DataFrame(res_s.data)
            if g_search: df_s = df_s[df_s.astype(str).apply(lambda x: x.str.contains(g_search, case=False)).any(axis=1)]
            st.dataframe(df_s[['po_number', 'project_name', 'total_amount']], use_container_width=True, hide_index=True)
    with f_t2:
        res_d = supabase.table("po_line_items").select("*").order("created_at", desc=True).limit(1000).execute()
        if res_d.data:
            df_d = pd.DataFrame(res_d.data)
            if g_search: df_d = df_d[df_d.astype(str).apply(lambda x: x.str.contains(g_search, case=False)).any(axis=1)]
            st.dataframe(df_d[['po_number', 'line_no', 'item_number', 'qty', 'amount', 'project_name', 'site_id']], use_container_width=True, hide_index=True)

# =====================================================================
# 📝 TAB 9: VIS PORTAL MASTER & AUDIT DISPATCH
# =====================================================================
# Naye tab ko tabs list mein upar add karna na bhoolein: tab1, ..., tab_vis = st.tabs([...])
with tab_audit:  # Aapne is tab ka naam tab_audit rakha hai
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Professional Audit Dispatch Portal</h3>", unsafe_allow_html=True)
    
    vis_sub1, vis_sub2 = st.tabs(["📊 Master Database", "📧 Send Audit Email"])

    # --- EMAIL SENDING FUNCTION ---
    def send_vis_audit_email(selected_df):
        # --- CONFIGURATION (Update these) ---
        SENDER_EMAIL = "your-email@gmail.com"  
        APP_PASSWORD = "xxxx xxxx xxxx xxxx"    # Google App Password
        RECEIVER_EMAIL = "amit.patil@example.com"
        CC_LIST = "Prashant Narkar; Projectvisiontech; Yogita Hatwar"
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%b-%y')
        
        msg = MIMEMultipart()
        msg['Subject'] = f"Audit Request_Visiontech_({tomorrow})"
        msg['From'] = f"Saira Quzi <{SENDER_EMAIL}>"
        msg['To'] = RECEIVER_EMAIL
        msg['Cc'] = CC_LIST

        # HTML Styling
        header_style = "background-color: #FFFF00; font-weight: bold; border: 1px solid black; padding: 5px; font-size: 10px; text-align: center; white-space: nowrap;"
        td_style = "border: 1px solid black; padding: 5px; font-size: 10px; text-align: center;"

        # Image ke hisaab se 27 Columns sequence mein
        audit_headers = [
            "Circle", "Ref. No.", "Indus ID", "Site Name", "Site Add", "Cluster / Zone",
            "Date of Offerance in ISQ", "Date Of Audit Planned in ISQ", "ISQ Offerance Status(Y/N)",
            "Documents uploaded in ISQ(Y/N)", "TSP Shared Filled checklist during Offerance for audit (Yes / No)",
            "TSP Shared Compliance Photographs during audit Offerance (yes / No)", "Project", "Tower Type",
            "Tower Ht.", "Stage", "TSP Name", "Audit Agency Name", "Representative Name",
            "Representative Contact Number", "Actual ofference date", "Audit Engineer Name",
            "Contact Details.", "Actual Audit date", "Actual Audit Time", "Lat", "Long"
        ]

        # Mapping: Agar database column name alag hai toh yahan fix karein
        # Example: Row['Circle'] file mein '#' ya 'OPERATOR' ho sakta hai
        col_map = {
            "Circle": "OPERATOR",
            "Indus ID": "SITE ID",
            "Project": "PROJECT NAME",
            "Actual Audit date": "AUDIT DATE"
        }

        h_html = "".join([f"<th style='{header_style}'>{h}</th>" for h in audit_headers])
        r_html = ""
        for _, row in selected_df.iterrows():
            r_html += "<tr>"
            for h in audit_headers:
                db_col = col_map.get(h, h) # Check mapping else use same name
                val = row.get(db_col, "-")
                r_html += f"<td style='{td_style}'>{val}</td>"
            r_html += "</tr>"

        body_html = f"""
        <html>
        <body style="font-family: Calibri, Arial, sans-serif;">
            <p>Hello Sir,</p>
            <p>Below sites is ready for audit. Kindly arrange auditor for same.</p>
            <div style="overflow-x: auto;">
                <table style="border-collapse: collapse; width: 100%; border: 1px solid black;">
                    <thead><tr style="background-color: #FFFF00;">{h_html}</tr></thead>
                    <tbody>{r_html}</tbody>
                </table>
            </div>
            <br>
            <p>Thanks,<br>
            <b>Saira Quzi</b><br>
            8180827123</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body_html, 'html'))

        try:
            import smtplib
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            st.error(f"Email Error: {e}")
            return False

    # --- SUB TAB 1: VIEW MASTER DATA ---
    with vis_sub1:
        st.write("🔍 Search from Master Portal Data")
        res_vis = supabase.table("VIS Portal Site Data").select("*").limit(1000).execute()
        if res_vis.data:
            df_vis = pd.DataFrame(res_vis.data)
            
            # Simple Filter
            search_key = st.text_input("Filter by Site ID / Project ID", key="vis_search")
            if search_key:
                df_vis = df_vis[df_vis.astype(str).apply(lambda x: x.str.contains(search_key, case=False)).any(axis=1)]
            
            st.dataframe(df_vis, use_container_width=True, hide_index=True)
        else:
            st.info("Database khali hai. Pehle data upload karein.")

    # --- SUB TAB 2: SELECT & DISPATCH ---
    with vis_sub2:
        if res_vis.data:
            st.write("### Select Sites for Audit Email")
            # Select multiple sites from the list
            selected_indices = st.multiselect(
                "Sites select karein:", 
                df_vis.index, 
                format_func=lambda x: f"{df_vis.loc[x, 'SITE ID']} - {df_vis.loc[x, 'SITE NAME']}"
            )
            
            if st.button("🚀 Send Professional Email to Amit Patil", type="primary", use_container_width=True):
                if selected_indices:
                    with st.spinner("Processing Email..."):
                        if send_vis_audit_email(df_vis.loc[selected_indices]):
                            st.success(f"✅ Audit Request Email successfully sent for {len(selected_indices)} sites!")
                else:
                    st.warning("⚠️ Pehle list se kam se kam ek site select karein.")
