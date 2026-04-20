import streamlit as st
from supabase import create_client, Client
import requests
import pandas as pd

# --- CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_secret_h_TJpksUbg2Cr5DvpFz5rA_b8cGGTih"
supabase: Client = create_client(URL, KEY)

# --- INTERAKT FUNCTION ---
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    payload = {
        "fullPhoneNumber": clean_mobile,
        "type": "Template",
        "template": {
            "name": "pending_followup",
            "languageCode": "mr",
            "bodyValues": [str(project_id), str(site_id), str(site_name), str(remark)]
        }
    }
    try:
        res = requests.post(interakt_url, json=payload, headers=headers)
        return res.status_code
    except:
        return 500

# --- UI ---
st.title("🛰️ Visiontech Site Tracking")
tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री", "📋 चालू ट्रॅकिंग"])

with tab1:
    sites = supabase.table("VIS Portal Site Data").select("*").execute()
    users = supabase.table("allowed_users").select("*").execute()
    
    with st.form("tracking_form"):
        p_ids = [s['PROJECT ID'] for s in sites.data] if sites.data else []
        sel_p = st.selectbox("Project ID निवडा", options=p_ids)
        s_info = next((s for s in sites.data if s['PROJECT ID'] == sel_p), None)
        
        st.text_input("Site ID", value=s_info['SITE ID'] if s_info else "", disabled=True)
        st.text_input("Site Name", value=s_info['SITE NAME'] if s_info else "", disabled=True)
        
        u_names = [u['name'] for u in users.data] if users.data else []
        sel_u = st.selectbox("Assign To", options=u_names)
        rem = st.text_area("Remark")
        
        if st.form_submit_button("Start Tracking"):
            u_data = next((u for u in users.data if u['name'] == sel_u), None)
            if u_data and s_info:
                entry = {
                    "project_id": sel_p, "site_id": s_info['Site ID'], "site_name": s_info['Site Name'],
                    "remark": rem, "user_name": sel_u, "user_mobile_number": str(u_data['phone_number']), "status": "Open"
                }
                supabase.table("site_tracking").insert(entry).execute()
                send_to_interakt(u_data['phone_number'], sel_p, s_info['Site ID'], s_info['Site Name'], rem)
                st.success("✅ ट्रॅकिंग सुरू झाले!")
                st.rerun()

with tab2:
    active = supabase.table("site_tracking").select("*").eq("status", "Open").execute()
    if active.data:
        for t in active.data:
            with st.expander(f"📍 {t['site_name']} ({t['user_name']})"):
                st.write(f"Remark: {t['remark']}")
                if st.button("Close Task", key=t['id']):
                    supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                    st.rerun()
    else:
        st.info("कोणतेही ट्रॅकिंग चालू नाही.")
