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
        st.markdown("### 📤 Export & Share")
        btn_col1, btn_col2 = st.columns([1, 4])
        p_val = df['Project Number'].iloc[0] if not df.empty and 'Project Number' in df.columns else "NA"
        s_id = df['Site ID'].iloc[0] if not df.empty and 'Site ID' in df.columns else "NA"
        s_name = st.session_state.get('wa_site_name', '-')
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False, sheet_name='BOQ_Report')
        processed_data = output.getvalue()
        with btn_col1: st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", use_container_width=True)
        with btn_col2:
            df_sorted = df.copy()
            if 'Sr. No.' in df_sorted.columns:
                df_sorted['Sr. No.'] = pd.to_numeric(df_sorted['Sr. No.'], errors='coerce')
                df_sorted = df_sorted.sort_values(by='Sr. No.')
            df_sorted = df_sorted.reset_index(drop=True)
            wa_msg = f"📦 *BOQ REPORT* : {p_val}\n*Project Number* - {p_val}\n*Site ID* - {s_id}\n*Site Name* - {s_name}\n\n"
            for index, row in df_sorted.iterrows():
                wa_msg += f"{index + 1}.\n*Transaction Type* - {row.get('Transaction Type', '-')}\n*BOQ Number* - {row.get('BOQ', '-')}\n*Item Code* - {row.get('Item Code', '-')}\n*Item Description* - {row.get('Item Description', '-')}\n*BOQ Qty* - {row.get('Qty A', '0')}\n*Dispatched Qty* - {row.get('Qty B', '0')}\n*STN Qty* - {row.get('Qty C', '0')}\n*Parent* - {row.get('Parent/Child', '-')}\n*Dispatched Date* - {row.get('Dispatch Date', '-')}\n*Transporter Name* - {row.get('Transporter', '-')}\n*TSP Name* - {row.get('TSP Partner Name', '-')}\n--------------------\n"
            wa_msg += st.session_state.get('wa_indus_data', "")
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">🚀 Share Full Report</button></a>', unsafe_allow_html=True)

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
                if s_sh.strip():
                    if s_sh.strip().isdigit(): q_po = q_po.eq("Shipment Number", int(s_sh.strip()))
                    else: q_po = q_po.ilike("Shipment Number", f"%{s_sh.strip()}%")
                if s_re.strip(): q_po = q_po.ilike("Receipt Number", f"%{s_re.strip()}%")
                res_po = q_po.execute()
                if res_po.data:
                    df_po = pd.DataFrame(res_po.data)
                    st.write("📋 **Full Details**")
                    st.dataframe(df_po, use_container_width=True, hide_index=True)
                    st.divider()
                    st.write("📌 **Unique Summary**")
                    col_l, col_r = st.columns([0.4, 0.6])
                    with col_l:
                        sum_df = df_po[['PO Number', 'Shipment Number', 'Receipt Number']].drop_duplicates()
                        st.dataframe(sum_df, use_container_width=True, hide_index=True)
                else: st.info("No PO data found.")
            except Exception as e: st.error(f"❌ Error: {e}")

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL (NO CHANGE)
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
# 📊 TAB 4: INDUS DATA (NO CHANGE)
# =====================================================================
with tab4:
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_v5"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID Search")
        with i2: in_nm = st.text_input("🏢 Site Name Search")
        with i3: st.write(""); sub_ind = st.form_submit_button("🔍 Search Indus")
    if sub_ind:
        res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
        if res_ind.data:
            df_ind = pd.DataFrame(res_ind.data)
            st.dataframe(df_ind, use_container_width=True, hide_index=True)
            st.divider(); st.subheader("📌 Vertical Site Details")
            row_in = res_ind.data[0]
            def call_html(label, name, num):
                if num and str(num).strip() not in ['-', '', 'None', 'nan']:
                    return f'{label}: **{name}** ({num}) <a href="tel:{num}"><button style="background-color:#007bff;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;">📞 Call</button></a>'
                return f'{label}: **{name}** (-)'
            v1, v2 = st.columns(2)
            with v1:
                st.markdown(f"🛰️ **Area Name** :- {row_in.get('Area Name','-')}")
                st.markdown(call_html("👨‍🔧 **Tech Name**", row_in.get('Tech Name','-'), row_in.get('Tech Number','-')), unsafe_allow_html=True)
                st.markdown(call_html("👷 **FSE**", row_in.get('FSE','-'), row_in.get('FSE Number','-')), unsafe_allow_html=True)
            with v2:
                st.markdown(call_html("👨‍💼 **AOM Name**", row_in.get('AOM Name','-'), row_in.get('AOM Number','-')), unsafe_allow_html=True)
                lat, lon = row_in.get('Lat', ''), row_in.get('Long', '')
                if lat and lon and str(lat).strip() not in ['-', '', 'None', 'nan']:
                    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                    st.markdown(f"📍 **Lat/Long** :- {lat} / {lon} <a href='{maps_url}' target='_blank'><button style='background-color:#EA4335;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;'>📍 Direction</button></a>", unsafe_allow_html=True)
                else: st.markdown(f"📍 **Lat/Long** :- {lat if lat else '-'} / {lon if lon else '-'}")
        st.divider(); st.subheader("🧭 Route Plan")
        if 'route_list' not in st.session_state: st.session_state.route_list = []
        with st.expander("🛠️ Create New Route Plan", expanded=False):
            c1, c2 = st.columns(2)
            with c1: start_coords = st.text_input("🏠 Start Location", placeholder="Pune")
            with c2: end_coords = st.text_input("🏁 End Location", placeholder="Mumbai")
            with st.form("add_site_form", clear_on_submit=True):
                add_sid = st.text_input("📍 Add Indus Site ID")
                if st.form_submit_button("➕ Add +"):
                    if add_sid:
                        s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                        if s_res.data: st.session_state.route_list.append(s_res.data[0]); st.success(f"Site {add_sid} added!")
                        else: st.error("Site ID not found!")
        if st.button("🚀 Calculate Best Route", use_container_width=True):
            if start_coords and end_coords and st.session_state.route_list:
                try:
                    geolocator = Nominatim(user_agent="vis_route_planner")
                    def get_lat_lon(loc):
                        if ',' in loc and any(c.isdigit() for c in loc): return [float(x.strip()) for x in loc.split(',')]
                        l = geolocator.geocode(loc); return [l.latitude, l.longitude] if l else None
                    curr_p, end_p = get_lat_lon(start_coords), get_lat_lon(end_coords)
                    if curr_p and end_p:
                        unvisited = st.session_state.route_list.copy(); final_path = []
                        while unvisited:
                            valid_sites = [s for s in unvisited if s.get('Lat') and s.get('Long') and str(s.get('Lat')).strip() != '-']
                            if not valid_sites: break
                            next_s = min(valid_sites, key=lambda x: geodesic(curr_p, (float(x['Lat']), float(x['Long']))).km)
                            final_path.append(next_s); curr_p = (float(next_s['Lat']), float(next_s['Long'])); unvisited.remove(next_s)
                        route_data = [{"Serial No": "0", "Task": "START", "Site ID": "Home/Office", "Location": start_coords}]
                        for i, s in enumerate(final_path, 1): route_data.append({"Serial No": str(i), "Task": "Visit", "Site ID": s['Site ID'], "Location": f"{s['Lat']}, {s['Long']}"})
                        route_data.append({"Serial No": str(len(final_path)+1), "Task": "END", "Site ID": "Destination", "Location": end_coords})
                        st.table(pd.DataFrame(route_data))
                        coords_str = "/".join([start_coords] + [f"{s['Lat']},{s['Long']}" for s in final_path] + [end_coords])
                        st.markdown(f'<a href="https://www.google.com/maps?q=lat,long{coords_str}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Full Route in Maps</button></a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

# =====================================================================
# 📡 TAB 5: WCC TRACKER (RESTORED TO ORIGINAL WITH EDIT & WHATSAPP)
# =====================================================================
with tab_wcc:
    def fetch_wcc():
        try: 
            res = supabase.table("WCC Status").select("*").execute()
            return res.data
        except: return []

    def save_wcc_data(payload):
        try:
            return supabase.table("WCC Status").upsert(payload).execute()
        except Exception as e:
            st.error(f"❌ Database Error: {e}")
            return None

    st.title("📡 WCC Status Tracker")

    if "wcc_role" not in st.session_state: st.session_state.wcc_role = None

    if not st.session_state.wcc_role:
        pwd = st.text_input("Enter Password:", type="password", key="wcc_pwd_v24_style")
        if st.button("🔓 Unlock Folder"):
            if pwd == "Vision@321": st.session_state.wcc_role = "requester"
            elif pwd == "Account@321": st.session_state.wcc_role = "accountant"
            else: st.error("❌ Wrong Password!")
            st.rerun()
    else:
        role = st.session_state.wcc_role
        st.info(f"Logged in as: **{role.upper()}**")
        if st.sidebar.button("🔒 Logout WCC"):
            st.session_state.wcc_role = None
            st.rerun()

        @st.dialog("📝 WCC Details Form", width="large")
        def wcc_modal(row_data=None):
            is_edit = row_data is not None
            with st.form("wcc_form_v24"):
                if role == "requester":
                    c1, c2 = st.columns(2)
                    v_proj = c1.text_input("Project", value=str(row_data.get("Project", "")) if is_edit else "")
                    v_pid = c2.text_input("Project ID *", value=str(row_data.get("Project ID", "")) if is_edit else "", disabled=is_edit)
                    c3, c4 = st.columns(2)
                    v_sid = c3.text_input("Site ID", value=str(row_data.get("Site ID", "")) if is_edit else "")
                    v_snm = c4.text_input("Site Name", value=str(row_data.get("Site Name", "")) if is_edit else "")
                    c5, c6 = st.columns(2)
                    v_po = c5.text_input("PO Number", value=str(row_data.get("PO Number", "")) if is_edit else "")
                    d_val = datetime.now().date()
                    if is_edit and row_data.get("Reqeust Date"):
                        try: d_val = pd.to_datetime(row_data.get("Reqeust Date")).date()
                        except: d_val = datetime.now().date()
                    v_dt = st.date_input("Request Date", value=d_val)
                    st.markdown("### Status Tracking")
                    c7, c8, c9 = st.columns(3)
                    p_opts = ["Pending", "Available on Portal"]
                    v_pht = c7.selectbox("Photo", p_opts, index=p_opts.index(row_data.get("Photo", "Available on Portal")) if is_edit and row_data.get("Photo") in p_opts else 1)
                    j_opts = ["Pending", "Available on Portal", "Create by You"]
                    v_jms = c8.selectbox("JMS", j_opts, index=j_opts.index(row_data.get("JMS", "Create by You")) if is_edit and row_data.get("JMS") in j_opts else 2)
                    s_opts = ["Creation Pending", "Pending for Approval", "Proceed", "Rejected", "Cancel"]
                    v_sts = c9.selectbox("WCC Status", s_opts, index=s_opts.index(row_data.get("WCC Status", "Creation Pending")) if is_edit and row_data.get("WCC Status") in s_opts else 0)
                    v_wno = row_data.get("WCC Number") if is_edit else None 
                else:
                    v_pid = row_data.get('Project ID')
                    v_wno = st.text_input("Enter WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")

                submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
                if submitted:
                    def clean_numeric(val):
                        if not val or str(val).strip() in ["", "None", "nan"]: return None
                        num_only = ''.join(filter(str.isdigit, str(val)))
                        return num_only if num_only != "" else None
                    payload = {"Project ID": v_pid, "WCC Number": clean_numeric(v_wno)}
                    if role == "requester":
                        payload.update({"Project": v_proj, "Site ID": v_sid, "Site Name": v_snm, "PO Number": clean_numeric(v_po), "Reqeust Date": str(v_dt), "Photo": v_pht, "JMS": v_jms, "WCC Status": v_sts})
                    if save_wcc_data(payload): st.rerun()

        raw_data = fetch_wcc()
        df_wcc = pd.DataFrame(raw_data) if raw_data else pd.DataFrame()
        
        c_top1, c_top2 = st.columns(2)
        with c_top1:
            if role == "requester" and st.button("➕ Add New Site Request", type="primary", use_container_width=True): wcc_modal()
        with c_top2:
            if not df_wcc.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df_wcc.to_excel(writer, index=False)
                st.download_button(label="📥 Download Excel Report", data=output.getvalue(), file_name="WCC_Report.xlsx", use_container_width=True)

        st.divider()

        if not df_wcc.empty:
            st.markdown("""
                <style>
                .main-header { font-size: 20px; font-weight: bold; color: #1E3A8A; margin-bottom: 10px; }
                .site-badge { background-color: #E0F2FE; color: #0369A1; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 12px; border: 1px solid #BAE6FD; }
                .wa-btn { background-color: #25D366; color: white !important; padding: 6px 12px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: bold; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .wa-btn:hover { background-color: #128C7E; }
                </style>
            """, unsafe_allow_html=True)

            h_cols = st.columns([0.6, 0.4, 1, 1.2, 1, 1.2, 1, 1, 1, 1, 1, 1])
            fields = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "Date", "Photo", "JMS", "WCC No", "Status"]
            for col, name in zip(h_cols, fields): col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:14px;'>{name}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

            for i, row in df_wcc.iterrows():
                r_cols = st.columns([0.6, 0.4, 1, 1.2, 1, 1.2, 1, 1, 1, 1, 1, 1])
                with r_cols[0]:
                    b1, b2 = st.columns(2)
                    if b1.button("✏️", key=f"sty_ed_{row['Project ID']}"): wcc_modal(row)
                    if role == 'requester':
                        msg = (f"Hello Prkash Ji,\nRaise WCC urgently...\n\n*Project* :- {row.get('Project')}\n*Project ID* :- {row.get('Project ID')}\n*Site ID* :- {row.get('Site ID')}\n*Site Name* :- {row.get('Site Name')}\n*PO Number* :- {row.get('PO Number')}\n*Reqeust Date* :- {row.get('Reqeust Date')}\n*WCC Number* :- {row.get('WCC Number')}\n*WCC Status* :- {row.get('WCC Status')}\n\nThanks,\nMayur Patil\n7350533473")
                        url = f"whatsapp://send?text={urllib.parse.quote(msg)}"
                        b2.markdown(f'<a href="{url}" class="wa-btn">💬</a>', unsafe_allow_html=True)

                r_cols[1].write(f"<p style='font-size:13px;'>{i+1}</p>", unsafe_allow_html=True)
                r_cols[2].write(f"<p style='font-size:13px;'>{row.get('Project','')}</p>", unsafe_allow_html=True)
                r_cols[3].write(f"<p style='font-size:13px;'>{row.get('Project ID','')}</p>", unsafe_allow_html=True)
                r_cols[4].markdown(f'<span class="site-badge">{row.get("Site ID","")}</span>', unsafe_allow_html=True)
                r_cols[5].write(f"<p style='font-size:13px;'>{row.get('Site Name','')}</p>", unsafe_allow_html=True)
                r_cols[6].write(f"<p style='font-size:13px;'>{row.get('PO Number','')}</p>", unsafe_allow_html=True)
                r_cols[7].write(f"<p style='font-size:13px;'>{row.get('Reqeust Date','')}</p>", unsafe_allow_html=True)
                r_cols[8].write(f"<p style='font-size:13px;'>{row.get('Photo','')}</p>", unsafe_allow_html=True)
                r_cols[9].write(f"<p style='font-size:13px;'>{row.get('JMS','')}</p>", unsafe_allow_html=True)
                r_cols[10].markdown(f"<p style='color:#DC2626; font-weight:bold; font-size:13px;'>{row.get('WCC Number','-')}</p>", unsafe_allow_html=True)
                r_cols[11].write(f"<p style='font-size:13px;'>{row.get('WCC Status','')}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:0; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        else: st.info("No records found.")

# =====================================================================
# 📁 TAB 6: DATA ENTRY (DOCUMENT CENTER)
# =====================================================================
with tab5:
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center</h3>", unsafe_allow_html=True)
    d_sub1, d_sub2, d_sub3 = st.tabs(["📤 Upload", "🔍 Search", "📊 Status"])
    with d_sub1:
        with st.form("doc_upload_v1", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            u_proj = col_u1.text_input("📁 Project Number")
            u_indus = col_u2.text_input("📍 Indus ID")
            u_site = col_u1.text_input("🏢 Site Name")
            u_type = col_u2.selectbox("📄 Doc Type", ["Photo", "SRC", "DC", "STN", "REPORT"])
            u_files = st.file_uploader("Select Files", accept_multiple_files=True)
            if st.form_submit_button("🚀 Upload"):
                if u_files and u_proj:
                    for i, single_file in enumerate(u_files):
                        fname = f"{u_proj.replace('/','-')}_{u_indus}_{u_type}_{i}.{single_file.name.split('.')[-1]}"
                        supabase.storage.from_("site_documents").upload(path=fname, file=single_file.getvalue(), file_options={"x-upsert": "true"})
                        p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                        supabase.table("site_documents_master").upsert({"project_number": u_proj, "indus_id": u_indus, "site_name": u_site, "doc_type": u_type, "file_name": fname, "file_url": p_url}, on_conflict="file_name").execute()
                    st.success("Uploaded!")
    with d_sub2:
        q_s = st.text_input("Search...")
        if q_s:
            r = supabase.table("site_documents_master").select("*").or_(f"project_number.ilike.%{q_s}%,indus_id.ilike.%{q_s}%").execute()
            if r.data: st.write(r.data)
    with d_sub3:
        r_t = supabase.table("site_documents_master").select("*").execute()
        if r_t.data:
            df_t = pd.DataFrame(r_t.data)
            st.dataframe(df_t, use_container_width=True)

❌
Error: 'Series' object has no attribute 'strip'
