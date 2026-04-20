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
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking")

tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री", "📋 चालू ट्रॅकिंग"])

with tab1:
    st.subheader("Search & Add Site")
    # 3000 entries sathi search box best ahe
    search_pid = st.text_input("📁 Project ID taka ani Enter daba (उदा. VIS/...)")
    
    # User list fetch karne
    users = supabase.table("allowed_users").select("*").execute()
    
    if search_pid:
        # Database madhun fakt tevhach data ghene jeva search kela jaail
        res = supabase.table("VIS Portal Site Data").select("*").ilike("PROJECT ID", f"%{search_pid}%").execute()
        
        if res.data:
            s_info = res.data[0] # Pahila match ghene
            st.success(f"Site Sapadli: {s_info.get('SITE NAME', 'N/A')}")
            
            with st.form("tracking_form_v2"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Project ID", value=s_info.get('PROJECT ID', ''), disabled=True)
                    st.text_input("Site ID", value=s_info.get('SITE ID', ''), disabled=True)
                with col2:
                    st.text_input("Site Name", value=s_info.get('SITE NAME', ''), disabled=True)
                    u_names = [u['name'] for u in users.data] if users.data else []
                    sel_u = st.selectbox("Assign To", options=u_names)
                
                remark = st.text_area("काय माहिती/डॉक्युमेंट बाकी आहे?")
                
                if st.form_submit_button("🚀 Start Tracking & Send WhatsApp"):
                    u_data = next((u for u in users.data if u['name'] == sel_u), None)
                    if u_data:
                        entry = {
                            "project_id": s_info.get('PROJECT ID'),
                            "site_id": s_info.get('SITE ID'),
                            "site_name": s_info.get('SITE NAME'),
                            "remark": remark,
                            "user_name": sel_u,
                            "user_mobile_number": str(u_data['phone_number']),
                            "status": "Open"
                        }
                        supabase.table("site_tracking").insert(entry).execute()
                        
                        # WhatsApp Message
                        status = send_to_interakt(u_data['phone_number'], s_info.get('PROJECT ID'), s_info.get('SITE ID'), s_info.get('SITE NAME'), remark)
                        st.success(f"✅ Tracking suru jhale! Reminder user la gela ahe.")
                        st.rerun()
        else:
            st.error("ह्या Project ID ची कोणतीही माहिती सापडली नाही.")

with tab2:
    st.subheader("Active Follow-ups")
    # Open status aslele active records
    active = supabase.table("site_tracking").select("*").eq("status", "Open").order('created_at', descending=True).execute()
    
    if active.data:
        for t in active.data:
            with st.expander(f"📍 {t['site_name']} ({t['project_id']}) - {t['user_name']}"):
                st.write(f"**Remark:** {t['remark']}")
                st.write(f"**Mobile:** {t['user_mobile_number']}")
                if st.button(f"Close Tracking for {t['site_id']}", key=f"close_{t['id']}"):
                    supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                    st.success("Tracking Closed!")
                    st.rerun()
    else:
        st.info("सध्या कोणतेही ट्रॅकिंग चालू नाही.")
