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
tab1, tab2, tab3, tab4, tab_wcc, tab5, tab6 = st.tabs([
    "📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", 
    "📊 Indus Basic Data", "📡 WCC Tracker", "📁 Data Entry", "💰 Finance Entry"
])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT
# =====================================================================
with tab1:
    st.markdown("""
        <style>
            div[data-testid="stDataTableBody"]::-webkit-scrollbar { width: 14px; height: 14px; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb { background: #888; border-radius: 10px; border: 2px solid #f1f1f1; }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb:hover { background: #555; }
        </style>
    """, unsafe_allow_html=True)    
    st.markdown("<h3 style='text-align: center;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

    if 'cleared' not in st.session_state: st.session_state.cleared = False

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
    with r4: update_click = st.button("🔄 Update", use_container_width=True)

    if submit_search or stn_pending_btn or gen_new_boq or update_click:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        # API Logics... (Original)
        response = query.execute()
        if response.data:
            df_res = pd.DataFrame(response.data)
            st.session_state['boq_df'] = df_res

    if 'boq_df' in st.session_state:
        st.dataframe(st.session_state['boq_df'], use_container_width=True, hide_index=True)

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
# 📡 TAB 5: WCC TRACKER (EDIT & WHATSAPP BUTTONS RESTORED)
# =====================================================================
with tab_wcc:
    def fetch_wcc():
        try: res = supabase.table("WCC Status").select("*").execute(); return res.data
        except: return []
    def save_wcc_data(p):
        try: return supabase.table("WCC Status").upsert(p).execute()
        except: return None

    st.title("📡 WCC Status Tracker")
    if "wcc_role" not in st.session_state: st.session_state.wcc_role = None
    if not st.session_state.wcc_role:
        pwd = st.text_input("Enter Password:", type="password", key="wcc_pwd_style")
        if st.button("🔓 Unlock Folder"):
            if pwd == "Vision@321": st.session_state.wcc_role = "requester"
            elif pwd == "Account@321": st.session_state.wcc_role = "accountant"
            else: st.error("❌ Wrong Password!")
            st.rerun()
    else:
        role = st.session_state.wcc_role
        @st.dialog("📝 WCC Details Form", width="large")
        def wcc_modal(row_data=None):
            is_edit = row_data is not None
            with st.form("wcc_form_v24"):
                if role == "requester":
                    c1, c2 = st.columns(2)
                    v_proj = c1.text_input("Project", value=str(row_data.get("Project", "")) if is_edit else "")
                    v_pid = c2.text_input("Project ID *", value=str(row_data.get("Project ID", "")) if is_edit else "", disabled=is_edit)
                    v_sid = st.text_input("Site ID", value=str(row_data.get("Site ID", "")) if is_edit else "")
                    v_snm = st.text_input("Site Name", value=str(row_data.get("Site Name", "")) if is_edit else "")
                    v_po = st.text_input("PO Number", value=str(row_data.get("PO Number", "")) if is_edit else "")
                    v_dt = st.date_input("Request Date", value=datetime.now().date())
                    v_sts = st.selectbox("WCC Status", ["Creation Pending", "Pending for Approval", "Proceed", "Rejected", "Cancel"], index=0)
                    v_wno = row_data.get("WCC Number") if is_edit else None 
                else:
                    v_pid = row_data.get('Project ID')
                    v_wno = st.text_input("Enter WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                if st.form_submit_button("💾 Save Changes"):
                    def cn(v): return ''.join(filter(str.isdigit, str(v))) if v else None
                    p = {"Project ID": v_pid, "WCC Number": cn(v_wno)}
                    if role == "requester": p.update({"Project": v_proj, "Site ID": v_sid, "Site Name": v_snm, "PO Number": cn(v_po), "Reqeust Date": str(v_dt), "WCC Status": v_sts})
                    if save_wcc_data(p): st.rerun()

        raw_w = fetch_wcc()
        df_wcc = pd.DataFrame(raw_w) if raw_w else pd.DataFrame()
        if role == "requester" and st.button("➕ Add Site Request"): wcc_modal()
        if not df_wcc.empty:
            st.markdown("""<style>.site-badge { background-color: #E0F2FE; color: #0369A1; padding: 4px 10px; border-radius: 20px; font-weight: 600; border: 1px solid #BAE6FD; } .wa-btn { background-color: #25D366; color: white !important; padding: 6px 12px; border-radius: 8px; font-weight: bold; text-decoration: none; }</style>""", unsafe_allow_html=True)
            for i, row in df_wcc.iterrows():
                c_act, c_proj, c_sid, c_sts = st.columns([1, 2, 2, 2])
                with c_act:
                    if st.button("✏️", key=f"ed_{row['Project ID']}"): wcc_modal(row)
                    if role == 'requester':
                        msg = f"Hello Prkash Ji,\nRaise WCC urgently...\n\n*Project ID* :- {row.get('Project ID')}"
                        st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(msg)}" class="wa-btn">💬</a>', unsafe_allow_html=True)
                c_proj.write(row.get('Project ID'))
                c_sid.markdown(f'<span class="site-badge">{row.get("Site ID")}</span>', unsafe_allow_html=True)
                c_sts.write(row.get('WCC Status'))

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
