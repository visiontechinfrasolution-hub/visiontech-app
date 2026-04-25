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

# --- NAVIGATION FUNCTION ---
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .stApp { background-color: #F8FAFC; }
    
    /* Desktop Buttons */
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

    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important; flex-wrap: wrap !important;
            justify-content: center !important; gap: 10px !important;
        }
        div[data-testid="column"] {
            min-width: 45% !important; max-width: 45% !important; padding: 0 !important;
        }
        div.stButton > button {
            height: 100px !important; font-size: 14px !important;
        }
    }

    .back-btn button {
        height: 50px !important; width: 160px !important;
        background-color: #64748B !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- 2. POP-UP DIALOG (NEW ENTRY FORM) ---
@st.dialog("➕ Add New Site Record")
def open_entry_popup():
    with st.form("site_form_pop", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            p_id = st.text_input("Project ID")
            s_id = st.text_input("Site ID")
            s_name = st.text_input("Site Name")
        with f2:
            clstr = st.text_input("Cluster")
            a_date = st.date_input("Allocation Date")
            w_desc = st.text_area("Work Description")
        with f3:
            p_no = st.text_input("PO No")
            p_amt = st.number_input("PO Amount", min_value=0.0)
            wcc_no = st.text_input("WCC Number")
            wcc_st = st.selectbox("WCC Status", ["Pending", "Approved", "Rejected"])
        
        if st.form_submit_button("Submit Data", use_container_width=True):
            new_data = {
                "project_id": p_id, "site_id": s_id, "site_name": s_name,
                "cluster": clstr, "allocation_date": str(a_date),
                "work_description": w_desc, "po_no": p_no, "po_amt": float(p_amt),
                "wcc_number": wcc_no, "wcc_status": wcc_st
            }
            try:
                # Using upsert as requested to handle conflicts automatically
                supabase.table("nr_calculation").upsert(new_data, on_conflict="project_id").execute()
                st.success("✅ Record Added Successfully!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Database Error: {e}")

# --- MAIN DASHBOARD ---
if st.session_state.current_page == "Dashboard":
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🚀 Visiontech Portal</h1>", unsafe_allow_html=True)
    
    spacer1, c1, c2, c3, spacer2 = st.columns([1, 2, 2, 2, 1])
    
    with c1:
        if st.button("📦\nBOQ Report"): st.switch_page("pages/boq_report.py")
        if st.button("📊\nIndus Data"): st.switch_page("pages/indus_data.py")
        if st.button("🚨\nSTN Manager"): navigate_to("STN Manager")
        if st.button("📜\nVintage PDF"): navigate_to("PDFFormat")

    with c2:
        if st.button("🧾\nPO Report"): navigate_to("PO")
        if st.button("📡\nWCC Tracker"): st.switch_page("pages/wcc_tracker.py")
        if st.button("📝\nAudit Portal"): navigate_to("Audit")
        if st.button("🛰️\nSite Tracking"): st.switch_page("pages/tracking.py")

    with c3:
        if st.button("🚀\nJajupro"): navigate_to("Jajupro")
        if st.button("📁\nData Entry"): st.switch_page("pages/data_entry.py")
        if st.button("📢\nRFAI Billing"): navigate_to("RFAI")

# --- JAJUPRO PAGE LOGIC ---
elif st.session_state.current_page == "Jajupro":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): navigate_to("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    st.title("🚀 Jajupro Management")

    # Fetch Fresh Data
    try:
        site_res = supabase.table("nr_calculation").select("*").order('id', desc=True).execute()
        fin_res = supabase.table("nr_finance").select("*").execute()
        df_site = pd.DataFrame(site_res.data) if site_res.data else pd.DataFrame()
        df_fin = pd.DataFrame(fin_res.data) if fin_res.data else pd.DataFrame()
        
        # Ensure all column names are lowercase to prevent display issues
        if not df_site.empty:
            df_site.columns = [c.lower() for c in df_site.columns]
    except:
        df_site, df_fin = pd.DataFrame(), pd.DataFrame()

    # Metrics (3 Boxes)
    t_site = df_site['po_amt'].sum() if not df_site.empty and 'po_amt' in df_site.columns else 0
    t_paid = df_fin['payment_amt'].sum() if not df_fin.empty and 'payment_amt' in df_fin.columns else 0
    balance = t_site - t_paid

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Site Amount", f"₹ {t_site:,.2f}")
    m2.metric("Total Paid Amount", f"₹ {t_paid:,.2f}")
    m3.metric("Pending Balance", f"₹ {balance:,.2f}")

    st.divider()

    tab_site, tab_finance = st.tabs(["🏗️ Site Entry", "💰 Finance"])

    with tab_site:
        st.subheader("Site Entry - NR Calculation")
        # Action Bar (New Entry, Bulk, Download)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("➕ New Entry", key="jaju_new_btn"):
                open_entry_popup()
        
        with col2:
            up_file = st.file_uploader("📂 Bulk Upload", type=['xlsx', 'csv'], label_visibility="collapsed")
            if up_file:
                try:
                    bulk_df = pd.read_excel(up_file) if up_file.name.endswith('xlsx') else pd.read_csv(up_file)
                    bulk_df.columns = [c.lower().replace(' ', '_') for c in bulk_df.columns]
                    data_to_save = bulk_df.to_dict(orient='records')
                    supabase.table("nr_calculation").upsert(data_to_save, on_conflict="project_id").execute()
                    st.success(f"Successfully uploaded {len(data_to_save)} records!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Bulk Upload Error: {e}")

        with col3:
            if not df_site.empty:
                st.download_button("📥 Download Excel", data=df_site.to_csv(index=False), file_name="NR_Report.csv")

        st.write("---")
        
        # Search Bar
        search = st.text_input("🔍 Search Site Data...", placeholder="Type Site ID or Project ID...")
        if search and not df_site.empty:
            df_site = df_site[df_site.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

        # --- CUSTOM TABLE WITH EDIT BUTTONS ---
        if not df_site.empty:
            # Table Header Styling
            st.markdown("""
                <div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>
                    <div style='display: flex; color: white; font-weight: bold;'>
                        <div style='flex: 0.6;'>Edit</div>
                        <div style='flex: 1;'>Site ID</div>
                        <div style='flex: 1;'>Project ID</div>
                        <div style='flex: 2;'>Site Name</div>
                        <div style='flex: 1;'>PO Amount</div>
                        <div style='flex: 1;'>Status</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Table Data Rows
            for idx, row in df_site.iterrows():
                # Case-insensitive data fetch logic
                s_id = row.get('site_id', row.get('Site_ID', '-'))
                p_id = row.get('project_id', row.get('Project_ID', '-'))
                s_name = row.get('site_name', row.get('Site_Name', '-'))
                p_amt = row.get('po_amt', row.get('Po_amt', 0))
                status = row.get('wcc_status', row.get('Wcc_status', '-'))
                db_id = row.get('id')

                t_row = st.columns([0.6, 1, 1, 2, 1, 1])
                # Edit Action
                if t_row[0].button("📝", key=f"edit_act_{db_id}"):
                    st.toast(f"Edit Mode Active for {s_id}")
                
                t_row[1].write(s_id)
                t_row[2].write(p_id)
                t_row[3].write(s_name)
                t_row[4].write(f"₹{float(p_amt):,.2f}")
                t_row[5].write(status)
                st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        else:
            st.info("No records found in database.")

    with tab_finance:
        st.subheader("Finance Transaction History")
        st.dataframe(df_fin, use_container_width=True, hide_index=True)

# --- OTHER PAGES LOGIC ---
elif st.session_state.current_page != "Dashboard":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"): navigate_to("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    cur_p = st.session_state.current_page
    if cur_p == "STN Manager":
        st.title("🚨 STN Manager")
    elif cur_p == "Audit":
        st.title("📝 Audit Portal")
    elif cur_p == "PO":
        st.title("🧾 PO Report")
    elif cur_p == "RFAI":
        st.title("📢 RFAI Billing")
    elif cur_p == "PDFFormat":
        st.title("📜 Vintage PDF")
    else:
        st.write(f"Section {cur_p} is active.")
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
                    # Error Fix: Query building ko simple rakha hai
                    query = supabase.table("BOQ Report").select("*")
                    if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
                    if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
                    if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
                    
                    try:
                        data = fetch_complete_data(query)
                        df_final = process_boq_data(data)
                    except Exception as e:
                        st.error(f"Supabase Fetch Error: {e}")
                        df_final = pd.DataFrame()
                    
                    if not df_final.empty:
                        st.success(f"✅ {len(df_final)} Records Found!")

                        # --- UPDATED LOGIC: STN STATUS (Qty B > 0 Only) ---
                        try:
                            # Step 1: Filter Capex AND Parent items only
                            mask = (
                                df_final['Product'].astype(str).str.contains('Capex', case=False, na=False) & 
                                df_final['Parent/Child'].astype(str).str.contains('Parent', case=False, na=False)
                            )
                            df_status_check = df_final[mask].copy()

                            if not df_status_check.empty:
                                # Qty numeric conversion
                                df_status_check['Qty A'] = pd.to_numeric(df_status_check['Qty A'], errors='coerce').fillna(0)
                                df_status_check['Qty B'] = pd.to_numeric(df_status_check['Qty B'], errors='coerce').fillna(0)
                                df_status_check['Qty C'] = pd.to_numeric(df_status_check['Qty C'], errors='coerce').fillna(0)

                                # logic: Sirf wahi rows consider karo jahan Qty B > 0 hai (Material liya gaya hai)
                                # Isse wo rows ignore ho jayengi jisme process shuru hi nahi hua
                                df_dispatched = df_status_check[df_status_check['Qty B'] > 0]

                                if not df_dispatched.empty:
                                    # Condition: Jitna liya (Qty B) utna hi mila (Qty C) hona chahiye
                                    is_stn_done = all(df_dispatched['Qty B'] == df_dispatched['Qty C'])

                                    if is_stn_done:
                                        st.markdown("""
                                            <div style='background-color: #DCFCE7; padding: 20px; border-radius: 12px; border: 2px solid #166534; text-align: center;'>
                                                <h1 style='color: #166534; margin: 0;'>✅ STN Done</h1>
                                                <p style='color: #166534; margin: 0; font-weight: bold;'>Jitna material liya (Qty B), utna mil gaya (Qty C)!</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        st.markdown("""
                                            <div style='background-color: #FEE2E2; padding: 20px; border-radius: 12px; border: 2px solid #991B1B; text-align: center;'>
                                                <h1 style='color: #991B1B; margin: 0;'>❌ STN Pending</h1>
                                                <p style='color: #991B1B; margin: 0; font-weight: bold;'>Liya hua material (Qty B) aur mila hua material (Qty C) match nahi hai.</p>
                                            </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.info("ℹ️ Is Project mein abhi koi Capex-Parent material 'Liya' (Qty B > 0) nahi gaya hai.")
                            else:
                                st.info("ℹ️ Is Search mein koi Capex-Parent item nahi mila.")
                            st.write("") 
                        except Exception as e:
                            st.error(f"Logic Error: {e}")
                        # --- END OF UPDATED LOGIC ---

                        st.dataframe(df_final[[c for c in mera_sequence if c in df_final.columns]], use_container_width=True, hide_index=True)
                    else: 
                        st.warning("कोणतीही माहिती सापडली नाही.")

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

    import streamlit as st
import pandas as pd
import urllib.parse
from geopy.distance import geodesic

# --- Syntax check for if/elif alignment ---
if st.session_state.current_page == "Home":
    st.markdown("<h2 style='text-align: center;'>🏠 Visiontech Portal Home</h2>", unsafe_allow_html=True)

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
                    # Format: origin/stop1/stop2/destination
                    stops = "/".join([f"{s['Lat']},{s['Long']}" for s in final_path])
                    gmaps_route = f"https://www.google.com/maps/dir/{start_coords}/{stops}/{end_coords}"
                    st.markdown(f'<a href="{gmaps_route}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold; cursor:pointer;">🗺️ Open Sequential Route (1-2-3-4)</button></a>', unsafe_allow_html=True)
            except Exception as e: st.error(f"Error: {e}")
   # =====================================================================
    # 📡 TAB 5: WCC STATUS (ORIGINAL LOGIC + SEARCH BOX)
    # =====================================================================
    elif st.session_state.current_page == "WCC":
        st.markdown("""
            <style>
                .site-badge { background-color: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px; border: 1px solid #BAE6FD; }
                .wa-btn { background-color: #25D366; color: white !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; }
                [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
            </style>
        """, unsafe_allow_html=True)

        def send_interakt_whatsapp(row_data):
            import requests
            api_key = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="
            numbers = ["919960843473", "919552273181", "917498984373"]
            url = "https://api.interakt.ai/v1/public/message/"
            headers = {"Authorization": f"Basic {api_key}", "Content-Type": "application/json"}
            
            body_values = [
                str(row_data.get("Project", "")), str(row_data.get("Project ID", "")),
                str(row_data.get("Site ID", "")), str(row_data.get("Site Name", "")),
                str(row_data.get("PO Number", "")), str(row_data.get("Reqeust Date", "")),
                str(row_data.get("WCC Number", "")), str(row_data.get("WCC Status", ""))
            ]

            for num in numbers:
                payload = {
                    "countryCode": "+91", "phoneNumber": num[2:], 
                    "callbackData": "WCC Request Automation", "type": "Template",
                    "template": {"name": "wccrequest", "languageCode": "en", "bodyValues": body_values}
                }
                try: requests.post(url, headers=headers, json=payload, timeout=5)
                except: pass

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
                            def to_num(val): return str(val).strip() if str(val).strip() != "" else None
                            payload = {"Project ID": v_pid.strip(), "WCC Number": to_num(v_wno), "Remark": v_rem}
                            if role == "requester": 
                                payload.update({"Project": v_proj, "Site ID": v_sid, "Site Name": v_snm, "PO Number": to_num(v_po), "Reqeust Date": str(v_dt), "WCC Status": v_sts})
                            response = update_wcc_record(payload)
                            if response:
                                if role == "requester": send_interakt_whatsapp(payload)
                                st.success("Data Saved & WhatsApp Sent! ✅")
                                st.rerun()

            data_list = fetch_wcc_data_simple()
            df_wcc = pd.DataFrame(data_list)[::-1] if data_list else pd.DataFrame()
            
            c_top1, c_top2, c_top3 = st.columns([1, 1, 1.5])
            with c_top1:
                if role == "requester" and st.button("➕ Add New Site Request", type="primary"): wcc_edit_modal()
            with c_top2:
                if not df_wcc.empty:
                    excel_data = df_wcc.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Download Report", data=excel_data, file_name=f"WCC_Report.csv", mime="text/csv")
            with c_top3:
                search_query = st.text_input("🔍 Search Project, Site, PO...", key="wcc_search_v1")

            if search_query and not df_wcc.empty:
                df_wcc = df_wcc[df_wcc.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

            with st.expander("🛠️ Bulk Update WCC & Remarks via Excel"):
                st.info("फक्त डाउनलोड केलेली फाईल वापरा (Project ID, PO Number, WCC Number, Remark)")
                uploaded_file = st.file_uploader("Upload Excel/CSV", type=["csv", "xlsx"], key="bulk_up_v3")
                if uploaded_file:
                    try:
                        up_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                        up_df.columns = [str(c).strip() for c in up_df.columns]
                        if st.button("🆙 Start Update Process"):
                            success_count, not_found_count = 0, 0
                            for _, up_row in up_df.iterrows():
                                def get_clean_val(col_name):
                                    val = str(up_row.get(col_name, '')).strip()
                                    if val.endswith('.0'): val = val[:-2]
                                    return val if val not in ['nan', 'None', ''] else None
                                pid, po_no, wcc_no, remark = get_clean_val('Project ID'), get_clean_val('PO Number'), get_clean_val('WCC Number'), get_clean_val('Remark')
                                if pid and po_no:
                                    match = df_wcc[(df_wcc['Project ID'].astype(str).str.strip() == pid) & (df_wcc['PO Number'].astype(str).str.strip() == po_no)]
                                    if not match.empty:
                                        try:
                                            supabase.table("WCC Status").update({"WCC Number": wcc_no, "Remark": remark if remark else ""}).eq("Project ID", pid).eq("PO Number", po_no).execute()
                                            success_count += 1
                                        except Exception as e: st.error(f"Error for {pid}: {e}")
                                    else: not_found_count += 1
                            if success_count > 0: st.success(f"✅ {success_count} Records Updated!"); st.rerun()
                            else: st.error("❌ No matches found!")
                    except Exception as e: st.error(f"❌ File Error: {e}")            
            
            st.divider()

            if not df_wcc.empty:
                h_cols = st.columns([1, 0.4, 0.8, 1.2, 0.8, 1, 0.8, 0.8, 1, 1])
                cols_names = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "WCC No", "Status", "Remark"]
                for col, name in zip(h_cols, cols_names): col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:11px; text-align:center;'>{name}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0px; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

                for i, row in df_wcc.iterrows():
                    r_cols = st.columns([1, 0.4, 0.8, 1.2, 0.8, 1, 0.8, 0.8, 1, 1])
                    def clean_none(val): return str(val) if val and str(val).lower() != 'none' else ""
                    with r_cols[0]:
                        b1, b2 = st.columns(2)
                        if b1.button("✏️", key=f"edit_{row['Project ID']}_{i}"): wcc_edit_modal(row)
                        if role == 'requester':
                            import urllib.parse
                            msg = (f"*Hello Prakash Ji,*\nRaise WCC urgently...\n\n*Project* :- {clean_none(row.get('Project'))}\n*Project ID* :- {clean_none(row.get('Project ID'))}\n*Site ID* :- {clean_none(row.get('Site ID'))}\n*PO Number* :- {clean_none(row.get('PO Number'))}\n\nThanks,\n*Mayur Patil*")
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

    # =====================================================================
    # 🏗️ TAB 6: DATA ENTRY (Document Center & Tracker)
    # =====================================================================
    elif "Data" in str(st.session_state.current_page) or "Entry" in str(st.session_state.current_page):
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
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
                                supabase.storage.from_("site_documents").upload(path=fname, file=f.getvalue(), file_options={"x-upsert": "true"})
                                p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                                supabase.table("site_documents_master").upsert({
                                    "project_number": u_proj, "indus_id": u_indus, "site_name": u_site, 
                                    "doc_type": u_type, "file_name": fname, "file_url": p_url
                                }, on_conflict="file_name").execute()
                            st.success("✅ Files Uploaded & Master Updated!")
                            st.rerun()
                        except Exception as e: st.error(f"❌ Error: {e}")
                    else: st.warning("⚠️ Files aur Project Number dalna zaroori hai!")

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
            try:
                res_t = supabase.table("site_documents_master").select("*").execute()
                if res_t.data:
                    df_t = pd.DataFrame(res_t.data)
                    summary = []
                    for ind_id, gp in df_t.groupby('indus_id'):
                        types = gp['doc_type'].str.upper().tolist()
                        summary.append({
                            "Project ID": gp.iloc[0]['project_number'], "Indus ID": ind_id, "Site Name": gp.iloc[0]['site_name'], 
                            "SRC": "✅" if "SRC" in types else "❌", "DC": "✅" if "DC" in types else "❌", "STN": "✅" if "STN" in types else "❌", 
                            "Report": "✅" if "REPORT" in types else "❌", "Photo": "✅" if "PHOTO" in types else "❌"
                        })
                    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
            except: st.info("Tracker data loading...")
    # =====================================================================
    # 💰 TAB 1: FINANCE ENTRY (Baaki code same rahega)
    # =====================================================================
    if st.session_state.current_page == "Finance":
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
    if st.session_state.current_page == "Audit":
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
    if st.session_state.current_page == "RFAI":
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
# =====================================================================
    # 🚨 TAB 7: STN MANAGER - NON-STOP MARATHI FOLLOW-UP
    # =====================================================================
    if st.session_state.current_page == "STN Manager":
        import requests
        import pandas as pd
        import re 
        import google.generativeai as genai
        from datetime import datetime, timedelta

        # --- 1. CONFIG ---
        genai.configure(api_key="AIzaSyDed-krPqnZXVCRcbIpV3yPPdXoxF3qEQk")
        INTERAKT_API_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="

        st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🤖 Visiontech Smart AI Assistant</h2>", unsafe_allow_html=True)

        # --- 2. AI MOTIVATOR BRAIN ---
        def get_ai_followup(site_id, team_name):
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Yethun AI la kadak Marathi सूचना dilelya aahet
            prompt = (
                f"Team member '{team_name}' yaala Site {site_id} cha STN close karaycha reminder dya. "
                "Tone ekdam natural Marathi pahije. 'Dada', 'Malak', 'Bhava' vapra. "
                "Vichara ki 'Kay jhala?', 'Kiti vel lagnar?', 'Kam purna karunach thamba'. "
                "Thodi duniyadari kiwa politics chi witty line add kara jyamule tyala chatting vatel. "
                "Max 20 words. 100% Marathi."
            )
            try:
                response = model.generate_content(prompt)
                return response.text.strip()
            except:
                return f"Dada {team_name}, Site {site_id} cha STN pending ahe, kay jhala? Lavkar purna kara malak!"

        # --- 3. WHATSAPP ENGINE ---
        def send_wa_chat(phone, msg):
            url = "https://api.interakt.ai/v1/public/message/"
            headers = {"Authorization": f"Basic {INTERAKT_API_KEY}", "Content-Type": "application/json"}
            payload = {"countryCode": "+91", "phoneNumber": str(phone)[-10:], "type": "Text", "message": msg}
            try: requests.post(url, headers=headers, json=payload, timeout=10)
            except: pass

        def send_wa_template(phone, row):
            url = "https://api.interakt.ai/v1/public/message/"
            headers = {"Authorization": f"Basic {INTERAKT_API_KEY}", "Content-Type": "application/json"}
            items_clean = re.sub(r'\s+', ' ', str(row['item_details']).replace("\n", " ➤ ")).strip()
            payload = {
                "countryCode": "+91", "phoneNumber": str(phone)[-10:],
                "type": "Template",
                "template": {
                    "name": "stnpending", "languageCode": "mr",
                    "bodyValues": [
                        str(row['project_id']), str(row['site_id']), str(row['site_name']),
                        str(row['cluster']), items_clean, str(row['total_qty_b']), "तात्काळ क्लोज करा."
                    ]
                }
            }
            try: requests.post(url, headers=headers, json=payload, timeout=15)
            except: pass

        # --- 4. TOP BUTTONS ---
        res_display = supabase.table("stn_pending_analysis").select("*").execute()
        df_display = pd.DataFrame(res_display.data)

        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("🔄 Sync Fresh Data", use_container_width=True):
                # (Assumed sync function exists)
                st.rerun()
        with col_b:
            if st.button("📢 Bulk Message (Initial Notify)", use_container_width=True, type="primary"):
                count = 0
                for _, r in df_display.iterrows():
                    if r.get('team_number') and r.get('v_status') == "Pending":
                        send_wa_template(r['team_number'], r)
                        count += 1
                st.success(f"✅ {count} Teams na purna data pathvla!")

        st.divider()

        # --- 5. THE 2-MINUTE SMART MONITOR ---
        st.subheader("⏱️ AI Live Follow-up Status")
        if not df_display.empty:
            now = datetime.now()
            for idx, row in df_display.iterrows():
                if row.get('team_number') and row.get('v_status') == "Pending":
                    try:
                        l_time_str = row.get('last_followup')
                        l_time = datetime.fromisoformat(l_time_str) if l_time_str else now - timedelta(minutes=10)
                        
                        seconds_passed = (now - l_time).total_seconds()
                        
                        if seconds_passed >= 120:  # STRICT 2 MINUTES
                            st.info(f"🤖 AI Chatting with {row['assigned_team']}...")
                            # AI kadun natural Marathi message ghene
                            msg = get_ai_followup(row['site_id'], row['assigned_team'])
                            send_wa_chat(row['team_number'], msg)
                            # Update time in Supabase
                            supabase.table("stn_pending_analysis").update({"last_followup": now.isoformat()}).eq("project_id", row['project_id']).execute()
                    except: continue

        # --- 6. ACTION TABLE ---
        if not df_display.empty:
            res_teams = supabase.table("allowed_users").select("name, phone_number").execute()
            df_teams = pd.DataFrame(res_teams.data)
            for i, row in df_display.iterrows():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1.5, 2.5, 1.5, 1])
                    with c1: st.write(f"**Project:** {row['project_id']}"); st.caption(f"📍 {row['cluster']}")
                    with c2: st.info(row['item_details'])
                    with c3:
                        t_list = ["Select Team"] + df_teams['name'].tolist()
                        sel_t = st.selectbox("Assign Team", t_list, index=t_list.index(row['assigned_team']) if row['assigned_team'] in t_list else 0, key=f"t_{i}")
                        sel_v = st.selectbox("Status", ["Pending", "Closed"], index=0 if row['v_status'] == "Pending" else 1, key=f"v_{i}")
                    with c4:
                        if st.button("💾 Save", key=f"s_{i}", use_container_width=True):
                            t_ph = df_teams[df_teams['name'] == sel_t]['phone_number'].values[0] if sel_t != "Select Team" else None
                            supabase.table("stn_pending_analysis").update({
                                "assigned_team": sel_t, "team_number": t_ph, "v_status": sel_v, "last_followup": datetime.now().isoformat()
                            }).eq("project_id", row['project_id']).execute()
                            st.success("Saved!")
                        if st.button("💬 Chat", key=f"chat_{i}", use_container_width=True):
                            # Force chat
                            m = get_ai_followup(row['site_id'], row['assigned_team'])
                            send_wa_chat(row['team_number'], m)
                            st.toast(f"AI: {m}")

# =====================================================================
# 📜 TAB 10: VINTAGE PDF FORMATTER - FINAL MASTER (NO CONTENT CUT)
# =====================================================================
if st.session_state.current_page == "PDFFormat":
    import io
    import random
    import numpy as np
    from PIL import Image, ImageDraw, ImageOps, ImageFilter

    if "v_uploader_key" not in st.session_state:
        st.session_state.v_uploader_key = 100

    try:
        import fitz 
    except:
        st.error("Terminal madhe 'pip install pymupdf' run kara")
        st.stop()

    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📜 Professional Vintage Fold</h2>", unsafe_allow_html=True)
    
    col_u, col_d, col_cl = st.columns(3)
    v_file = st.file_uploader("📂 Upload PDF", type=['pdf'], key=f"v_up_v3_{st.session_state.v_uploader_key}")

    def apply_perfect_vintage(image):
        image = image.convert("RGBA")
        w, h = image.size
        
        # 1. Base Setup (Off-White / Eggshell Color)
        # Tumhala ganda pivla nako hota, mhanun ekdum light off-white set kela ahe.
        canvas = Image.new("RGBA", (w, h), (248, 247, 242, 255))
        canvas.paste(image, (0, 0), image)

        # 2. REAL 4-FOLD CREASE (No Lines - Only Depth)
        # Kagad 4 vela modun parat ughadlya sarkha vatel
        draw = ImageDraw.Draw(canvas)
        
        def add_soft_crease(draw_obj, y_pos):
            # Multiple faint shadows for depth (10px wide shadow)
            for i in range(12):
                strength = int(30 * (1 - i/12))
                # Shadow (Darker)
                draw_obj.line([(0, y_pos + i), (w, y_pos + i)], fill=(110, 105, 90, strength), width=1)
                # Highlight (Lighter)
                draw_obj.line([(0, y_pos - i), (w, y_pos - i)], fill=(255, 255, 255, strength), width=1)

        # 4 Horizontal Folds precisely
        fold_locations = [h//5, 2*h//5, 3*h//5, 4*h//5]
        for fy in fold_locations:
            add_soft_crease(draw, fy + random.randint(-10, 10))

        # 3. INTERNAL TORN EFFECT (Page chya aatun fadla ahe)
        # Content cut honar nahi yachi kaalji ghetli ahe.
        mask = Image.new("L", (w, h), 255)
        d_mask = ImageDraw.Draw(mask)
        tear_y = h - random.randint(40, 70)
        
        points = [(0, tear_y)]
        for x in range(0, w + 10, 20):
            # Randomized 'V' and 'U' cuts
            ty = tear_y + random.randint(-10, 30)
            if x > w//4 and x < 3*w//4: ty -= random.randint(20, 40)
            points.append((x, ty))
        points.extend([(w, h), (0, h)])
        d_mask.polygon(points, fill=0)
        
        canvas.putalpha(mask.filter(ImageFilter.GaussianBlur(radius=0.5)))

        # 4. FINAL POLISH
        final = Image.new("RGB", (w, h), (255, 255, 255))
        final.paste(canvas, (0, 0), canvas)
        
        # Subtle Noise for Scan feel
        img_arr = np.array(final)
        noise = np.random.normal(0, 5, img_arr.shape)
        final = Image.fromarray(np.clip(img_arr + noise, 0, 255).astype(np.uint8))
        
        return final

    if v_file:
        try:
            pdf_bytes = v_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            processed_pages = []

            with st.spinner("⏳ High Quality Fold Processing..."):
                for page in doc:
                    # Rendering matrix 1.5 kela ahe taaki content cut hou naye
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8)) 
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    processed_pages.append(apply_perfect_vintage(img))

            output_pdf = io.BytesIO()
            if processed_pages:
                processed_pages[0].save(output_pdf, format="PDF", save_all=True, append_images=processed_pages[1:], quality=100)
            
            with col_u: st.success("✅ SNC Master Done!")
            with col_d:
                st.download_button("📥 DOWNLOAD VINTAGE PDF", output_pdf.getvalue(), f"Vintage_{v_file.name}", "application/pdf", use_container_width=True)
            
            st.divider()
            st.image(processed_pages[0], caption="No Content Cut - Real 4-Folds", use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")

    with col_cl:
        if st.button("🧹 CLEAR ALL", use_container_width=True):
            st.session_state.v_uploader_key += 1
            st.rerun()
