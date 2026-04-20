import streamlit as st
from supabase import create_client, Client
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_secret_h_TJpksUbg2Cr5DvpFz5rA_b8cGGTih"
supabase: Client = create_client(URL, KEY)

# --- 2. WHATSAPP FUNCTION ---
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    if len(clean_mobile) == 10: clean_mobile = "91" + clean_mobile
        
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
        requests.post(interakt_url, json=payload, headers=headers, timeout=5)
    except: pass

# --- 3. UI SETUP ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking")

tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री (Add)", "📋 चालू ट्रॅकिंग (Active)"])

with tab1:
    st.subheader("Search Project for Tracking")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_pid = st.text_input("Project ID taka", placeholder="उदा. VIS/P-...", key="search_val")
    with col2:
        st.write("##")
        btn_search = st.button("🔍 Search", use_container_width=True)
    with col3:
        st.write("##")
        if st.button("🧹 Clear", use_container_width=True):
            st.rerun()

    if btn_search or search_pid:
        res = supabase.table("VIS Portal Site Data").select("*").ilike("PROJECT ID", f"%{search_pid}%").execute()
        
        if res.data:
            s_info = res.data[0]
            st.success(f"✅ Site सापडली: {s_info.get('SITE NAME')}")
            
            users_res = supabase.table("allowed_users").select("*").execute()
            
            with st.form("tracking_form_v5", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Project ID", value=s_info.get('PROJECT ID'), disabled=True)
                    st.text_input("Site ID", value=s_info.get('SITE ID'), disabled=True)
                with c2:
                    st.text_input("Site Name", value=s_info.get('SITE NAME'), disabled=True)
                    
                    # MULTIPLE USER SELECTION
                    u_map = {u['name']: u['phone_number'] for u in users_res.data} if users_res.data else {}
                    selected_users = st.multiselect("Assign To (Multiple Select Karu Shakta)", options=list(u_map.keys()))
                
                remark = st.text_area("Remark (काय काम बाकी आहे?)")
                
                if st.form_submit_button("🚀 Start Tracking & Send WhatsApp"):
                    # TIME CHECK (10 AM to 10 PM)
                    tz = pytz.timezone('Asia/Kolkata')
                    now = datetime.now(tz)
                    current_hour = now.hour
                    
                    if not (10 <= current_hour < 22):
                        st.error(f"❌ Follow-up chi vel sampali ahe! Shala/Office vel 10 AM te 10 PM ahe. (Ata chi vel: {now.strftime('%H:%M')})")
                    elif not selected_users:
                        st.warning("Kripaya kamit kami ek user select kara.")
                    else:
                        for user_name in selected_users:
                            phone = u_map.get(user_name)
                            entry = {
                                "project_id": s_info.get('PROJECT ID'),
                                "site_id": s_info.get('SITE ID'),
                                "site_name": s_info.get('SITE NAME'),
                                "remark": remark,
                                "user_name": user_name,
                                "user_mobile_number": str(phone),
                                "status": "Open"
                            }
                            try:
                                supabase.table("site_tracking").insert(entry).execute()
                                if phone:
                                    send_to_interakt(phone, s_info.get('PROJECT ID'), s_info.get('SITE ID'), s_info.get('SITE NAME'), remark)
                            except Exception as e:
                                st.error(f"Error saving for {user_name}: {e}")
                        
                        st.success(f"🎯 {', '.join(selected_users)} ला मेसेज गेले आणि ट्रॅकिंग सुरू झाले!")
        else:
            st.error("ह्या प्रोजेक्ट आयडीची माहिती सापडली नाही.")

# --- TAB 2: ACTIVE LIST ---
with tab2:
    st.subheader("Live Tracking Status")
    search_active = st.text_input("🔍 Active list मध्ये शोधा (ID किंवा नाव)")
    
    try:
        query = supabase.table("site_tracking").select("*").eq("status", "Open")
        if search_active:
            query = query.or_(f"site_id.ilike.%{search_active}%,user_name.ilike.%{search_active}%")
            
        active_res = query.execute()
        
        if active_res.data:
            df = pd.DataFrame(active_res.data).sort_values(by='created_at', ascending=False)
            for _, t in df.iterrows():
                with st.expander(f"📍 {t['site_name']} | {t['user_name']}"):
                    st.write(f"**Assigned To:** {t['user_name']} ({t['user_mobile_number']})")
                    st.info(f"**Pending:** {t['remark']}")
                    if st.button(f"Close Tracking ✅", key=f"close_{t['id']}"):
                        supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                        st.rerun()
        else:
            st.info("सध्या कोणतेही ट्रॅकिंग चालू नाही.")
    except:
        st.error("Data load होत नाहीये.")
