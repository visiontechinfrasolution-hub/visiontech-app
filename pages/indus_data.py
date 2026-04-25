import streamlit as st
import pandas as pd
import urllib.parse
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
        df_ind = pd.DataFrame(res_ind.data)
        st.dataframe(df_ind, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("📌 Vertical Site Details")
        row_in = res_ind.data[0]
        
        base_lat, base_lon = 18.6233, 74.0312
        site_lat = row_in.get('Lat')
        site_lon = row_in.get('Long')
        dist_km = "-"
        if site_lat and site_lon:
            try:
                dist_km = f"{geodesic((base_lat, base_lon), (float(site_lat), float(site_lon))).km:.2f} KM"
            except: pass
        
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
            st.markdown(f"📏 **Aerial Distance** :- **{dist_km}**")
            st.markdown(call_html("👨‍💼 **AOM Name**", row_in.get('AOM Name','-'), row_in.get('AOM Number','-')), unsafe_allow_html=True)
            lat, lon = row_in.get('Lat', ''), row_in.get('Long', '')
            if lat and lon and str(lat).strip() not in ['-', '', 'None', 'nan']:
                maps_url = f"https://www.google.com/maps/dir/{base_lat},{base_lon}/{lat},{lon}"
                st.markdown(f"📍 **Lat/Long** :- {lat} / {lon} <a href='{maps_url}' target='_blank'><button style='background-color:#EA4335;color:white;border:none;padding:2px 10px;border-radius:5px;cursor:pointer;font-weight:bold;'>📍 Direction</button></a>", unsafe_allow_html=True)
            else: st.markdown(f"📍 **Lat/Long** :- {lat if lat else '-'} / {lon if lon else '-'}")
        
        maps_dir = f"https://www.google.com/maps/dir/{base_lat},{base_lon}/{lat},{lon}"
        msg_body = f"*{row_in.get('Site ID','-')}*\n*{row_in.get('Project ID','-')}*\n*{row_in.get('Site Name','-')}*\n\n👨‍🔧 Tech: {row_in.get('Tech Name','-')} ({row_in.get('Tech Number','-')})\n📍 Lat/Long: {lat}/{lon}\n\n🗺️ Map:\n{maps_dir}"
        wa_encoded = urllib.parse.quote(msg_body)
        st.link_button("🚀 Send to WhatsApp Desktop App", f"whatsapp://send?text={wa_encoded}", use_container_width=True)
    else: st.info("No Indus data found.")

st.divider()
st.subheader("🧭 Route Plan")
if 'route_list' not in st.session_state: st.session_state.route_list = []

with st.expander("🛠️ Add Sites to Route", expanded=True):
    c1, c2 = st.columns(2)
    with c1: start_coords = st.text_input("🏠 Start Location", value="Lonikand, Pune")
    with c2: end_coords = st.text_input("🏁 End Location", placeholder="e.g. Mumbai")
    
    with st.form("add_site_form", clear_on_submit=True):
        add_sid = st.text_input("📍 Add Indus Site ID")
        if st.form_submit_button("➕ Add to List"):
            if add_sid:
                s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                if s_res.data: 
                    st.session_state.route_list.append(s_res.data[0])
                    st.success(f"Site {add_sid} added!")
                    st.rerun()
                else: st.error("Site ID not found!")

    # --- Current Added Sites List (Visible before calculation) ---
    if st.session_state.route_list:
        st.write("### 📋 Added Sites:")
        temp_df = pd.DataFrame(st.session_state.route_list)[['Site ID', 'Site Name', 'Lat', 'Long']]
        st.dataframe(temp_df, use_container_width=True, hide_index=True)
        if st.button("🗑️ Clear All Sites", use_container_width=True):
            st.session_state.route_list = []
            st.rerun()

if st.button("🚀 Calculate Best Route (Point-wise)", use_container_width=True):
    if not start_coords or not end_coords or not st.session_state.route_list: 
        st.warning("Please add Start, End and at least one Site!")
    else:
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="vis_route_planner")
            def get_lat_lon(loc):
                if ',' in loc and any(c.isdigit() for c in loc): return [float(x.strip()) for x in loc.split(',')]
                l = geolocator.geocode(loc); return [l.latitude, l.longitude] if l else None
            
            curr_p, end_p = get_lat_lon(start_coords), get_lat_lon(end_coords)
            if not curr_p or not end_p: st.error("Invalid Start or End Location.")
            else:
                unvisited = [s for s in st.session_state.route_list if s.get('Lat') and s.get('Long')]
                final_path = []
                while unvisited:
                    next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x['Lat']), float(x['Long']))).km)
                    final_path.append(next_s)
                    curr_p = (float(next_s['Lat']), float(next_s['Long']))
                    unvisited.remove(next_s)
                
                # Showing Sequential Table
                route_results = []
                for i, s in enumerate(final_path, 1):
                    route_results.append({"Stop No": i, "Site ID": s['Site ID'], "Name": s.get('Site Name','-')})
                st.table(pd.DataFrame(route_results))
                
                # Point-wise Google Maps Link
                stops = "/".join([f"{s['Lat']},{s['Long']}" for s in final_path])
                gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops}/{end_coords}"
                st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Sequential Route (1-2-3-4)</button></a>', unsafe_allow_html=True)
        except Exception as e: st.error(f"Error: {e}")
