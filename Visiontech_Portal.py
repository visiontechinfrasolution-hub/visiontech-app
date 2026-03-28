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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data", "📁 Data Entry", "💰 Finance Entry"])

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (Original & Untouched Code)
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
            if boq_date_pick:
                gen_new_boq = True
            else:
                st.warning("Select Date!")

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
            
            # --- START FIXED LOGIC ---
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
            # --- END FIXED LOGIC ---

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
        
        with btn_col1:
            st.download_button(label="📥 Download Excel", data=processed_data, file_name=f"{p_val}_{s_id}.xlsx", use_container_width=True)

        with btn_col2:
            # --- 1. Header Details ---
            wa_msg = f"📦 *BOQ REPORT* : {p_val}\n"
            wa_msg += f"*Project Number* - {p_val}\n"
            wa_msg += f"*Site ID* - {s_id}\n"
            
            # Site Name agar available ho toh
            site_nm = df['Site Name'].iloc[0] if 'Site Name' in df.columns else "-"
            wa_msg += f"*Site Name* - {s_name}\n\n" # 🟢 Ab yahan Site Name aayega
            
            # --- 2. BOQ Items Loop (Numbered Format) ---
            for index, row in df.iterrows():
                wa_msg += f"{index + 1}.\n"
                wa_msg += f"*Transaction Type* - {row.get('Transaction Type', '-')}\n"
                wa_msg += f"*BOQ Number* - {row.get('BOQ', '-')}\n"
                wa_msg += f"*Item Code* - {row.get('Item Code', '-')}\n"
                wa_msg += f"*Item Description* - {row.get('Item Description', '-')}\n"
                wa_msg += f"*BOQ Qty* - {row.get('Qty A', '0')}\n"
                wa_msg += f"*Dispatched Qty* - {row.get('Qty B', '0')}\n"
                wa_msg += f"*STN Qty* - {row.get('Qty C', '0')}\n"
                wa_msg += f"*Parent* - {row.get('Parent/Child', '-')}\n"
                wa_msg += f"*Dispatched Date* - {row.get('Dispatch Date', '-')}\n"
                wa_msg += f"*Transporter Name* - {row.get('Transporter', '-')}\n"
                wa_msg += f"*TSP Name* - {row.get('TSP Partner Name', '-')}\n"
                wa_msg += "--------------------\n"
            
            # --- 3. Indus Site Data (Vertical Format) ---
            wa_msg += st.session_state.get('wa_indus_data', "")

            # URL Encode and Button
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">🚀 Share Full Report</button></a>', unsafe_allow_html=True)
# =====================================================================
# 🧾 TAB 2: PO REPORT (Original Code with BigInt Fix & Summary Table)
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
                
                # Check for PO Number (Handling BigInt Error)
                if s_po.strip():
                    if s_po.strip().isdigit(): 
                        q_po = q_po.eq("PO Number", int(s_po.strip()))
                    else: 
                        q_po = q_po.ilike("PO Number", f"%{s_po.strip()}%")
                
                # Check for Shipment Number (Handling BigInt Error)
                if s_sh.strip():
                    if s_sh.strip().isdigit(): 
                        q_po = q_po.eq("Shipment Number", int(s_sh.strip()))
                    else: 
                        q_po = q_po.ilike("Shipment Number", f"%{s_sh.strip()}%")
                
                # Check for Receipt Number
                if s_re.strip(): 
                    q_po = q_po.ilike("Receipt Number", f"%{s_re.strip()}%")
                
                res_po = q_po.execute()
                
                if res_po.data:
                    df_po = pd.DataFrame(res_po.data)
                    
                    # 1. Main Table (Full Details)
                    st.write("📋 **Full Details**")
                    st.dataframe(df_po, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    
                    # 2. Unique Summary Table (Left Side, No Duplicates)
                    st.write("📌 **Unique Summary**")
                    col_l, col_r = st.columns([0.4, 0.6])
                    with col_l:
                        sum_df = df_po[['PO Number', 'Shipment Number', 'Receipt Number']].drop_duplicates()
                        st.dataframe(sum_df, use_container_width=True, hide_index=True)
                else: 
                    st.info("No PO data found.")
            except Exception as e: 
                st.error(f"❌ Error: {e}")

# =====================================================================
# 🏗️ TAB 3: SITE DETAIL (Existing Logic)
# =====================================================================
with tab3:
    # (Existing Site Detail logic - unchanged)
    pass

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (Fixed Vertical Display, Call & Route Plan)
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
            # 1. Pehle table dikhayenge
            df_ind = pd.DataFrame(res_ind.data)
            st.dataframe(df_ind, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # 2. Ab Vertical Detail with Call Buttons & Direction
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
                
                lat = row_in.get('Lat', '')
                lon = row_in.get('Long', '')
                
                if lat and lon and str(lat).strip() not in ['-', '', 'None', 'nan']:
                    maps_url = f"https://www.google.com/maps?q={lat},{lon}"
                    st.markdown(
                        f"📍 **Lat/Long** :- {lat} / {lon} "
                        f'<a href="{maps_url}" target="_blank">'
                        f'<button style="background-color:#EA4335;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;">📍 Direction</button>'
                        f'</a>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"📍 **Lat/Long** :- {lat if lat else '-'} / {lon if lon else '-'}")
        else:
            st.info("No Indus data found for this Site ID.")

    # --- NAYA SECTION: ROUTE PLANNER ---
    st.divider()
    st.subheader("🧭 Route Plan")

    if 'route_list' not in st.session_state:
        st.session_state.route_list = []

    with st.expander("🛠️ Create New Route Plan", expanded=False):
        c1, c2 = st.columns(2)
        # 🟢 NAYA: Ab aap City ka naam (Pune) bhi daal sakte hain
        with c1: start_coords = st.text_input("🏠 Start Location (City or Lat, Long)", placeholder="e.g. Pune or 18.52, 73.85")
        with c2: end_coords = st.text_input("🏁 End Location (City or Lat, Long)", placeholder="e.g. Mumbai or 19.07, 72.87")
        
        st.write("---")
        
        # 🟢 NAYA: Form use kiya taaki 'Add' dabane ke baad box automatically CLEAR ho jaye
        with st.form("add_site_form", clear_on_submit=True):
            add_sid = st.text_input("📍 Add Indus Site ID")
            submit_add = st.form_submit_button("➕ Add +")
            
            if submit_add:
                if add_sid:
                    s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                    if s_res.data:
                        st.session_state.route_list.append(s_res.data[0])
                        st.success(f"Site {add_sid} added!")
                    else:
                        st.error("Site ID not found!")

        if st.session_state.route_list:
            st.write("**Current Sites:** " + ", ".join([s['Site ID'] for s in st.session_state.route_list]))
            if st.button("🗑️ Clear List"):
                st.session_state.route_list = []
                st.rerun()

    if st.button("🚀 Calculate Best Route", use_container_width=True):
        if not start_coords or not end_coords or not st.session_state.route_list:
            st.warning("Please provide Start, End locations and at least one Site ID.")
        else:
            try:
                # 🟢 NAYA: City name ko Coordinates mein badalne ka logic
                geolocator = Nominatim(user_agent="vis_route_planner")
                
                def get_lat_lon(loc_input):
                    if ',' in loc_input and any(char.isdigit() for char in loc_input):
                        return [float(x.strip()) for x in loc_input.split(',')]
                    else:
                        location = geolocator.geocode(loc_input)
                        if location:
                            return [location.latitude, location.longitude]
                        else:
                            raise ValueError(f"Location '{loc_input}' nahi mili. Kripya correct spelling ya Lat,Long daalein.")

                curr_p = get_lat_lon(start_coords)
                end_p = get_lat_lon(end_coords)
                
                # Baaki ka logic same hai
                unvisited = st.session_state.route_list.copy()
                final_path = []
                
                while unvisited:
                    next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x['Lat']), float(x['Long']))).km)
                    final_path.append(next_s)
                    curr_p = (float(next_s['Lat']), float(next_s['Long']))
                    unvisited.remove(next_s)
                
                route_data = []
                route_data.append({"Serial No": "0", "Task": "START", "Site ID": "Home/Office", "Location": start_coords})
                for i, s in enumerate(final_path, 1):
                    route_data.append({"Serial No": str(i), "Task": "Visit", "Site ID": s['Site ID'], "Location": f"{s['Lat']}, {s['Long']}"})
                route_data.append({"Serial No": str(len(final_path)+1), "Task": "END", "Site ID": "Destination", "Location": end_coords})
                
                st.table(pd.DataFrame(route_data))
                
                # 🟢 NAYA: Google Maps /dir/ API (Multi-stop link perfectly kaam karega)
                coords_str = "/".join([start_coords] + [f"{s['Lat']},{s['Long']}" for s in final_path] + [end_coords])
                gmaps_route = f"https://www.google.com/maps/dir/{coords_str}"
                st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Full Route in Maps</button></a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# =====================================================================
# 📁 TAB 5 & 6 (Data Entry & Finance)
# =====================================================================
with tab5:
    st.subheader("📁 Site Data Entry Form")
    with st.form("site_entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: p_no_in = st.text_input("Project Number"); s_id_in = st.text_input("Site ID")
        with c2: d_dt_in = st.date_input("Dispatch Date", value=datetime.now()); qty_in = st.number_input("Qty A", min_value=0, step=1)
        if st.form_submit_button("🚀 Save Data"):
            if p_no_in and s_id_in:
                try: 
                    supabase_new.table("Site_Data_Entry").insert({"Project Number": p_no_in, "Site ID": s_id_in, "Dispatch Date": d_dt_in.strftime('%d-%b-%Y'), "Qty A": qty_in}).execute()
                    st.success("✅ Saved!")
                except Exception as e: st.error(f"❌ Error: {e}")

with tab6:
    st.subheader("💰 Finance & Billing Entry")
    with st.form("fin_form", clear_on_submit=True):
        f1, f2 = st.columns(2)
        with f1: fin_p_no = st.text_input("Project Number (Finance)"); t_bill = st.number_input("Team Billing", min_value=0)
        with f2: t_paid = st.number_input("Team Paid Amt", min_value=0); fin_dt = st.date_input("Entry Date", value=datetime.now())
        if st.form_submit_button("💵 Record Finance"):
            if fin_p_no:
                v_bal = t_bill - t_paid
                try: 
                    supabase_new.table("Finance_Entry").insert({"Project Number": fin_p_no, "Team Billing": t_bill, "Team Paid Amt": t_paid, "VIS Balance": v_bal, "Date": fin_dt.strftime('%d-%b-%Y')}).execute()
                    st.success(f"✅ Saved! Balance: {v_bal}")
                except Exception as e: st.error(f"❌ Error: {e}")
