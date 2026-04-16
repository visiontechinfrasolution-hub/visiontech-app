import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

def show(supabase):
    st.markdown("""
        <style>
            .site-badge { 
                background-color: #E0F2FE; color: #0369A1; padding: 2px 8px; 
                border-radius: 12px; font-weight: 600; font-size: 11px; border: 1px solid #BAE6FD; 
            }
            .wa-btn { 
                background-color: #25D366; color: white !important; padding: 4px 8px; 
                border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px;
            }
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
        try: return supabase.table("WCC Status").upsert(payload).execute()
        except: return None

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
                    v_wno = row_data.get("WCC Number") if is_edit else None 
                else:
                    v_pid = row_data.get('Project ID')
                    v_wno = st.text_input("Enter WCC Number", value=str(row_data.get("WCC Number", "")) if is_edit else "")
                
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    def clean_id(v): return ''.join(filter(str.isdigit, str(v))) if v else None
                    payload = {"Project ID": v_pid, "WCC Number": clean_id(v_wno)}
                    if role == "requester": 
                        payload.update({"Project": v_proj, "Site ID": v_sid, "Site Name": v_snm, "PO Number": clean_id(v_po), "Reqeust Date": str(v_dt), "WCC Status": v_sts})
                    if update_wcc_record(payload): st.rerun()

        data_list = fetch_wcc_data_simple()
        df_wcc = pd.DataFrame(data_list) if data_list else pd.DataFrame()
        
        if role == "requester":
            if st.button("➕ Add New Site Request", type="primary"): wcc_edit_modal()
        
        st.divider()

        if not df_wcc.empty:
            h_cols = st.columns([1, 0.5, 1.2, 1.5, 1, 1.2, 1, 1.2])
            cols_names = ["Actions", "Sr.", "Project", "Project ID", "Site ID", "Site Name", "PO No", "Status"]
            for col, name in zip(h_cols, cols_names):
                col.markdown(f"<p style='color:#1E3A8A; font-weight:bold; font-size:13px; text-align:center;'>{name}</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0px; border-top: 2px solid #1E3A8A;'>", unsafe_allow_html=True)

            for i, row in df_wcc.iterrows():
                r_cols = st.columns([1, 0.5, 1.2, 1.5, 1, 1.2, 1, 1.2])
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
                            f"Hello Prkash Ji,\nRaise WCC urgently...\n\n"
                            f"*Project* :- {clean_none(row.get('Project'))}\n"
                            f"*Project ID* :- {clean_none(row.get('Project ID'))}\n"
                            f"*Site ID* :- {clean_none(row.get('Site ID'))}\n"
                            f"*Site Name* :- {clean_none(row.get('Site Name'))}\n"
                            f"*PO Number* :- {clean_none(row.get('PO Number'))}\n"
                            f"*Reqeust Date* :- {formatted_date}\n"
                            f"*WCC Number* :- {clean_none(row.get('WCC Number'))}\n"
                            f"*WCC Status* :- {clean_none(row.get('WCC Status'))}\n\n"
                            f"Thanks,\nMayur Patil\n7350533473"
                        )
                        wa_url = f"whatsapp://send?text={urllib.parse.quote(msg)}"
                        b2.markdown(f'<a href="{wa_url}" class="wa-btn">💬</a>', unsafe_allow_html=True)
                
                r_cols[1].markdown(f"<p style='font-size:12px; text-align:center;'>{i+1}</p>", unsafe_allow_html=True)
                r_cols[2].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('Project'))}</p>", unsafe_allow_html=True)
                r_cols[3].markdown(f"<p style='font-size:12px; text-align:center; font-weight:bold;'>{clean_none(row.get('Project ID'))}</p>", unsafe_allow_html=True)
                r_cols[4].markdown(f"<div style='text-align:center;'><span class='site-badge'>{clean_none(row.get('Site ID'))}</span></div>", unsafe_allow_html=True)
                r_cols[5].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('Site Name'))}</p>", unsafe_allow_html=True)
                r_cols[6].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('PO Number'))}</p>", unsafe_allow_html=True)
                r_cols[7].markdown(f"<p style='font-size:12px; text-align:center;'>{clean_none(row.get('WCC Status'))}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:1px 0px; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
