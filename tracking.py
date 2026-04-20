import streamlit as st
from st_supabase_connection import SupabaseConnection
import requests
import json

# 1. Supabase Connection Setup
# Tumchya .streamlit/secrets.toml madhye URL ani Key asne garjeche aahe
conn = st.connection("supabase", type=SupabaseConnection)

# 2. Interakt Message Function
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    payload = {
        "fullPhoneNumber": f"91{mobile}",
        "type": "Template",
        "template": {
            "name": "pending_followup",
            "languageCode": "mr",
            "bodyValues": [
                str(project_id), 
                str(site_id), 
                str(site_name), 
                str(remark)
            ]
        }
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI START ---
st.set_page_config(page_title="Visiontech Tracking System", layout="centered")
st.title("🚀 VIS Portal Site Tracking")

# 3. Data Fetching
# Master table madhun sites cha data ghene
sites_query = conn.table("vis_portal_data").select("*").execute()
users_query = conn.table("allowed_users").select("*").execute()

if not sites_query.data:
    st.error("VIS Portal Data table madhye data nahiye!")
else:
    # 4. Input Form
    with st.form("tracking_form", clear_on_submit=True):
        st.subheader("Navin Entry kara")
        
        # Project ID Dropdown
        project_ids = [item['project_id'] for item in sites_query.data]
        selected_project = st.selectbox("Select Project ID", options=project_ids)
        
        # Auto-fill Site ID & Name
        site_info = next((item for item in sites_query.data if item['project_id'] == selected_project), None)
        
        col1, col2 = st.columns(2)
        with col1:
            site_id = st.text_input("Site ID", value=site_info['site_id'] if site_info else "", disabled=True)
        with col2:
            site_name = st.text_input("Site Name", value=site_info['site_name'] if site_info else "", disabled=True)
        
        # User Selection
        user_list = [u['user_name'] for u in users_query.data]
        selected_user_name = st.selectbox("Select User", options=user_list)
        
        # Remark
        remark = st.text_area("Remark (माहिती/डॉक्टरमेंट का बाकी आहे?)")
        
        submit_button = st.form_submit_button("Submit & Start Tracking")

    # 5. Form Submission Logic
    if submit_button:
        # Get Mobile Number for the selected user
        user_data = next((u for u in users_query.data if u['user_name'] == selected_user_name), None)
        mobile_no = user_data['user_mobile_number'] if user_data else None

        if not mobile_no:
            st.error("User cha mobile number sapadla nahi!")
        else:
            # A. Supabase madhye data save kara
            insert_data = {
                "project_id": selected_project,
                "site_id": site_info['site_id'],
                "site_name": site_info['site_name'],
                "remark": remark,
                "user_name": selected_user_name,
                "user_mobile_number": mobile_no,
                "status": "Open"
            }
            
            try:
                conn.table("site_tracking").insert(insert_data).execute()
                
                # B. Interakt la pahila message pathva
                status = send_to_interakt(mobile_no, selected_project, site_info['site_id'], site_info['site_name'], remark)
                
                if status == 200 or status == 201:
                    st.success(f"✅ Entry saved! Pahila message {selected_user_name} la gela aahe.")
                    st.info("System ata pratyek 1 tasala automatic reminder pathvel.")
                else:
                    st.warning(f"Data save jhala pan Interakt message gela nahi (Status: {status})")
            
            except Exception as e:
                st.error(f"Database Error: {e}")

# --- TRACKING DASHBOARD (To Close Status) ---
st.divider()
st.subheader("📋 Active Tracking (Open Cases)")

# Open cases fetch kara
active_tasks = conn.table("site_tracking").select("*").eq("status", "Open").execute()

if active_tasks.data:
    for task in active_tasks.data:
        with st.expander(f"{task['site_name']} ({task['project_id']}) - {task['user_name']}"):
            st.write(f"**Remark:** {task['remark']}")
            st.write(f"**Mobile:** {task['user_mobile_number']}")
            if st.button(f"Close Tracking for {task['site_id']}", key=task['id']):
                conn.table("site_tracking").update({"status": "Closed"}).eq("id", task['id']).execute()
                st.rerun()
else:
    st.write("Kontihi active cases nahiyeat.")
