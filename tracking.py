import streamlit as st
from supabase import create_client, Client
import requests

# 1. CONNECTION
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_secret_h_TJpksUbg2Cr5DvpFz5rA_b8cGGTih" # Tumchi Secret Key
supabase: Client = create_client(URL, KEY)

# 2. INTERAKT FUNCTION
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    # Mobile number madhle spaces kadhun takne
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    
    payload = {
        "fullPhoneNumber": clean_mobile, # Tumchya table madhye aadhiach 91 aahe
        "type": "Template",
        "template": {
            "name": "pending_followup",
            "languageCode": "mr",
            "bodyValues": [str(project_id), str(site_id), str(site_name), str(remark)]
        }
    }
    res = requests.post(interakt_url, json=payload, headers=headers)
    return res.status_code

# --- UI START ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking System")

# 3. FETCH DATA
# Tumchya table names pramane: 'VIS Portal Site Data' ani 'allowed_users'
sites = supabase.table("VIS Portal Site Data").select("*").execute()
users = supabase.table("allowed_users").select("*").execute()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 नवीन ट्रॅकिंग सुरु करा")
    with st.form("tracking_form", clear_on_submit=True):
        # Column names: 'Project ID', 'Site ID', 'Site Name' (Verify if spaces exist)
        p_ids = [s['Project ID'] for s in sites.data] if sites.data else []
        selected_p = st.selectbox("Project ID निवडा", options=p_ids)
        
        s_info = next((s for s in sites.data if s['Project ID'] == selected_p), None)
        s_id = st.text_input("Site ID", value=s_info['Site ID'] if s_info else "", disabled=True)
        s_name = st.text_input("Site Name", value=s_info['Site Name'] if s_info else "", disabled=True)
        
        # User selection from 'name' column
        u_names = [u['name'] for u in users.data] if users.data else []
        selected_u = st.selectbox("कोणाला मेसेज पाठवायचा?", options=u_names)
        
        rem = st.text_area("Remark")
        
        if st.form_submit_button("Submit & Start Tracking"):
            # Get mobile from 'phone_number' column
            u_data = next((u for u in users.data if u['name'] == selected_u), None)
            mobile = u_data['phone_number'] if u_data else None
            
            if mobile:
                entry = {
                    "project_id": selected_p, 
                    "site_id": s_info['Site ID'], 
                    "site_name": s_info['Site Name'],
                    "remark": rem, 
                    "user_name": selected_u, 
                    "user_mobile_number": str(mobile), 
                    "status": "Open"
                }
                supabase.table("site_tracking").insert(entry).execute()
                
                send_to_interakt(mobile, selected_p, s_info['Site ID'], s_info['Site Name'], rem)
                st.success(f"✅ मेसेज गेला आणि ट्रॅकिंग सुरु झाले!")
            else:
                st.error("User चा मोबाईल नंबर सापडला नाही!")

with col2:
    st.subheader("📋 चालू असलेले फॉलो-अप्स")
    active = supabase.table("site_tracking").select("*").eq("status", "Open").execute()
    
    if active.data:
        for t in active.data:
            with st.expander(f"📍 {t['site_name']} - {t['user_name']}"):
                st.write(f"**Remark:** {t['remark']}")
                if st.button("काम पूर्ण झाले (Close)", key=t['id']):
                    supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                    st.rerun()
    else:
        st.info("सध्या कोणतेही फॉलो-अप चालू नाहीत.")
