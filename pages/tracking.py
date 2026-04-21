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
def send_to_interakt(mobile, project_id, site_id, site_name, remark_text):
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
            "bodyValues": [
                str(project_id).strip(),
                str(site_id).strip(),
                str(site_name).strip(),
                str(remark_text).strip() if remark_text else "Reminder: Please update status."
            ]
        }
    }
    try:
        requests.post(interakt_url, json=payload, headers=headers, timeout=10)
    except:
        pass

# --- 3. UI SETUP ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking System")

tab1, tab2, tab3 = st.tabs(["➕ नवीन एन्ट्री (Add)", "📋 चालू ट्रॅकिंग (Active)", "🔔 Bulk Reminder"])

# --- TAB 1: ADD NEW ENTRY ---
with tab1:
    st.subheader("Search Project & Assign Team")
    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
    with col_s1:
        search_pid = st.text_input("Project ID टाकून सर्च करा", key="ip_pid")
    with col_s2:
        st.write("##")
        btn_search = st.button("🔍 Search Site", use_container_width=True)
    with col_s3:
        st.write("##")
        if st.button("🧹 Clear", use_container_width=True): st.rerun()

    if btn_search or search_pid:
        res = supabase.table("VIS Portal Site Data").select("*").ilike("PROJECT ID", f"%{search_pid}%").execute()
        if res.data:
            s_info = res.data[0]
            st.success(f"✅ साईट सापडली: {s_info.get('SITE NAME')}")
            users_res = supabase.table("allowed_users").select("*").execute()
            
            with st.form("tracking_v8", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    f_p_id, f_s_id = s_info.get('PROJECT ID', 'NA'), s_info.get('SITE ID', 'NA')
                    st.text_input("Project ID", value=f_p_id, disabled=True)
                    st.text_input("Site ID", value=f_s_id, disabled=True)
                with c2:
                    f_s_nm = s_info.get('SITE NAME', 'NA')
                    st.text_input("Site Name", value=f_s_nm, disabled=True)
                    u_map = {u['name']: u['phone_number'] for u in users_res.data}
                    selected_users = st.multiselect("Assign To", options=list(u_map.keys()))
                
                user_remark = st.text_area("काय काम बाकी आहे?")
                
                if st.form_submit_button("🚀 Start Tracking"):
                    for user_name in selected_users:
                        u_phone = u_map.get(user_name)
                        entry = {"project_id": f_p_id, "site_id": f_s_id, "site_name": f_s_nm, "remark": user_remark, "user_name": user_name, "user_mobile_number": str(u_phone), "status": "Open"}
                        supabase.table("site_tracking").insert(entry).execute()
                        if u_phone: send_to_interakt(u_phone, f_p_id, f_s_id, f_s_nm, user_remark)
                    st.success("✅ एन्ट्री सेव्ह झाली!")

# --- TAB 2: ACTIVE LIST ---
with tab2:
    st.subheader("Current Live Tracking")
    active_res = supabase.table("site_tracking").select("*").eq("status", "Open").execute()
    if active_res.data:
        df = pd.DataFrame(active_res.data)
        for _, t in df.iterrows():
            with st.expander(f"📍 {t['site_name']} | {t['user_name']}"):
                st.write(f"Remark: {t['remark']}")
                if st.button(f"Close Task ✅", key=f"cls_{t['id']}"):
                    supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                    st.rerun()
    else: st.info("No active tracking.")

# --- TAB 3: BULK REMINDER BUTTON ---
with tab3:
    st.subheader("Manual Bulk Reminder")
    st.write("Khalil button dabalya-var sarv active users na tyanchya pending sites cha WhatsApp reminder jail.")
    
    if st.button("📢 Send All Reminders (Daily 11 AM)", use_container_width=True):
        active_list = supabase.table("site_tracking").select("*").eq("status", "Open").execute()
        
        if active_list.data:
            count = 0
            with st.spinner("Reminders pathvat aahe..."):
                for item in active_list.data:
                    if item['user_mobile_number']:
                        send_to_interakt(
                            item['user_mobile_number'], 
                            item['project_id'], 
                            item['site_id'], 
                            item['site_name'], 
                            f"REMINDER: {item['remark']}"
                        )
                        count += 1
            st.success(f"✅ Total {count} Reminders pathvale ahet!")
        else:
            st.warning("Pathvnya-sathi kontihi active case nahiye.")
