import streamlit as st
from supabase import create_client, Client
import requests
import pandas as pd
from datetime import datetime
import pytz

# --- 1. CONNECTION SETTINGS ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_secret_h_TJpksUbg2Cr5DvpFz5rA_b8cGGTih"
supabase: Client = create_client(URL, KEY)

# --- 2. FIXED WHATSAPP FUNCTION (INTERAKT) ---
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    
    # Mobile number cleaning
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    if len(clean_mobile) == 10: 
        clean_mobile = "91" + clean_mobile
        
    # Data Formatting for Interakt Template (Ensures no blank fields)
    p_id = str(project_id) if project_id else "N/A"
    s_id = str(site_id) if site_id else "N/A"
    s_nm = str(site_name) if site_name else "N/A"
    rem = str(remark) if remark else "माहिती लवकरात लवकर द्या."

    payload = {
        "fullPhoneNumber": clean_mobile,
        "type": "Template",
        "template": {
            "name": "pending_followup",
            "languageCode": "mr",
            "bodyValues": [p_id, s_id, s_nm, rem]
        }
    }
    
    try:
        # Using json=payload to ensure correct data transmission
        requests.post(interakt_url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        pass

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking System")

tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री (Add New)", "📋 चालू ट्रॅकिंग (Active List)"])

# --- TAB 1: DATA ENTRY ---
with tab1:
    st.subheader("Search Project & Assign Team")
    
    col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
    with col_s1:
        search_pid = st.text_input("Project ID टाकून सर्च करा", placeholder="उदा. VIS/P-...", key="ip_pid")
    with col_s2:
        st.write("##")
        btn_search = st.button("🔍 Search Site", use_container_width=True)
    with col_s3:
        st.write("##")
        if st.button("🧹 Clear", use_container_width=True):
            st.rerun()

    if btn_search or search_pid:
        res = supabase.table("VIS Portal Site Data").select("*").ilike("PROJECT ID", f"%{search_pid}%").execute()
        
        if res.data:
            s_info = res.data[0]
            st.success(f"✅ साईट सापडली: {s_info.get('SITE NAME')}")
            
            # Get Users for Assignment
            users_res = supabase.table("allowed_users").select("*").execute()
            
            with st.form("final_tracking_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Project ID", value=s_info.get('PROJECT ID'), disabled=True)
                    st.text_input("Site ID", value=s_info.get('SITE ID'), disabled=True)
                with c2:
                    st.text_input("Site Name", value=s_info.get('SITE NAME'), disabled=True)
                    
                    # MULTIPLE USER SELECT
                    u_map = {u['name']: u['phone_number'] for u in users_res.data} if users_res.data else {}
                    selected_users = st.multiselect("Assign To (एक किंवा अनेक निवडा)", options=list(u_map.keys()))
                
                remark = st.text_area("काय काम बाकी आहे? (Remark for WhatsApp)")
                
                if st.form_submit_button("🚀 Start Tracking & Send WhatsApp"):
                    # TIME RESTRICTION (10 AM to 10 PM IST)
                    tz = pytz.timezone('Asia/Kolkata')
                    now_ist = datetime.now(tz)
                    if not (10 <= now_ist.hour < 22):
                        st.error(f"❌ ऑफिस वेळ संपली आहे! (सकाळी १० ते रात्री १० मध्येच फॉलो-अप घेता येतो). आताची वेळ: {now_ist.strftime('%I:%M %p')}")
                    elif not selected_users:
                        st.warning("कृपया कमीत कमी एक टीम मेंबर निवडा.")
                    else:
                        for user_name in selected_users:
                            u_phone = u_map.get(user_name)
                            entry_data = {
                                "project_id": s_info.get('PROJECT ID'),
                                "site_id": s_info.get('SITE ID'),
                                "site_name": s_info.get('SITE NAME'),
                                "remark": remark,
                                "user_name": user_name,
                                "user_mobile_number": str(u_phone),
                                "status": "Open"
                            }
                            try:
                                # Save to Database
                                supabase.table("site_tracking").insert(entry_data).execute()
                                # Send WhatsApp
                                if u_phone:
                                    send_to_interakt(u_phone, s_info.get('PROJECT ID'), s_info.get('SITE ID'), s_info.get('SITE NAME'), remark)
                            except Exception as e:
                                st.error(f"Error for {user_name}: {e}")
                        
                        st.success(f"🎯 {', '.join(selected_users)} ला मेसेज गेले आणि ट्रॅकिंग सुरू झाले!")
        else:
            st.error("ह्या प्रोजेक्ट आयडीची माहिती सापडली नाही.")

# --- TAB 2: ACTIVE LIST ---
with tab2:
    st.subheader("Current Live Tracking")
    search_active = st.text_input("🔍 लिस्टमध्ये शोधा (ID किंवा नाव)")
    
    try:
        query = supabase.table("site_tracking").select("*").eq("status", "Open")
        if search_active:
            query = query.or_(f"site_id.ilike.%{search_active}%,user_name.ilike.%{search_active}%")
            
        active_res = query.execute()
        
        if active_res.data:
            df_active = pd.DataFrame(active_res.data)
            # Reverse order by creation time
            if 'created_at' in df_active.columns:
                df_active = df_active.sort_values(by='created_at', ascending=False)
            
            for _, t in df_active.iterrows():
                with st.expander(f"📍 {t['site_name']} | {t['user_name']}"):
                    st.info(f"**Remark:** {t['remark']}")
                    st.write(f"**Site ID:** {t['site_id']} | **User Mobile:** {t['user_mobile_number']}")
                    
                    if st.button(f"Close Tracking Task ✅", key=f"cls_{t['id']}"):
                        supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                        st.rerun()
        else:
            st.info("सध्या कोणतेही ट्रॅकिंग चालू नाही.")
    except:
        st.error("डेटा लोड होत नाहीये. कृपया 'site_tracking' टेबल तपासा.")
