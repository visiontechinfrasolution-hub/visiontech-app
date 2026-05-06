import streamlit as st
import pandas as pd
import urllib.parse
import time
from geopy.distance import geodesic
from supabase import create_client

# --- SUPABASE CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- BACK BUTTON ---
st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
if st.button("⬅️ Dashboard"):
    st.switch_page("Visiontech_Portal.py")
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# =====================================================================
# 📊 TAB 4: INDUS BASIC DATA (0% LOGIC CHANGE)
# =====================================================================
st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)

with st.form("ind_form_v5"):
    i1, i2, i3 = st.columns(3)
    with i1: in_id = st.text_input("📍 Site ID Search")
    with i2: in_nm = st.text_input("🏢 Site Name Search")
    with i3: st.write(""); sub_ind = st.form_submit_button("🔍 Search Indus")
    
if sub_ind:
    res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
    if res_ind.data:
        # Step 1: Create DataFrame
        df_ind = pd.DataFrame(res_ind.data)
        st.dataframe(df_ind, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("📌 Vertical Site Details")
        
        # Step 2: Extract values using column names directly from the DataFrame 
        row_data = df_ind.iloc[0]
        
        base_lat, base_lon = 18.6233, 74.0312
        
        try:
            site_lat = float(row_data['Lat'])
            site_lon = float(row_data['Long'])
        except:
            site_lat, site_lon = 0.0, 0.0

        dist_km = "-"
        if site_lat != 0.0:
            try:
                dist_km = f"{geodesic((base_lat, base_lon), (site_lat, site_lon)).km:.2f} KM"
            except: pass
        
        def call_html(label, name, num):
            if num and str(num).strip() not in ['-', '', 'None', 'nan']:
                return f'{label}: **{name}** ({num}) <a href="tel:{num}"><button style="background-color:#007bff;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;">📞 Call</button></a>'
            return f'{label}: **{name}** (-)'
        
        v1, v2 = st.columns(2)
        with v1:
            st.markdown(f"🛰️ **Area Name** :- {row_data.get('Area Name','-')}")
            st.markdown(call_html("👨‍🔧 **Tech Name**", row_data.get('Tech Name','-'), row_data.get('Tech Number','-')), unsafe_allow_html=True)
            st.markdown(call_html("👷 **FSE**", row_data.get('FSE','-'), row_data.get('FSE Number','-')), unsafe_allow_html=True)
        with v2:
            st.markdown(f"📏 **Aerial Distance** :- **{dist_km}**")
            st.markdown(call_html("👨‍💼 **AOM Name**", row_data.get('AOM Name','-'), row_data.get('AOM Number','-')), unsafe_allow_html=True)
            
            if site_lat != 0.0:
                maps_url = f"https://www.google.com/maps/dir/{base_lat},{base_lon}/{site_lat},{site_lon}"
                st.markdown(f"📍 **Lat/Long** :- {site_lat} / {site_lon} <a href='{maps_url}' target='_blank'><button style='background-color:#EA4335;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;'>📍 Direction</button></a>", unsafe_allow_html=True)
            else: 
                st.markdown(f"📍 **Lat/Long** :- {site_lat} / {site_lon}")
        
        msg_body = (
            f"*Namaskar,*\n\n"
            f"➡️ *Site Name* :- {row_data.get('Site Name','-')}\n"
            f"➡️ *Site ID* :- {row_data.get('Site ID','-')}\n"
            f"➡️ *District* :- {row_data.get('District','-')}\n"
            f"➡️ *Cluster* :- {row_data.get('Area Name','-')}\n\n"
            f"👨‍🔧 *Technician* :- {row_data.get('Tech Name','-')} ({row_data.get('Tech Number','-')})\n"
            f"👷 *FSE* :- {row_data.get('FSE','-')} ({row_data.get('FSE Number','-')})\n"
            f"👨‍💼 *AOM* :- {row_data.get('AOM Name','-')} ({row_data.get('AOM Number','-')})\n\n"
            f"📍 *Lat Long* :- {site_lat} / {site_lon}\n\n"
            f"🛣️ *Site Location* :- https://www.google.com/maps/dir/{base_lat},{base_lon}/{site_lat},{site_lon}\n\n"
            f"🚩 Thanks,\n"
            f"*Visiontech AI Team*"
        )
        
        wa_encoded = urllib.parse.quote(msg_body)
        st.link_button("🚀 Send to WhatsApp Desktop App", f"whatsapp://send?text={wa_encoded}", use_container_width=True)
    else: st.info("No Indus data found.")

st.divider()
st.subheader("🧭 Route Plan")
if 'route_list' not in st.session_state: st.session_state.route_list = []

with st.expander("🛠️ Add Sites to Route", expanded=True):
    c1, c2 = st.columns(2)
    with c1: start_coords = st.text_input("🏠 Start Location", value="Lonikand, Pune")
    with c2: end_coords = st.text_input("🏁 End Location (Optional)", placeholder="e.g. Mumbai")
    
    with st.form("add_site_form", clear_on_submit=True):
        add_sid = st.text_input("📍 Add Indus Site ID")
        if st.form_submit_button("➕ Add to List"):
            if add_sid:
                s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                if s_res.data: 
                    new_site = s_res.data[0]
                    new_site['Select'] = False # Default checkbox value
                    st.session_state.route_list.append(new_site)
                    st.success(f"Site {add_sid} added!")
                    st.rerun()
                else: st.error("Site ID not found!")

    if st.session_state.route_list:
        st.write("### 📋 Added Sites:")
        
        # DataFrame banate waqt ensure karein ki 'Select' column hamesha ho
        df_route = pd.DataFrame(st.session_state.route_list)
        if 'Select' not in df_route.columns:
            df_route.insert(0, 'Select', False)
        
        # Error fix: Column names ko directly fetch karna filter karne se pehle
        target_cols = ['Select', 'Site ID', 'Site Name', 'Lat', 'Long']
        valid_cols = [c for c in target_cols if c in df_route.columns]

        edited_df = st.data_editor(
            df_route[valid_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", default=False),
                "Site ID": st.column_config.TextColumn(disabled=True),
                "Site Name": st.column_config.TextColumn(disabled=True),
                "Lat": st.column_config.NumberColumn(disabled=True),
                "Long": st.column_config.NumberColumn(disabled=True),
            },
            key="route_editor_v1"
        )

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("🗑️ Delete Selected", use_container_width=True):
                # Selected sites ko filter out karke route_list update karna
                st.session_state.route_list = edited_df[edited_df['Select'] == False].to_dict('records')
                st.rerun()
        with col_act2:
            if st.button("🧹 Clear All", use_container_width=True):
                st.session_state.route_list = []
                st.rerun()

if st.button("🚀 Calculate Best Route (Point-wise)", use_container_width=True):
    if not start_coords or not st.session_state.route_list: 
        st.warning("Please add Start Location and at least one Site!")
    else:
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="vis_route_planner")
            def get_lat_lon(loc):
                if not loc: return None
                if ',' in loc and any(c.isdigit() for c in loc): return [float(x.strip()) for x in loc.split(',')]
                l = geolocator.geocode(loc); return [l.latitude, l.longitude] if l else None
            
            curr_p = get_lat_lon(start_coords)
            end_p = get_lat_lon(end_coords) if end_coords else None
            
            if not curr_p: st.error("Invalid Start Location.")
            else:
                unvisited = [s for s in st.session_state.route_list]
                final_path = []
                while unvisited:
                    next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x.get('Lat',0)), float(x.get('Long',0)))).km)
                    final_path.append(next_s)
                    curr_p = (float(next_s.get('Lat',0)), float(next_s.get('Long',0)))
                    unvisited.remove(next_s)
                
                route_results = []
                for i, s in enumerate(final_path, 1):
                    route_results.append({"Stop No": i, "Site ID": s['Site ID'], "Name": s.get('Site Name','-')})
                st.table(pd.DataFrame(route_results))
                
                stops_str = "/".join([f"{s.get('Lat')},{s.get('Long')}" for s in final_path])
                
                if end_coords:
                    gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops_str}/{end_coords}"
                else:
                    gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops_str}"
                
                st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Sequential Route (1-2-3-4)</button></a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"Error: {e}")
