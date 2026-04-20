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

# --- 2. FINAL FIXED WHATSAPP FUNCTION ---
def send_to_interakt(mobile, project_id, site_id, site_name, remark_text):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    if len(clean_mobile) == 10: 
        clean_mobile = "91" + clean_mobile
        
    # Strictly using the remark_text passed from the form
    p_id = str(project_id).strip() if project_id else "NA"
    s_id = str(site_id).strip() if site_id else "NA"
    s_nm = str(site_name).strip() if site_name else "NA"
    # Jar remark kharch r रिकामी asel tarach default vapra, nahi tar form madhla vapra
    rem = str(remark_text).strip() if remark_text else "माहिती लवकरात लवकर द्या."

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
        requests.post(interakt_url, json=payload, headers=headers, timeout=15)
    except:
        pass

# --- 3. UI SETUP ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking System")

tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री (Add New)", "📋 चालू ट्रॅकिंग (Active List)"])

# --- TAB 1: ADD NEW ENTRY ---
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
            
            users_res = supabase.table("allowed_users").select("*").execute()
            
            # Form chya aat remark handle karne
            with st.form("final_tracking_form_v7", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    f_p_id = s_info.get('PROJECT ID', 'NA')
                    f_s_id = s_info.get('SITE ID', 'NA')
                    st.text_input("Project ID", value=f_p_id, disabled=True)
                    st.text_input("Site ID", value=f_s_id, disabled=True)
                with c2:
                    f_s_nm = s_info.get('SITE NAME', 'NA')
                    st.text_input("Site Name", value=f_s_nm, disabled=True)
                    
                    u_map = {u['name']: u['phone_number'] for u in users_res.data} if users_res.data else {}
                    selected_users = st.multiselect("Assign To", options=list(u_map.keys()))
                
                # IMPORTANT: Form madhla remark variable
                user_remark = st.text_area("काय काम बाकी आहे? (Remark)")
                
                if st.form_submit_button("🚀 Start Tracking & Send WhatsApp"):
                    tz = pytz.timezone('Asia/Kolkata')
                    now_ist = datetime.now(tz)
                    
                    if not (10 <= now_ist.hour < 22):
                        st.error(f"❌ ऑफिस वेळ संपली आहे! वेळ: {now_ist.strftime('%I:%M %p')}")
                    elif not selected_users:
                        st.warning("कृपया टीम मेंबर निवडा.")
                    else:
                        for user_name in selected_users:
                            u_phone = u_map.get(user_name)
                            # Database entry
                            entry_data = {
                                "project_id": f_p_id,
                                "site_id": f_s_id,
                                "site_name": f_s_nm,
                                "remark": user_remark,
                                "user_name": user_name,
                                "user_mobile_number": str(u_phone),
                                "status": "Open"
                            }
                            try:
                                supabase.table("site_tracking").insert(entry_data).execute()
                                # WhatsApp logic - passing user_remark directly
                                if u_phone:
                                    send_to_interakt(u_phone, f_p_id, f_s_id, f_s_nm, user_remark)
                            except Exception as e:
                                st.error(f"Error for {user_name}: {e}")
                        
                        st.success(f"🎯 फॉलो-अप सुरू झाला आणि मेसेज पाठवले!")
        else:
            st.error("ह्या प्रोजेक्ट आयडीची माहिती सापडली नाही.")

# --- TAB 2: ACTIVE LIST ---
with tab2:
    st.subheader("Current Live Tracking")
    search_active = st.text_input("🔍 लिस्टमध्ये शोधा")
    
    try:
        active_res = supabase.table("site_tracking").select("*").eq("status", "Open").execute()
        if active_res.data:
            df_active = pd.DataFrame(active_res.data).sort_values(by='created_at', ascending=False)
            for _, t in df_active.iterrows():
                with st.expander(f"📍 {t['site_name']} | {t['user_name']}"):
                    st.write(f"**Remark:** {t['remark']}")
                    if st.button(f"Close Task ✅", key=f"cls_{t['id']}"):
                        supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                        st.rerun()
        else:
            st.info("सध्या कोणतेही ट्रॅकिंग चालू नाही.")
    except:
        st.error("डेटा लोड होत नाहीये.")
