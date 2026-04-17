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

# --- PAGES LOGIC ---
else:
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("⬅️ Dashboard"):
        navigate_to("Dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # =====================================================================
    # 🟩 TAB 1: BOQ REPORT
    # =====================================================================
    if st.session_state.current_page == "BOQ":
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

                if not update_click:
                    if 'Item Code' in df_res.columns:
                        df_res['TempGroupKey'] = df_res.apply(lambda x: x['Sr. No.'] if str(x['Item Code']).strip() == '' else x['Item Code'], axis=1)
                        agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['TempGroupKey']}
                        df_res = df_res.groupby('TempGroupKey', as_index=False).agg(agg_dict)
                
                for col in ['Dispatch Date', 'BOQ Date']:
                    if col in df_res.columns: df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
                
                df_res = df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
                st.session_state['boq_df'] = df_res

        if 'boq_df' in st.session_state:
            df = st.session_state['boq_df']
            final_cols = [c for c in mera_sequence if c in df.columns]
            st.dataframe(df[final_cols], use_container_width=True, hide_index=True)

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
            in_id = st.text_input("📍 Site ID Search")
            if st.form_submit_button("🔍 Search Indus"):
                res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
                if res_ind.data: st.dataframe(pd.DataFrame(res_ind.data))

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
                    else:
                        v_pid = row_data.get('Project ID')
                        v_wno = st.text_input("Enter/Update WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        if not v_pid or v_pid.strip() == "":
                            st.warning("Project ID is mandatory!")
                        else:
                            # Numeric fields handle करण्यासाठी मदत: जर रिकांमे असेल तर None पाठवणे
                            def to_num(val):
                                val = str(val).strip()
                                return val if val != "" else None

                            payload = {
                                "Project ID": v_pid.strip(),
                                "WCC Number": to_num(v_wno)
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
            
            st.divider()

            if not df_wcc.empty:
                h_cols = st.columns([1, 0.5, 1, 1.2, 1, 1.2, 1, 1, 1.2])
                cols_names = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "WCC No", "Status"]
                for col, name in zip(h_cols, cols_names):
                    col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:11px; text-align:center;'>{name}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0px; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

                for i, row in df_wcc.iterrows():
                    r_cols = st.columns([1, 0.5, 1, 1.2, 1, 1.2, 1, 1, 1.2])
                    
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
                    st.markdown("<hr style='margin:1px 0px; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)

    elif st.session_state.current_page == "Data":
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)

    # =====================================================================
    # 📁 TAB 6: DATA ENTRY (Document Center & Tracker)
    # =====================================================================
    elif st.session_state.current_page == "Data":
        st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
        
        # --- Database Functions ---
        def fetch_doc_data():
            try:
                res = supabase.table("Document_Tracker").select("*").execute()
                return res.data if res.data else []
            except Exception as e:
                return []

        def save_doc_entry(data):
            try:
                return supabase.table("Document_Tracker").insert(data).execute()
            except Exception as e:
                st.error(f"❌ Save Error: {e}")
                return None

        # --- Sub-Tabs ---
        d_sub1, d_sub2, d_sub3 = st.tabs(["📤 Manager Upload", "🔍 Team Search", "📊 Tracker"])
        
        with d_sub1:
            st.markdown("#### 📂 Upload New Document Details")
            with st.form("doc_upload_form_v2", clear_on_submit=True):
                c1, c2 = st.columns(2)
                d_proj = c1.selectbox("Project Name", ["Operation", "Maintenance", "I-Tower", "Other"])
                d_site = c2.text_input("Site ID / Project ID *")
                
                c3, c4 = st.columns(2)
                d_type = c3.selectbox("Document Type", ["WCC", "PO", "BOQ", "Invoice", "Approval Letter", "Other"])
                d_po = c4.text_input("PO Number (Optional)")
                
                d_remarks = st.text_area("Remarks / Notes")
                
                if st.form_submit_button("🚀 Save Entry to Portal", use_container_width=True):
                    if d_site:
                        entry_data = {
                            "Date": datetime.now().strftime("%Y-%m-%d"),
                            "Project": d_proj,
                            "Site_ID": d_site.strip(),
                            "Doc_Type": d_type,
                            "PO_Number": d_po.strip() if d_po else None,
                            "Remarks": d_remarks.strip() if d_remarks else None,
                            "Status": "Uploaded"
                        }
                        if save_doc_entry(entry_data):
                            st.success(f"✅ Entry for {d_site} saved successfully!")
                            st.rerun()
                    else:
                        st.warning("⚠️ Please enter Site ID / Project ID.")

        with d_sub2:
            st.markdown("#### 🔍 Search Documents")
            search_q = st.text_input("Search Site ID / Project ID / PO Number", key="doc_search_box")
            if search_q:
                all_docs = fetch_doc_data()
                results = [d for d in all_docs if search_q.lower() in str(d).lower()]
                if results:
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                else:
                    st.info("No matching records found.")

        with d_sub3:
            st.markdown("#### 📊 Document Tracker")
            raw_docs = fetch_doc_data()
            if raw_docs:
                st.dataframe(pd.DataFrame(raw_docs)[::-1], use_container_width=True)
            else:
                st.info("No documents tracked yet.")
    # =====================================================================
    # 💰 TAB 7: FINANCE (या ओळीची स्पेस नीट तपासा)
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
            default_to = ["visiontechinfrasolution@gmail.com"]
            default_cc = ["services@vispltower.com", "project.visiontechinfra@gmail.com"]
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


