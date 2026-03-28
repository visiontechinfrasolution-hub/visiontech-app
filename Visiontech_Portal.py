import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import io
from geopy.distance import geodesic

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
# 🟩 TAB 1: BOQ REPORT (Existing Logic)
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
        with c7: submit_search = st.form_submit_button("🔍 Search")
    
    if submit_search:
        # (Existing BOQ logic - unchanged)
        pass

# =====================================================================
# 🧾 TAB 2: PO REPORT (Existing Logic)
# =====================================================================
with tab2:
    # (Existing PO logic - unchanged)
    pass

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
            row_in = res_ind.data[0] # Pehla result le rahe hain vertical detail ke liye

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
                
                # --- LAT/LONG SECTION WITH DIRECTION BUTTON ---
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
        with c1: start_coords = st.text_input("🏠 Start Location (Lat, Long)", placeholder="e.g. 18.52, 73.85")
        with c2: end_coords = st.text_input("🏁 End Location (Lat, Long)", placeholder="e.g. 19.07, 72.87")
        
        st.write("---")
        add_sid = st.text_input("📍 Add Indus Site ID")
        if st.button("➕ Add +"):
            if add_sid:
                s_res = supabase.table("Indus Data").select("Site ID", "Lat", "Long").ilike("Site ID", f"%{add_sid.strip()}%").execute()
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
                curr_p = [float(x.strip()) for x in start_coords.split(',')]
                end_p = [float(x.strip()) for x in end_coords.split(',')]
                
                unvisited = st.session_state.route_list.copy()
                final_path = []
                
                # Optimized logic: Nearest Neighbor
                while unvisited:
                    next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x['Lat']), float(x['Long']))).km)
                    final_path.append(next_s)
                    curr_p = (float(next_s['Lat']), float(next_s['Long']))
                    unvisited.remove(next_s)
                
                # Display Sequence Table
                route_data = []
                route_data.append({"Serial No": "0", "Task": "START", "Site ID": "Home/Office", "Location": start_coords})
                for i, s in enumerate(final_path, 1):
                    route_data.append({"Serial No": str(i), "Task": "Visit", "Site ID": s['Site ID'], "Location": f"{s['Lat']}, {s['Long']}"})
                route_data.append({"Serial No": str(len(final_path)+1), "Task": "END", "Site ID": "Destination", "Location": end_coords})
                
                st.table(pd.DataFrame(route_data))
                
                # Google Maps Multi-stop link
                coords_str = "/".join([start_coords] + [f"{s['Lat']},{s['Long']}" for s in final_path] + [end_coords])
                gmaps_route = f"https://www.google.com/maps?q=lat,long{coords_str}"
                st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Full Route in Maps</button></a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: Ensure Lat/Long format is '18.52, 73.85'. Detail: {e}")
# =====================================================================
# 📁 TAB 5 & 6 (Data Entry & Finance)
# =====================================================================
with tab5:
    # (Existing Data Entry logic - unchanged)
    pass

with tab6:
    # (Existing Finance logic - unchanged)
    pass
