import streamlit as st
import pandas as pd
import requests
from supabase import create_client
import urllib.parse
from datetime import datetime

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
# 📡 WCC STATUS TRACKER (STANDALONE PAGE)
# =====================================================================
st.markdown("""
    <style>
        .site-badge { background-color: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 12px; font-weight: 600; font-size: 11px; border: 1px solid #BAE6FD; }
        .wa-btn { background-color: #25D366; color: white !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; }
        [data-testid="column"] { display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

def send_interakt_whatsapp(row_data):
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

if "wcc_role" not in st.session_state: 
    st.session_state.wcc_role = None

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
                    msg = (
                        f"*Hello Prkash Ji,*\n"
                        f"As per your requirement of pending Wcc please find below detail.\n"
                        f"Raise WCC urgently\n\n"
                        f"*Project* :- {clean_none(row.get('Project'))}\n"
                        f"*Project ID* :- {clean_none(row.get('Project ID'))}\n"
                        f"*Site ID* :- {clean_none(row.get('Site ID'))}\n"
                        f"*Site Name* :- {clean_none(row.get('Site Name'))}\n"
                        f"*PO Number* :- {clean_none(row.get('PO Number'))}\n"
                        f"*Reqeust Date* :- {clean_none(row.get('Reqeust Date'))}\n"
                        f"*WCC Number* :- {clean_none(row.get('WCC Number'))}\n"
                        f"*WCC Status* :- {clean_none(row.get('WCC Status'))}\n\n"
                        f"Thanks,\n"
                        f"Mayur Patil\n"
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
