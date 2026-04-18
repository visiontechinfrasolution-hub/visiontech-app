import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import json
import time
import io
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 1.A EMAIL FUNCTION (With Full Signature & Body) ---
def send_professional_email(selected_df, to_emails, cc_emails):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from datetime import datetime, timedelta

    SENDER = "vispltower@gmail.com" 
    PWD = "llzg bjkq dyig rykv" 
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%b-%Y')
    
    msg = MIMEMultipart()
    msg['Subject'] = f"Audit Request_Visiontech_({tomorrow})"
    msg['From'] = f"Visiontech Portal <{SENDER}>"
    msg['To'] = to_emails
    msg['Cc'] = cc_emails

    header_style = "background-color: #FFFF00; font-weight: bold; border: 1px solid black; padding: 4px; font-size: 10px; text-align: center; color: black;"
    td_style = "border: 1px solid black; padding: 4px; font-size: 10px; text-align: center;"

    cols = [
        "Circle", "Ref. No.", "Indus ID", "Site Name", "Site Add", "Cluster / Zone",
        "Date of Offerance in ISQ", "Date Of Audit Planned in ISQ", "ISQ Offerance Status(Y/N)",
        "Documents uploaded in ISQ(Y/N)", "TSP Shared Filled checklist during Offerance for audit (Yes / No)",
        "TSP Shared Compliance Photographs during audit Offerance (yes / No)", "Project", "Tower Type",
        "Tower Ht.", "Stage", "TSP Name", "Audit Agency Name", "Representative Name",
        "Representative Contact Number", "Actual ofference date", "Audit Engineer Name",
        "Contact Details.", "Actual Audit date", "Actual Audit Time", "Lat", "Long"
    ]

    h_html = "".join([f"<th style='{header_style}'>{c}</th>" for c in cols])
    r_html = ""
    for _, row in selected_df.iterrows():
        r_html += "<tr>"
        for col in cols:
            val = row.get(col, "-")
            r_html += f"<td style='{td_style}'>{val}</td>"
        r_html += "</tr>"

    body = f"""
    <html>
    <body style="font-family: Calibri, Arial; font-size: 11px;">
        <p>Hello Sir,</p>
        <p>Please find the audit request for the following sites attached in the table below:</p>
        <div style="overflow-x: auto;">
            <table border="1" style="border-collapse: collapse; width: 100%; border: 1px solid black;">
                <thead><tr style="background-color: #FFFF00;">{h_html}</tr></thead>
                <tbody>{r_html}</tbody>
            </table>
        </div>
        <br>
        <p>Thanks & Regards,<br>
        <b>Saira Quzi</b><br>
        Mobile: +91 8180827123<br>
        Visiontech Infra Solution</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER, PWD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        import streamlit as st
        st.error(f"Gmail Error: {e}")
        return False

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide", initial_sidebar_state="collapsed")

# --- 3. CUSTOM CSS FOR MOBILE APP LOOK ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stApp { background-color: #F8FAFC; }
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 20px; border: none;
        background-color: white; color: #1E293B; font-size: 18px; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px;
        display: flex; flex-direction: column; justify-content: center;
        white-space: pre-wrap; transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: translateY(-5px); background-color: #1E3A8A; color: white;
    }
    .back-btn button {
        height: 50px !important; width: 160px !important;
        background-color: #64748B !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Navigation Control
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- MAIN DASHBOARD ---
if st.session_state.current_page == "Dashboard":
    # 👉 मोबाईलवर २ बटन्स एका लाईनमध्ये येण्यासाठी फक्त इथे CSS ॲड केली आहे
    st.markdown("""
        <style>
        @media (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
                justify-content: center !important;
            }
            div[data-testid="column"] {
                min-width: 48% !important;
                max-width: 48% !important;
                padding: 0 5px !important;
            }
            /* लॅपटॉपची रिकामी जागा (Spacers) मोबाईलवर लपवणे */
            div[data-testid="column"]:nth-child(1), 
            div[data-testid="column"]:nth-child(5) {
                display: none !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🚀 Visiontech Portal</h1>", unsafe_allow_html=True)
    
    # बटन्सना लॅपटॉपवर जवळ आणण्यासाठी आजूबाजूला 1.5 ची रिकामी जागा (spacer) जोडली आहे
    spacer1, c1, c2, c3, spacer2 = st.columns([1.5, 2, 2, 2, 1.5])
    
    with c1:
        if st.button("📦\nBOQ Report"): navigate_to("BOQ")
        if st.button("📊\nIndus Data"): navigate_to("Indus")
        if st.button("💰\nFinance"): navigate_to("Finance")
    with c2:
        if st.button("🧾\nPO Report"): navigate_to("PO")
        if st.button("📡\nWCC Tracker"): navigate_to("WCC")
        if st.button("📝\nAudit Portal"): navigate_to("Audit")
    with c3:
        if st.button("🏗️\nSite Detail"): navigate_to("Site")
        if st.button("📁\nData Entry"): navigate_to("Data")
        if st.button("📢\nRFAI Billing"): navigate_to("RFAI")
        if st.button("📄\nJMS Generator"): navigate_to("JMS")

# --- PAGES LOGIC ---
elif st.session_state.current_page != "Dashboard": # लाईन १७० वर 'else' काढून हे टाकले आहे
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"):
        navigate_to("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

# =====================================================================
    # 🟩 TAB 1: BOQ REPORT (3 Dedicated Sections - 0% Logic Change)
    # =====================================================================
    if st.session_state.current_page == "BOQ":
        import io
        import random
        from datetime import datetime, timedelta

        st.markdown("""
            <style>
                [data-testid="stDataFrame"] { border: 2px solid #1E3A8A; border-radius: 12px; }
                div.stButton > button:first-child {
                    height: 60px !important; font-size: 20px !important; font-weight: bold !important;
                    background-color: #1E3A8A !important; color: white !important; border-radius: 12px !important;
                    width: 100% !important;
                }
                .table-header { 
                    background-color: #1E3A8A; color: white; padding: 10px; border-radius: 8px; 
                    margin-top: 25px; text-align: center; font-weight: bold; 
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔍 Visiontech Infra Solutions</h2>", unsafe_allow_html=True)
        
        mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

        # --- ०. तुमचे मूळ फंक्शन्स (०% बदल) ---
        def process_boq_data(raw_data):
            if not raw_data: return pd.DataFrame()
            df_res = pd.DataFrame(raw_data)
            df_res.columns = [str(c).strip() for c in df_res.columns]
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df_res.columns:
                    df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0).astype(int)
            if 'Item Code' in df_res.columns and 'Project Number' in df_res.columns:
                df_res['TempKey'] = df_res.apply(lambda x: x.get('Sr. No.', random.random()) if str(x.get('Item Code','')).strip() == '' else x['Item Code'], axis=1)
                agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['Project Number', 'TempKey']}
                df_res = df_res.groupby(['Project Number', 'TempKey'], as_index=False).agg(agg_dict)
            for col in ['Dispatch Date', 'BOQ Date']:
                if col in df_res.columns:
                    df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
            return df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')

        def fetch_complete_data(query_builder):
            all_records = []
            page_size = 1000 
            offset = 0
            while True:
                response = query_builder.range(offset, offset + page_size - 1).execute()
                batch = response.data
                if not batch: break
                all_records.extend(batch)
                if len(batch) < page_size: break
                offset += page_size
            return all_records

        # --- १. तुमच्या मागणीनुसार ३ मुख्य पेजेस (Tabs) ---
        t1, t2, t3 = st.tabs([
            "🔎 Single Site Search", 
            "📅 Date Range Reports", 
            "📤 Bulk Project Upload"
        ])

        # --- PAGE 1: Single Site / Project Search ---
        with t1:
            with st.form("search_form_v27", clear_on_submit=False):
                st.markdown("#### 🔎 Single Site / Project Search")
                c1, c2, c3 = st.columns(3)
                with c1: project_query = st.text_input("📁 Project Number", key="boq_p_v27")
                with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v27")
                with c3: boq_query = st.text_input("📄 BOQ Number", key="boq_b_v27")
                submit_search = st.form_submit_button("🔍 SEARCH SINGLE DATA")

            if submit_search:
                st.balloons()
                with st.spinner('शोधत आहे...'):
                    query = supabase.table("BOQ Report").select("*")
                    if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
                    if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
                    if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
                    data = fetch_complete_data(query)
                    df_final = process_boq_data(data)
                    if not df_final.empty:
                        st.success(f"✅ {len(df_final)} Records Found!")
                        st.dataframe(df_final[[c for c in mera_sequence if c in df_final.columns]], use_container_width=True, hide_index=True)
                    else: st.warning("कोणतीही माहिती सापडली नाही.")

        # --- PAGE 2: Date Range Dispatch Reports ---
        with t2:
            with st.form("date_range_filter_v27"):
                st.markdown("#### 📅 Date Range Dispatch Reports")
                c_from, c_to, c_btn = st.columns([1.5, 1.5, 1])
                with c_from: start_date = st.date_input("From Date", value=datetime.now().date(), key="d_from_v27")
                with c_to: end_date = st.date_input("To Date", value=datetime.now().date(), key="d_to_v27")
                with c_btn: btn_range_gen = st.form_submit_button("🚀 GENERATE DATA")

            if btn_range_gen:
                st.balloons()
                delta = end_date - start_date
                date_list = [(start_date + timedelta(days=i)).strftime('%d-%b-%Y') for i in range(delta.days + 1)]
                with st.spinner('डेटा फेच होत आहे...'):
                    try:
                        query = supabase.table("BOQ Report").select("*").in_('"Dispatch Date"', date_list)
                        data = fetch_complete_data(query)
                        if data:
                            df_processed = process_boq_data(data)
                            
                            # Table 1: Transporter
                            df_trans = df_processed[df_processed['Transporter'].astype(str).str.contains('Visiotech|Visiontech', case=False, na=False)]
                            st.markdown(f"<div class='table-header'>📦 Transporter Report</div>", unsafe_allow_html=True)
                            if not df_trans.empty:
                                buffer1 = io.BytesIO()
                                with pd.ExcelWriter(buffer1, engine='xlsxwriter') as writer:
                                    df_trans[[c for c in mera_sequence if c in df_trans.columns]].to_excel(writer, index=False)
                                st.download_button("📥 Download Transporter Excel", buffer1.getvalue(), f"Transporter_{start_date}_to_{end_date}.xlsx", key="dl_t1_p2")
                                st.dataframe(df_trans[[c for c in mera_sequence if c in df_trans.columns]], use_container_width=True, hide_index=True)

                            # Table 2: TSP Partner
                            df_tsp = df_processed[df_processed['TSP Partner Name'].astype(str).str.contains('Visiotech|Visiontech', case=False, na=False)]
                            st.markdown(f"<div class='table-header'>🏗️ TSP Partner Report</div>", unsafe_allow_html=True)
                            if not df_tsp.empty:
                                buffer2 = io.BytesIO()
                                with pd.ExcelWriter(buffer2, engine='xlsxwriter') as writer:
                                    df_tsp[[c for c in mera_sequence if c in df_tsp.columns]].to_excel(writer, index=False)
                                st.download_button("📥 Download TSP Excel", buffer2.getvalue(), f"TSP_{start_date}_to_{end_date}.xlsx", key="dl_t2_p2")
                                st.dataframe(df_tsp[[c for c in mera_sequence if c in df_tsp.columns]], use_container_width=True, hide_index=True)
                        else: st.error("डेटा सापडला नाही.")
                    except Exception as e: st.error(f"Error: {e}")

        # --- PAGE 3: Bulk Project ID Upload ---
        with t3:
            st.markdown("#### 📤 Bulk Project ID Upload (Excel/CSV)")
            st.info("'Project Number' नावाचा कॉलम असलेली फाईल अपलोड करा.")
            up_file = st.file_uploader("Upload File", type=['xlsx', 'csv'], key="bulk_up_v28")
            
            if up_file:
                try:
                    bulk_df = pd.read_excel(up_file, engine='openpyxl') if up_file.name.endswith('.xlsx') else pd.read_csv(up_file)
                    bulk_df.columns = [str(c).strip() for c in bulk_df.columns]
                    if 'Project Number' in bulk_df.columns:
                        p_list = bulk_df['Project Number'].astype(str).str.strip().unique().tolist()
                        
                        bc1, bc2 = st.columns(2)
                        with bc1: submit_bulk = st.button("🚀 SUBMIT & PROCESS", use_container_width=True, key="bulk_submit_p3")
                        with bc2: clear_bulk = st.button("🧹 CLEAR", use_container_width=True, key="bulk_clear_p3")

                        if clear_bulk: st.rerun()

                        if submit_bulk:
                            st.balloons()
                            with st.spinner(f'{len(p_list)} प्रोजेक्ट्स शोधत आहे...'):
                                query = supabase.table("BOQ Report").select("*").in_("Project Number", p_list)
                                data = fetch_complete_data(query) 
                                df_final = process_boq_data(data)
                                if not df_final.empty:
                                    output = io.BytesIO()
                                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                        df_final[[c for c in mera_sequence if c in df_final.columns]].to_excel(writer, index=False)
                                    st.download_button("📥 Download Bulk Excel", output.getvalue(), "Bulk_Report.xlsx")
                                    st.dataframe(df_final[[c for c in mera_sequence if c in df_final.columns]], use_container_width=True, hide_index=True)
                                else: st.warning("डेटा सापडला नाही.")
                    else: st.error("Project Number कॉलम सापडला नाही.")
                except Exception as e: st.error(f"Error: {e}. Check openpyxl.")
    # =====================================================================
    # 🧾 TAB 2: PO REPORT
    # =====================================================================
    elif st.session_state.current_page == "PO":
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
    elif st.session_state.current_page == "Site":
        st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
        with st.form("sd_form_v5"):
            site_id_sd = st.text_input("📍 Site ID Search")
            if st.form_submit_button("🔍 Search Detail"):
                res_sd = supabase.table("Site Data").select("*").ilike("SITE ID", f"%{site_id_sd}%").execute()
                if res_sd.data: st.write(res_sd.data)

# =====================================================================

    # 📊 TAB 4: INDUS BASIC DATA

    # =====================================================================

    elif st.session_state.current_page == "Indus":
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
                
                # WhatsApp Option for FE
                f_no = row_in.get('Tech Number', row_in.get('FE Number', ''))
                if f_no:
                    wa_msg = urllib.parse.quote(f"Hello, regarding Site ID: {row_in.get('Site ID')}")
                    st.markdown(f'<a href="https://wa.me/91{f_no}?text={wa_msg}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">💬 Message on WhatsApp</button></a>', unsafe_allow_html=True)
            else: st.info("No Indus data found.")

        st.divider()
        st.subheader("🧭 Route Plan")
        if 'route_list' not in st.session_state: st.session_state.route_list = []
        with st.expander("🛠️ Create New Route Plan", expanded=False):
            c1, c2 = st.columns(2)
            with c1: start_coords = st.text_input("🏠 Start Location", placeholder="e.g. Pune")
            with c2: end_coords = st.text_input("🏁 End Location", placeholder="e.g. Mumbai")
            with st.form("add_site_form", clear_on_submit=True):
                add_sid = st.text_input("📍 Add Indus Site ID")
                if st.form_submit_button("➕ Add +"):
                    if add_sid:
                        s_res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{add_sid.strip()}%").execute()
                        if s_res.data: 
                            st.session_state.route_list.append(s_res.data[0])
                            st.success(f"Site {add_sid} added!")
                        else: st.error("Site ID not found!")
            if st.session_state.route_list:
                st.write("**Current Sites:** " + ", ".join([s['Site ID'] for s in st.session_state.route_list]))
                if st.button("🗑️ Clear List"): st.session_state.route_list = []; st.rerun()
        
        if st.button("🚀 Calculate Best Route", use_container_width=True):
            if not start_coords or not end_coords or not st.session_state.route_list: st.warning("Incomplete details!")
            else:
                try:
                    from geopy.geocoders import Nominatim
                    from geopy.distance import geodesic
                    geolocator = Nominatim(user_agent="vis_route_planner")
                    def get_lat_lon(loc):
                        if ',' in loc and any(c.isdigit() for c in loc): return [float(x.strip()) for x in loc.split(',')]
                        l = geolocator.geocode(loc); return [l.latitude, l.longitude] if l else None
                    curr_p, end_p = get_lat_lon(start_coords), get_lat_lon(end_coords)
                    if not curr_p or not end_p: st.error("Check Start/End location.")
                    else:
                        unvisited = st.session_state.route_list.copy(); final_path = []
                        while unvisited:
                            next_s = min(unvisited, key=lambda x: geodesic(curr_p, (float(x['Lat']), float(x['Long']))).km)
                            final_path.append(next_s); curr_p = (float(next_s['Lat']), float(next_s['Long'])); unvisited.remove(next_s)
                        route_data = [{"Serial No": str(i), "Site ID": s['Site ID'], "Location": f"{s['Lat']}, {s['Long']}"} for i, s in enumerate(final_path, 1)]
                        st.table(pd.DataFrame(route_data))
                        coords_str = "/".join([start_coords] + [f"{s['Lat']},{s['Long']}" for s in final_path] + [end_coords])
                        gmaps_route = f"https://www.google.com/maps/dir/{coords_str}"
                        st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Full Route in Maps</button></a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

    # =====================================================================
    # 📡 TAB 5: WCC STATUS
    # =====================================================================
    elif st.session_state.current_page == "WCC":
        st.markdown("""
            <style>
                .site-badge { background-color: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px; border: 1px solid #BAE6FD; }
                .wa-btn { background-color: #25D366; color: white !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; }
                [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
            </style>
        """, unsafe_allow_html=True)

        def fetch_wcc_data_simple():
            try: 
                res = supabase.table("WCC Status").select("*").execute()
                return res.data
            except Exception as e:
                st.error(f"Fetch Error: {e}")
                return []

        def update_wcc_record(payload):
            try: 
                res = supabase.table("WCC Status").upsert(payload).execute()
                return res
            except Exception as e:
                st.error(f"SUPABASE ERROR: {str(e)}")
                return None

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
                        v_wno = st.text_input("WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                        v_rem = st.text_area("Remark", value=str(row_data.get("Remark", "")) if is_edit else "")
                    else:
                        v_pid = row_data.get('Project ID')
                        v_wno = st.text_input("Enter/Update WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                        v_rem = st.text_area("Remark", value=str(row_data.get("Remark", "")) if is_edit else "")
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        if not v_pid or v_pid.strip() == "":
                            st.warning("Project ID is mandatory!")
                        else:
                            def to_num(val):
                                val = str(val).strip()
                                return val if val != "" else None

                            payload = {
                                "Project ID": v_pid.strip(),
                                "WCC Number": to_num(v_wno),
                                "Remark": v_rem
                            }
                            if role == "requester": 
                                payload.update({
                                    "Project": v_proj, 
                                    "Site ID": v_sid, 
                                    "Site Name": v_snm, 
                                    "PO Number": to_num(v_po), 
                                    "Reqeust Date": str(v_dt), 
                                    "WCC Status": v_sts
                                })
                            
                            response = update_wcc_record(payload)
                            if response:
                                st.success("Data Saved!")
                                st.rerun()

            data_list = fetch_wcc_data_simple()
            df_wcc = pd.DataFrame(data_list)[::-1] if data_list else pd.DataFrame()
            
            c_top1, c_top2 = st.columns([1, 1])
            with c_top1:
                if role == "requester" and st.button("➕ Add New Site Request", type="primary"): wcc_edit_modal()
            with c_top2:
                if not df_wcc.empty:
                    excel_data = df_wcc.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Report", data=excel_data, file_name=f"WCC_Report.csv", mime="text/csv")

            # --- BULK UPDATE SECTION (STRICT FIX) ---
            with st.expander("🛠️ Bulk Update WCC & Remarks via Excel"):
                st.info("फक्त डाउनलोड केलेली फाईल वापरा (Project ID, PO Number, WCC Number, Remark)")
                uploaded_file = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"], key="bulk_up_v3")
                
                if uploaded_file:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            up_df = pd.read_csv(uploaded_file)
                        else:
                            up_df = pd.read_excel(uploaded_file)
                        
                        up_df.columns = [str(c).strip() for c in up_df.columns]
                        
                        if st.button("🆙 Start Update Process"):
                            success_count = 0
                            not_found_count = 0
                            
                            for _, up_row in up_df.iterrows():
                                # १. डेटा क्लीन करणे (Number ला String मध्ये व्यवस्थित रूपांतर करणे)
                                def get_clean_val(col_name):
                                    val = str(up_row.get(col_name, '')).strip()
                                    if val.endswith('.0'): val = val[:-2] # .0 काढणे
                                    return val if val not in ['nan', 'None', ''] else None

                                pid = get_clean_val('Project ID')
                                po_no = get_clean_val('PO Number')
                                wcc_no = get_clean_val('WCC Number')
                                remark = get_clean_val('Remark')

                                if pid and po_no:
                                    # २. डेटाबेसशी मॅचिंग (Case & Space Ignore करून)
                                    match = df_wcc[
                                        (df_wcc['Project ID'].astype(str).str.strip() == pid) & 
                                        (df_wcc['PO Number'].astype(str).str.strip() == po_no)
                                    ]
                                    
                                    if not match.empty:
                                        # ३. फक्त WCC Number आणि Remark अपडेट करणे
                                        payload = {
                                            "WCC Number": wcc_no, 
                                            "Remark": remark if remark else ""
                                        }
                                        try:
                                            # eq() मध्ये PID आणि PO दोन्ही वापरू जेणेकरून परफेक्ट अपडेट होईल
                                            supabase.table("WCC Status").update(payload).eq("Project ID", pid).eq("PO Number", po_no).execute()
                                            success_count += 1
                                        except Exception as e:
                                            st.error(f"Error for {pid}: {e}")
                                    else:
                                        not_found_count += 1
                            
                            if success_count > 0:
                                st.success(f"✅ {success_count} Records Updated!")
                                if not_found_count > 0:
                                    st.warning(f"⚠️ {not_found_count} matches not found.")
                                st.rerun()
                            else:
                                st.error("❌ No matches found! Excel मधले Project ID आणि PO Number डेटाबेसशी मॅच होत नाहीत.")
                                
                    except Exception as e:
                        st.error(f"❌ File Error: {e}")            
            st.divider()

            if not df_wcc.empty:
                h_cols = st.columns([1, 0.4, 0.8, 1.2, 0.8, 1, 0.8, 0.8, 1, 1])
                cols_names = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "WCC No", "Status", "Remark"]
                for col, name in zip(h_cols, cols_names):
                    col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:11px; text-align:center;'>{name}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0px; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

                for i, row in df_wcc.iterrows():
                    r_cols = st.columns([1, 0.4, 0.8, 1.2, 0.8, 1, 0.8, 0.8, 1, 1])
                    
                    raw_date = row.get('Reqeust Date', '')
                    try:
                        formatted_date = pd.to_datetime(raw_date).strftime('%d-%b-%Y') if raw_date and str(raw_date).lower() != 'none' else ""
                    except:
                        formatted_date = str(raw_date) if str(raw_date).lower() != 'none' else ""

                    def clean_none(val):
                        return str(val) if val and str(val).lower() != 'none' else ""

                    with r_cols[0]:
                        b1, b2 = st.columns(2)
                        if b1.button("✏️", key=f"edit_{row['Project ID']}_{i}"): wcc_edit_modal(row)
                        if role == 'requester':
                            msg = (
                                f"*Hello Prkash Ji,*\n"
                                f"Raise WCC urgently...\n\n"
                                f"*Project* :- {clean_none(row.get('Project'))}\n"
                                f"*Project ID* :- {clean_none(row.get('Project ID'))}\n"
                                f"*Site ID* :- {clean_none(row.get('Site ID'))}\n"
                                f"*Site Name* :- {clean_none(row.get('Site Name'))}\n"
                                f"*PO Number* :- {clean_none(row.get('PO Number'))}\n"
                                f"*Reqeust Date* :- {formatted_date}\n"
                                f"*WCC Number* :- {clean_none(row.get('WCC Number'))}\n"
                                f"*WCC Status* :- {clean_none(row.get('WCC Status'))}\n\n"
                                f"Thanks,\n"
                                f"*Mayur Patil*\n"
                                f"7350533473"
                            )
                            wa_url = f"whatsapp://send?text={urllib.parse.quote(msg)}"
                            b2.markdown(f'<a href="{wa_url}" class="wa-btn" style="text-align:center; display:block; text-decoration:none;">💬</a>', unsafe_allow_html=True)
                    
                    r_cols[1].markdown(f"<p style='font-size:11px; text-align:center;'>{i+1}</p>", unsafe_allow_html=True)
                    r_cols[2].markdown(f"<p style='font-size:11px; text-align:center;'>{clean_none(row.get('Project'))}</p>", unsafe_allow_html=True)
                    r_cols[3].markdown(f"<p style='font-size:11px; text-align:center; font-weight:bold;'>{clean_none(row.get('Project ID'))}</p>", unsafe_allow_html=True)
                    r_cols[4].markdown(f"<div style='text-align:center;'><span class='site-badge'>{clean_none(row.get('Site ID'))}</span></div>", unsafe_allow_html=True)
                    r_cols[5].markdown(f"<p style='font-size:11px; text-align:center;'>{clean_none(row.get('Site Name'))}</p>", unsafe_allow_html=True)
                    r_cols[6].markdown(f"<p style='font-size:11px; text-align:center;'>{clean_none(row.get('PO Number'))}</p>", unsafe_allow_html=True)
                    r_cols[7].markdown(f"<p style='font-size:11px; text-align:center; color:#0369A1; font-weight:bold;'>{clean_none(row.get('WCC Number'))}</p>", unsafe_allow_html=True)
                    r_cols[8].markdown(f"<p style='font-size:11px; text-align:center;'>{clean_none(row.get('WCC Status'))}</p>", unsafe_allow_html=True)
                    r_cols[9].markdown(f"<p style='font-size:10px; color:gray; text-align:center;'>{clean_none(row.get('Remark'))}</p>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin:1px 0px; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)

    elif st.session_state.current_page == "Data":
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
    # =====================================================================
    # 🏗️ TAB 6: DATA ENTRY (Document Center & Tracker) - FORCED DISPLAY
    # =====================================================================
    # 'in' keyword use kiya hai taaki agar sidebar mein emoji ya space ho toh bhi load ho jaye
    elif "Data" in str(st.session_state.current_page) or "Entry" in str(st.session_state.current_page):
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
        
        # Aapka Original 3-Tab Logic jo aapne bheja tha
        doc_sub1, doc_sub2, doc_sub3 = st.tabs(["📤 Manager Upload", "🔍 Team Search", "📊 Tracker"])
        
        with doc_sub1:
            with st.form("doc_upload_final_v1", clear_on_submit=True):
                col_u1, col_u2 = st.columns(2)
                u_proj = col_u1.text_input("📁 Project Number")
                u_indus = col_u2.text_input("📍 Indus ID")
                u_site = col_u1.text_input("🏢 Site Name")
                u_type = col_u2.selectbox("📄 Doc Type", ["Photo", "SRC", "DC", "STN", "REPORT", "OTHER"])
                u_files = st.file_uploader("Select Files", accept_multiple_files=True)
                
                if st.form_submit_button("🚀 Upload All Files"):
                    if u_files and u_proj:
                        try:
                            for i, f in enumerate(u_files):
                                clean_p = u_proj.replace("/", "-").strip()
                                fname = f"{clean_p}_{u_indus}_{u_type}_{i}.{f.name.split('.')[-1]}"
                                
                                # Supabase Storage Upload
                                supabase.storage.from_("site_documents").upload(
                                    path=fname, 
                                    file=f.getvalue(), 
                                    file_options={"x-upsert": "true"}
                                )
                                
                                # URL variable must be defined at the top of your file
                                p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                                
                                # Master Table Upsert
                                supabase.table("site_documents_master").upsert({
                                    "project_number": u_proj, 
                                    "indus_id": u_indus, 
                                    "site_name": u_site, 
                                    "doc_type": u_type, 
                                    "file_name": fname, 
                                    "file_url": p_url
                                }, on_conflict="file_name").execute()
                                
                            st.success("✅ Files Uploaded & Master Updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Upload Error: {e}")
                    else:
                        st.warning("⚠️ Files aur Project Number dalna zaroori hai!")

        with doc_sub2:
            q_s = st.text_input("🔍 Search Documents (Project, Indus, Site)")
            if q_s:
                res_db = supabase.table("site_documents_master").select("*").or_(
                    f"project_number.ilike.%{q_s}%,indus_id.ilike.%{q_s}%,site_name.ilike.%{q_s}%"
                ).execute()
                
                if res_db.data:
                    for row in res_db.data:
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(row['file_name'])
                        c2.info(row['doc_type'])
                        c3.markdown(f'[📥 View]({row["file_url"]})')
                        st.divider()

        with doc_sub3:
            try:
                res_t = supabase.table("site_documents_master").select("*").execute()
                if res_t.data:
                    df_t = pd.DataFrame(res_t.data)
                    site_groups = df_t.groupby('indus_id')
                    summary = []
                    for ind_id, gp in site_groups:
                        types = gp['doc_type'].str.upper().tolist()
                        summary.append({
                            "Project ID": gp.iloc[0]['project_number'], 
                            "Indus ID": ind_id, 
                            "Site Name": gp.iloc[0]['site_name'], 
                            "SRC": "✅" if "SRC" in types else "❌", 
                            "DC": "✅" if "DC" in types else "❌", 
                            "STN": "✅" if "STN" in types else "❌", 
                            "Report": "✅" if "REPORT" in types else "❌", 
                            "Photo": "✅" if "PHOTO" in types else "❌"
                        })
                    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
            except:
                st.info("Tracker data loading...")
    # =====================================================================
    # 💰 TAB 1: FINANCE ENTRY (Baaki code same rahega)
    # =====================================================================
    elif st.session_state.current_page == "Finance":
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
                            for col in df_r.columns: 
                                df_r[col] = df_r[col].astype(str).str.replace('"', '').str.strip()
                            
                            df_r['qty_tmp'] = df_r['Qty'].apply(clean_num_fixed)
                            df_r['amt_tmp'] = df_r['Amount'].apply(clean_num_fixed)
                            
                            df_cln = df_r[df_r['qty_tmp'] > 0].copy()
                            if not df_cln.empty:
                                supabase.table("po_line_items").delete().eq("po_number", str(u_po)).execute()
                                supabase.table("po_summaries").delete().eq("po_number", str(u_po)).execute()
                                
                                items = []
                                for _, r in df_cln.iterrows():
                                    items.append({
                                        "po_number": str(u_po), "line_no": str(r.get('Line', '')), "item_number": str(r.get('Item Num', '')), 
                                        "description": str(r.get('Description', '')), "uom": str(r.get('UOM', '')), 
                                        "qty": clean_num_fixed(r.get('Qty')), "price": clean_num_fixed(r.get('Price')), 
                                        "amount": clean_num_fixed(r.get('Amount')), "site_id": str(r.get('Site ID', '')), 
                                        "site_name": str(r.get('Site Name', '')), "project_name": str(r.get('Project Name', ''))
                                    })
                                supabase.table("po_line_items").insert(items).execute()
                                
                                df_cln['group_col'] = df_cln['Project Name'].replace('', None).fillna(df_cln['Site ID'])
                                sums = df_cln.groupby(['group_col', 'Site ID'])['amt_tmp'].sum().reset_index()
                                
                                summary_list = [
                                    {"po_number": str(u_po), "project_name": str(sr['group_col']), "site_id": str(sr['Site ID']), "total_amount": float(sr['amt_tmp'])} 
                                    for _, sr in sums.iterrows()
                                ]
                                supabase.table("po_summaries").insert(summary_list).execute()
                                st.success(f"✅ PO {u_po} Synced!")
                                st.rerun()
                    except Exception as e: st.error(f"❌ Error: {e}")

        if st.button("🗑️ Clear All Finance Data", use_container_width=True):
            supabase.table("po_line_items").delete().neq("po_number", "DATA_CLEANED").execute()
            supabase.table("po_summaries").delete().neq("po_number", "DATA_CLEANED").execute()
            st.rerun()

    # =====================================================================
    # 📝 TAB 8: AUDIT MANAGEMENT PORTAL
    # =====================================================================
    elif st.session_state.current_page == "Audit":
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Audit Management Portal</h3>", unsafe_allow_html=True)
        
        if 'audit_queue' not in st.session_state:
            st.session_state.audit_queue = []

        try:
            m_df = pd.DataFrame(supabase.table("VIS Portal Site Data").select('*').execute().data)
            u_df = pd.DataFrame(supabase.table("allowed_users").select("*").execute().data)
            h_df = pd.DataFrame(supabase.table("Audit Request").select("*").order("created_at", desc=True).execute().data)
            e_df = pd.DataFrame(supabase.table("Email Address").select("Email").execute().data)
        except: pass

        t1, t2 = st.tabs(["➕ Create Entry", "📜 History"])

        with t1:
            st.markdown("#### 📧 Email Configuration")
            c_em1, c_em2 = st.columns(2)
            db_emails = sorted(e_df["Email"].unique().tolist()) if not e_df.empty else []
            default_to = ["a-amit.patil@industowers.com"]
            default_cc = ["services@vispltower.com", "project.visiontechinfra@gmail.com", "vispltower@gmail.com", "visiontechinfrasolution@gmail.com"]
            for em in default_to + default_cc:
                if em not in db_emails: db_emails.append(em)

            sel_to = c_em1.multiselect("To:", db_emails, default=default_to, key="v22_to")
            sel_cc = c_em2.multiselect("Cc:", db_emails, default=default_cc, key="v22_cc")
            
            st.divider()

            c_top1, c_top2 = st.columns(2)
            p_ids = [""] + sorted(m_df["PROJECT ID"].unique().tolist()) if not m_df.empty else [""]
            sel_pid = c_top1.selectbox("🔍 Select Project ID", p_ids, key="v22_pid")
            user_names = [""] + sorted(u_df["name"].tolist()) if not u_df.empty else [""]
            sel_rep = c_top2.selectbox("👤 Select Representative", user_names, key="v22_rep")

            s_info, rep_mob, lat_val, long_val, linked_sid = {}, "", "", "", ""
            today_dt = datetime.now().strftime("%d-%b-%Y")
            tomorrow_dt = (datetime.now() + timedelta(days=1)).strftime("%d-%b-%Y")
            
            if sel_pid and not m_df.empty:
                s_info = m_df[m_df["PROJECT ID"] == sel_pid].iloc[0].to_dict()
                linked_sid = str(s_info.get("SITE ID", "")).strip()
                if linked_sid:
                    try:
                        res_coord = supabase.table("Indus_Coordinates").select("Lat", "Long").eq("Site ID", linked_sid).execute()
                        if res_coord.data:
                            match = res_coord.data[0]
                            lat_val, long_val = str(match.get("Lat", "")), str(match.get("Long", ""))
                    except: pass

            if sel_rep and not u_df.empty:
                match_u = u_df[u_df["name"].astype(str).str.strip() == str(sel_rep).strip()]
                if not match_u.empty: rep_mob = str(match_u.iloc[0].get('phone_number', ''))

            with st.form("v22_form"):
                col1, col2, col3 = st.columns(3)
                f = {}
                f["Circle"] = col1.text_input("Circle", value="Maharashtra")
                f["Ref. No."] = col1.text_input("Project ID", value=sel_pid)
                f["Indus ID"] = col2.text_input("Indus ID", value=linked_sid)
                f["Site Name"] = col2.text_input("Site Name", value=s_info.get("SITE NAME", ""))
                f["Site Add"] = col3.text_input("Site Add", value=s_info.get("CLUSTER", ""))
                f["Cluster / Zone"] = col3.text_input("Cluster / Zone", value=s_info.get("CLUSTER", ""))
                f["Date of Offerance in ISQ"] = col1.text_input("Offerance Date", value=today_dt)
                f["Date Of Audit Planned in ISQ"] = col2.text_input("Planned Audit Date", value=tomorrow_dt)
                f["ISQ Offerance Status(Y/N)"] = col3.selectbox("ISQ Offerance Status", ["Y", "N"])
                f["Project"] = col1.text_input("Project Name", value=s_info.get("PROJECT NAME", ""))
                f["Tower Type"] = col2.text_input("Tower Type", value="GBT")
                f["Tower Ht."] = col3.text_input("Tower Ht.", value="40 mtr")
                
                f["Documents uploaded in ISQ(Y/N)"] = col1.selectbox("Documents uploaded?", ["Y", "N"])
                f["TSP Shared Filled checklist during Offerance for audit (Yes / No)"] = col2.selectbox("Checklist Shared?", ["Yes", "No"])
                f["TSP Shared Compliance Photographs during audit Offerance (yes / No)"] = col3.selectbox("Photographs Shared?", ["yes", "No"])
                
                f["Representative Name"] = col1.text_input("Representative Name", value=sel_rep)
                f["Representative Contact Number"] = col2.text_input("Rep. Mobile", value=rep_mob)
                f["Actual ofference date"] = col3.text_input("Actual ofference date", value=today_dt)
                f["Lat"], f["Long"] = col1.text_input("Lat", value=lat_val), col2.text_input("Long", value=long_val)
                f["Actual Audit date"] = col3.text_input("Actual Audit date", value=tomorrow_dt)
                
                from datetime import time as time_dt
                audit_time_input = col1.time_input("Set Audit Time", value=time_dt(11, 0)) 
                f["Actual Audit Time"] = audit_time_input.strftime("%I:%M %p") 

                f["Stage"], f["Audit Agency Name"], f["TSP Name"] = "", "", "Visiontech"
                f["Audit Engineer Name"], f["Contact Details."], f["Mail Status"], f["Mail Sent Date"] = "", "", "Pending", "-"

                if st.form_submit_button("➕ Add Site to Queue"):
                    if sel_pid and f["Lat"]:
                        st.session_state.audit_queue.append(f.copy())
                        st.toast(f"✅ Added {linked_sid}")
                    else: st.error("Missing Data!")

            if st.session_state.audit_queue:
                st.divider()
                for i, item in enumerate(st.session_state.audit_queue):
                    q_col1, q_col2, q_col3, q_col4 = st.columns([3, 3, 2, 1])
                    q_col1.write(f"**ID:** {item['Indus ID']}")
                    q_col2.write(f"**Site:** {item['Site Name']}")
                    q_col3.write(f"**Time:** {item['Actual Audit Time']}")
                    if q_col4.button("❌", key=f"del_v22_{i}"):
                        st.session_state.audit_queue.pop(i)
                        st.rerun()

                if st.button("📧 Submit & Send Email", type="primary", use_container_width=True):
                    if not sel_to: st.error("Select 'To' email!")
                    else:
                        try:
                            res_schema = supabase.table("Audit Request").select("*").limit(1).execute()
                            db_cols = res_schema.data[0].keys() if res_schema.data else []
                            final_save = []
                            for item in st.session_state.audit_queue:
                                clean_item = {k: v for k, v in item.items() if k in db_cols and v != ""}
                                final_save.append(clean_item)

                            supabase.table("Audit Request").insert(final_save).execute()
                            
                            if send_professional_email(pd.DataFrame(st.session_state.audit_queue), ", ".join(sel_to), ", ".join(sel_cc)):
                                st.balloons()
                                st.success(f"🚀 Success! Email sent to {len(sel_to)} recipients.")
                                time.sleep(3) 
                                st.session_state.audit_queue = []
                                st.rerun()
                        except Exception as e: st.error(str(e))

# =====================================================================
    # 📢 PAGE 9: RFAI BILLING PENDING (EXCEL/CSV EXPORT ONLY)
    # =====================================================================
    elif st.session_state.current_page == "RFAI":
        st.markdown("<h3 style='text-align: center; color: #E11D48;'>📢 RFAI Billing Pending</h3>", unsafe_allow_html=True)
        
        col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
        
        if "billing_df" not in st.session_state:
            st.session_state.billing_df = pd.DataFrame()

        # Step 1: Check Data
        if col_2.button("🔍 Step 1: Check Data", use_container_width=True):
            try:
                res_bill = supabase.table("VIS Portal Site Data").select("*").execute()
                if res_bill.data:
                    df_raw = pd.DataFrame(res_bill.data)
                    df_raw.columns = df_raw.columns.str.strip()
                    rfai_list = ["Build Complete by BV", "Pending RFAI", "RFAI Notice Accepted"]
                    mask = (df_raw['RFAI STATUS'].isin(rfai_list)) & (df_raw['WCC NO.'].astype(str).str.strip().isin(['-', '', 'nan', 'None']))
                    st.session_state.billing_df = df_raw[mask]
                    if st.session_state.billing_df.empty:
                        st.warning("No pending sites found.")
                    else:
                        st.success(f"Found {len(st.session_state.billing_df)} Sites!")
            except Exception as e:
                st.error(f"Error: {e}")

        # Step 2: Generate Excel (CSV) & Notify
        if not st.session_state.billing_df.empty:
            # Create CSV Data (Opens natively in Excel without any extra libraries)
            csv_data = st.session_state.billing_df.to_csv(index=False).encode('utf-8')
            
            # Download Button (You must click this first)
            col_3.download_button(
                label="📥 Step 2: Download Excel",
                data=csv_data,
                file_name=f"RFAI_Pending_{datetime.now().strftime('%d-%b-%Y')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # WhatsApp Notification
            wa_msg = f"Hello, RFAI Pending Report ({len(st.session_state.billing_df)} sites) is ready. Please check the downloaded Excel file."
            wa_url = f"https://wa.me/919960843473?text={urllib.parse.quote(wa_msg)}"
            col_4.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:42px; background-color:#25D366; color:white; border-radius:8px; border:none; font-weight:bold; cursor:pointer;">💬 Notify on WA</button></a>', unsafe_allow_html=True)

        st.divider()
        if not st.session_state.billing_df.empty:
            st.write("### Pending Billing List")
            st.dataframe(st.session_state.billing_df[['SITE ID', 'SITE NAME', 'RFAI STATUS', 'WCC NO.']], use_container_width=True, hide_index=True)

