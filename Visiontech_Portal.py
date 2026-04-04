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

NEW_URL = "https://your-new-project-id.supabase.co" 
NEW_KEY = "your-new-anon-key-here"
supabase_new = create_client(NEW_URL, NEW_KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Infra Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 VIS Group")
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Infra Solutions")

# --- 3. TABS ---
# MAINE YAHAN WCC TRACKER KO TAB MEIN ADD KIYA HAI
tab1, tab2, tab3, tab4, tab_wcc, tab5, tab6 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data", "📡 WCC Tracker", "📁 Data Entry", "💰 Finance Entry"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT
# =====================================================================
with tab1:
    # --- NAYA: CUSTOM SCROLLBAR STYLE ---
    st.markdown("""
        <style>
            /* Pure table container ka scrollbar bada karne ke liye */
            div[data-testid="stDataTableBody"]::-webkit-scrollbar {
                width: 14px;      /* Vertical scrollbar ki choudai */
                height: 14px;     /* Horizontal scrollbar ki oonchai */
            }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-track {
                background: #f1f1f1; 
                border-radius: 10px;
            }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb {
                background: #888; 
                border-radius: 10px;
                border: 2px solid #f1f1f1; /* Space deta hai taaki pakadne mein aasani ho */
            }
            div[data-testid="stDataTableBody"]::-webkit-scrollbar-thumb:hover {
                background: #555; /* Mouse le jaane par color dark ho jayega */
            }
            
            /* Agar aap standard dataframe use kar rahe hain toh uske liye bhi: */
            .stDataFrame div::-webkit-scrollbar {
                width: 14px !important;
                height: 14px !important;
            }
            .stDataFrame div::-webkit-scrollbar-thumb {
                background-color: #007bff !important; /* Blue color taaki alag dikhe */
                border-radius: 10px !important;
            }
        </style>
    """, unsafe_allow_html=True)    
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Infra Solutions</h3>", unsafe_allow_html=True)
    mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

   # 1. Clear Functionality ke liye keys initialize karein (form ke upar)
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
                if submit_search:
                    st.session_state.cleared = False # Search ke waqt clear nahi karna
            with col_btn2:
                if st.form_submit_button("🗑️ Clear"):
                    st.session_state.cleared = True # Agli baar form clear ho jayega
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

            if update_click: 
                display_sequence = ['Project Number', 'Dispatch Date']
            else:
                display_sequence = mera_sequence
                if 'Item Code' in df_res.columns:
                    df_res['TempGroupKey'] = df_res.apply(lambda x: x['Sr. No.'] if str(x['Item Code']).strip() == '' else x['Item Code'], axis=1)
                    agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['TempGroupKey']}
                    df_res = df_res.groupby('TempGroupKey', as_index=False).agg(agg_dict)
            
            st.session_state['display_cols'] = display_sequence

            # --- FETCH SITE NAME & INDUS DATA ---
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
        s_name = st.session_state.get('wa_site_name', '-')
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='BOQ_Report')
        processed_data = output.getvalue()
        
        with btn_col1:
            st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", use_container_width=True)
        
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
        with i1: in_id = st.text_input("📍 Site ID Search")
        with i2: in_nm = st.text_input("🏢 Site Name Search")
        with i3: st.write(""); sub_ind = st.form_submit_button("🔍 Search Indus")
    if sub_ind:
        res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
        if res_ind.data:
            df_ind = pd.DataFrame(res_ind.data)
            st.dataframe(df_ind, use_container_width=True, hide_index=True)
            st.divider()
            st.subheader("📌 Vertical Site Details")
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
        else: st.info("No Indus data found.")

    st.divider()
    st.subheader("🧭 Route Plan")
    if 'route_list' not in st.session_state: st.session_state.route_list = []
    with st.expander("🛠️ Create New Route Plan", expanded=False):
        c1, c2 = st.columns(2)
        with c1: start_coords = st.text_input("🏠 Start Location (City or Lat, Long)", placeholder="e.g. Pune")
        with c2: end_coords = st.text_input("🏁 End Location (City or Lat, Long)", placeholder="e.g. Mumbai")
        with st.form("add_site_form", clear_on_submit=True):
            add_sid = st.text_input("📍 Add Indus Site ID")
            if st.form_submit_button("➕ Add +"):
                if add_sid:
                    s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                    if s_res.data: st.session_state.route_list.append(s_res.data[0]); st.success(f"Site {add_sid} added!")
                    else: st.error("Site ID not found!")
        if st.session_state.route_list:
            st.write("**Current Sites:** " + ", ".join([s['Site ID'] for s in st.session_state.route_list]))
            if st.button("🗑️ Clear List"): st.session_state.route_list = []; st.rerun()
    if st.button("🚀 Calculate Best Route", use_container_width=True):
        if not start_coords or not end_coords or not st.session_state.route_list: st.warning("Incomplete details!")
        else:
            try:
                geolocator = Nominatim(user_agent="vis_route_planner")
                def get_lat_lon(loc):
                    if ',' in loc and any(c.isdigit() for c in loc): return [float(x.strip()) for x in loc.split(',')]
                    l = geolocator.geocode(loc); return [l.latitude, l.longitude] if l else None
                curr_p, end_p = get_lat_lon(start_coords), get_lat_lon(end_coords)
                if not curr_p or not end_p: st.error("Check Start/End location name.")
                else:
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
                    gmaps_route = f"https://www.google.com/maps?q=lat,long{coords_str}"
                    st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Full Route in Maps</button></a>', unsafe_allow_html=True)
            except Exception as e: st.error(f"Error: {e}")

# =====================================================================
# 📡 TAB 5: WCC TRACKER
# =====================================================================
with tab_wcc:
    # --- HELPER FUNCTIONS FOR WCC TRACKER ---
    def fetch_table(table_name):
        try:
            res = supabase.table(table_name).select("*").execute()
            return res.data
        except Exception as e: 
            st.error(f"Error fetching data: {e}")
            return []

    def insert_row(table_name, data):
        return supabase.table(table_name).insert(data).execute()

    def update_row(table_name, row_id, data):
        return supabase.table(table_name).update(data).eq("id", row_id).execute()

    st.title("📡 WCC Status Tracker")

    # --- 1. PASSWORD PROTECTION ---
    if "wcc_auth" not in st.session_state:
        st.session_state.wcc_auth = False

    if not st.session_state.wcc_auth:
        st.warning("🔒 This section is highly confidential and locked.")
        c1, c2 = st.columns([1, 2])
        with c1:
            pwd = st.text_input("Enter Password:", type="password")
            if st.button("🔓 Unlock Tracker", type="primary"):
                if pwd == "Vision@321":
                    st.session_state.wcc_auth = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password!")
    else:
        # Tracker Unlocked State
        t1, t2 = st.columns([4, 1])
        t2.button("🔒 Lock Tracker", on_click=lambda: st.session_state.update(wcc_auth=False))
        
        st.write("---")

        df_wcc = pd.DataFrame(fetch_table("WCC Status"))

       # --- 2. POP-UP DIALOG FOR ADD/EDIT WCC ---
        @st.dialog("📝 WCC Details Form", width="large")
        def wcc_form_modal(ed=None):
            with st.form("wcc_update_form"):
                st.subheader("Site Information")
                c1, c2 = st.columns(2)
                p_id = c1.text_input("Project ID", value=str(ed.get("Project ID", "")) if ed is not None else "")
                s_id = c2.text_input("Site ID", value=str(ed.get("Site ID", "")) if ed is not None else "")

                c3, c4 = st.columns(2)
                s_name = c3.text_input("Site Name", value=str(ed.get("Site Name", "")) if ed is not None else "")
                po_no = c4.text_input("PO Number", value=str(ed.get("PO Number", "")) if ed is not None else "")

                c5, c6 = st.columns(2)
                
                # --- FIX: DATE FORMAT & CALENDAR PICKER ---
                existing_date = ed.get("Reqeust Date", "") if ed is not None else ""
                parsed_date = None
                if existing_date and str(existing_date).strip() not in ["", "None", "nan", "NULL"]:
                    try:
                        parsed_date = pd.to_datetime(existing_date).date()
                    except:
                        parsed_date = None
                
                # Yeh aapko Date Select (Calendar) ka option dega
                req_date_obj = c5.date_input("Request Date", value=parsed_date)
                
                wcc_no = c6.text_input("WCC Number", value=str(ed.get("WCC Number", "")) if ed is not None else "")

                st.markdown("### 📊 Status Tracking")
                c7, c8, c9 = st.columns(3)

                photo_opts = ["Pending", "Available on Portal"]
                photo_val = str(ed.get("Photo", "Pending")) if ed is not None else "Pending"
                photo = c7.selectbox("Photo *", photo_opts, index=photo_opts.index(photo_val) if photo_val in photo_opts else 0)

                jms_opts = ["Pending", "Available on Portal", "Create by You"]
                jms_val = str(ed.get("JMS", "Pending")) if ed is not None else "Pending"
                jms = c8.selectbox("JMS *", jms_opts, index=jms_opts.index(jms_val) if jms_val in jms_opts else 0)

                status_opts = ["Creation Pending", "Pending for Approval", "Proceed", "Rejected", "Cancel"]
                status_val = str(ed.get("WCC Status", "Creation Pending")) if ed is not None else "Creation Pending"
                wcc_status = c9.selectbox("WCC Status *", status_opts, index=status_opts.index(status_val) if status_val in status_opts else 0)

                if st.form_submit_button("💾 Save WCC Record", use_container_width=True):
                    # FIX: Supabase ko strict 'None' bhejna hai agar form khali ho
                    final_req_date = req_date_obj.strftime('%Y-%m-%d') if req_date_obj is not None else None
                    
                    payload = {
                        "Project ID": p_id.strip() if p_id.strip() else None,
                        "Site ID": s_id.strip() if s_id.strip() else None,
                        "Site Name": s_name.strip() if s_name.strip() else None,
                        "PO Number": po_no.strip() if po_no.strip() else None,
                        "Reqeust Date": final_req_date,  # <-- Ab Supabase Crash nahi karega
                        "Photo": photo,
                        "JMS": jms,
                        "WCC Number": wcc_no.strip() if wcc_no.strip() else None,
                        "WCC Status": wcc_status
                    }
                    
                    try:
                        if ed is not None and 'id' in ed:
                            update_row("WCC Status", ed['id'], payload)
                        else:
                            insert_row("WCC Status", payload)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Database Error: {e}")
        # --- 3. URL PARAMS FOR ACTIONS ---
        if "edit_wcc" in st.query_params:
            rid = str(st.query_params["edit_wcc"])
            st.query_params.clear()
            st.query_params["menu"] = "WCC Tracker"

            ed_row = pd.DataFrame()
            for idx, row in df_wcc.iterrows():
                db_id = str(row.get('id', row.get('ID', idx)))
                if db_id == rid:
                    ed_row = df_wcc.iloc[[idx]]
                    break

            if not ed_row.empty:
                wcc_form_modal(ed_row.iloc[0].to_dict())

        # Top Button
        if st.button("➕ Add New WCC Record", type="primary"):
            wcc_form_modal()

        # --- 4. LAVISH WCC TABLE ---
        if not df_wcc.empty:
            import urllib.parse

            html_code = """
            <style>
            .wcc-scroll { width: 100%; overflow-x: auto; border-radius: 10px; border: 1px solid #ddd; background: white; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); position: relative; z-index: 10; }
            .wcc-table { width: 100%; border-collapse: separate; border-spacing: 0; min-width: 1800px; font-family: sans-serif; }
            .wcc-table th { background: #009688; color: white; padding: 12px; text-align: left; position: sticky; top: 0; z-index: 20; font-size: 14px; border-bottom: 1px solid #eee; }
            .wcc-table td { padding: 12px; border-bottom: 1px solid #eee; font-size: 13px; color: #333; }
            .wcc-table tr:hover td { background: #e0f2f1; }
            .wcc-action { position: sticky; left: 0; background: #f4f6f9 !important; z-index: 999 !important; border-right: 2px solid #ddd !important; text-align: center; }
            .wcc-action-head { position: sticky; left: 0; z-index: 1000 !important; background: #009688 !important; border-right: 2px solid #00796b !important; text-align: center; }
            .wcc-btn { text-decoration: none; font-size: 18px; margin: 0 8px; cursor: pointer; position: relative; z-index: 9999 !important; pointer-events: auto !important; display: inline-block; }
            .wcc-btn:hover { transform: scale(1.2); }
            .wcc-badge { background: #e0f2f1; color: #00796b; padding: 4px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; }
            </style>

            <div class="wcc-scroll">
                <table class="wcc-table">
                    <tr>
                        <th class="wcc-action-head">Actions</th>
                        <th>Sr. No.</th>
                        <th>Project ID</th>
                        <th>Site ID</th>
                        <th>Site Name</th>
                        <th>PO Number</th>
                        <th>Request Date</th>
                        <th>Photo</th>
                        <th>JMS</th>
                        <th>WCC Number</th>
                        <th>WCC Status</th>
                    </tr>
            """

            for i, row in df_wcc.iterrows():
                db_id = row.get('id', row.get('ID', i))
                p_id = str(row.get('Project ID', '-'))
                s_id = str(row.get('Site ID', '-'))
                s_name = str(row.get('Site Name', '-'))
                po_no = str(row.get('PO Number', '-'))
                req_date = str(row.get('Reqeust Date', '-')) 
                wcc_no = str(row.get('WCC Number', '-'))
                wcc_sts = str(row.get('WCC Status', '-'))

                # Generate Exact WhatsApp Message
                wa_msg = f"""Hello,
Below Site WCC Request sent to you kindly raise WCC urgently and comfirm on Website.
All Detail Available on our vispltower.com software.

*Project ID* :- {p_id}
*Site ID* :- {s_id}
*Site Name* :- {s_name}
*PO Number* :- {po_no}
*Reqeust Date* :- {req_date}
*WCC Number* :- {wcc_no}
*WCC Status* :- {wcc_sts}

In case of any document or detail required please call to me or whatsaap to me but raise wcc in 1st priority."""
                
                # Format URL for WhatsApp API
                wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"

                html_code += f"""
                    <tr>
                        <td class="wcc-action">
                            <a href="?menu=WCC Tracker&edit_wcc={db_id}" target="_self" class="wcc-btn" title="Edit Record">✏️</a>
                            <a href="{wa_link}" target="_blank" class="wcc-btn" title="Send WhatsApp Message">💬</a>
                        </td>
                        <td><b>{i + 1}</b></td>
                        <td style="font-weight:bold; color:#009688;">{p_id}</td>
                        <td>{s_id}</td>
                        <td>{s_name}</td>
                        <td>{po_no}</td>
                        <td>{req_date}</td>
                        <td><span class="wcc-badge">{row.get('Photo', '-')}</span></td>
                        <td><span class="wcc-badge">{row.get('JMS', '-')}</span></td>
                        <td style="color:#e65100; font-weight:bold;">{wcc_no}</td>
                        <td><span class="wcc-badge">{wcc_sts}</span></td>
                    </tr>
                """

            html_code += "</table></div>"
            st.markdown(html_code.replace('\n', ''), unsafe_allow_html=True)

        else:
            st.info("No records found in WCC Status.")
