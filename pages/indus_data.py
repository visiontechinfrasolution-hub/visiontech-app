import streamlit as st
import pandas as pd
import urllib.parse
import time  # Unique ID ke liye
from geopy.distance import geodesic
from supabase import create_client

# ... (Apka baaki connection aur setup code same rahega) ...

st.divider()
st.subheader("🧭 Route Plan")

# session_state list ko track karne ke liye
if 'route_list' not in st.session_state: 
    st.session_state.route_list = []

with st.expander("🛠️ Add Sites to Route", expanded=True):
    c1, c2 = st.columns(2)
    with c1: 
        start_coords = st.text_input("🏠 Start Location", value="Lonikand, Pune")
    with c2: 
        # CHANGE 1: End Location placeholder change (ab ye compulsory nahi lagega logic mein)
        end_coords = st.text_input("🏁 End Location (Optional)", placeholder="e.g. Mumbai")
    
    with st.form("add_site_form", clear_on_submit=True):
        add_sid = st.text_input("📍 Add Indus Site ID")
        if st.form_submit_button("➕ Add to List"):
            if add_sid:
                s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                if s_res.data: 
                    site_to_add = s_res.data[0]
                    # Unique ID add kar rahe hain taaki delete karne mein asani ho
                    site_to_add['unique_id'] = time.time()
                    st.session_state.route_list.append(site_to_add)
                    st.success(f"Site {add_sid} added!")
                    st.rerun()
                else: 
                    st.error("Site ID not found!")

    # CHANGE 2: Individual Site Delete Option with Checkboxes
    if st.session_state.route_list:
        st.write("### 📋 Added Sites:")
        
        # DataFrame display for visual clarity
        temp_df = pd.DataFrame(st.session_state.route_list)[['Site ID', 'Site Name', 'Lat', 'Long']]
        st.dataframe(temp_df, use_container_width=True, hide_index=True)

        # Delete logic using checkboxes
        with st.container():
            st.write("Select sites to remove:")
            to_delete = []
            for idx, site in enumerate(st.session_state.route_list):
                if st.checkbox(f"Remove: {site['Site ID']} ({site.get('Site Name','-')})", key=f"del_{site['unique_id']}"):
                    to_delete.append(idx)
            
            col_del1, col_del2 = st.columns(2)
            with col_del1:
                if st.button("🗑️ Delete Selected", use_container_width=True) and to_delete:
                    # Reverse order mein delete kar rahe hain taaki index shift na ho
                    for index in sorted(to_delete, reverse=True):
                        st.session_state.route_list.pop(index)
                    st.rerun()
            with col_del2:
                if st.button("🧹 Clear All", use_container_width=True):
                    st.session_state.route_list = []
                    st.rerun()

if st.button("🚀 Calculate Best Route (Point-wise)", use_container_width=True):
    # CHANGE 1 logic: Ab sirf Start aur Route List check karega
    if not start_coords or not st.session_state.route_list: 
        st.warning("Please add Start Location and at least one Site!")
    else:
        try:
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="vis_route_planner")
            
            def get_lat_lon(loc):
                if not loc: return None
                if ',' in loc and any(c.isdigit() for c in loc): 
                    return [float(x.strip()) for x in loc.split(',')]
                l = geolocator.geocode(loc)
                return [l.latitude, l.longitude] if l else None
            
            curr_p = get_lat_lon(start_coords)
            # End point optional hai
            end_p = get_lat_lon(end_coords) if end_coords else None
            
            if not curr_p: 
                st.error("Invalid Start Location.")
            else:
                unvisited = [s for s in st.session_state.route_list]
                final_path = []
                
                # Nearest Neighbor Logic
                while unvisited:
                    next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x.get('Lat',0)), float(x.get('Long',0)))).km)
                    final_path.append(next_s)
                    curr_p = (float(next_s.get('Lat',0)), float(next_s.get('Long',0)))
                    unvisited.remove(next_s)
                
                # Result Table
                route_results = []
                for i, s in enumerate(final_path, 1):
                    route_results.append({"Stop No": i, "Site ID": s['Site ID'], "Name": s.get('Site Name','-')})
                st.table(pd.DataFrame(route_results))
                
                # Google Maps Link Generation
                stops_str = "/".join([f"{s.get('Lat')},{s.get('Long')}" for s in final_path])
                
                # Agar end_coords hai toh include karo, varna last site tak rakho
                if end_coords:
                    gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops_str}/{end_coords}"
                else:
                    gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops_str}"
                
                st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Sequential Route (1-2-3-4)</button></a>', unsafe_allow_html=True)
        except Exception as e: 
            st.error(f"Error: {e}")
