import streamlit as st
from supabase import create_client, Client
import requests
import pandas as pd

# --- 1. CONNECTION ---
# Visiontech Supabase Details
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_secret_h_TJpksUbg2Cr5DvpFz5rA_b8cGGTih"
supabase: Client = create_client(URL, KEY)

# --- 2. WHATSAPP FUNCTION (INTERAKT) ---
def send_to_interakt(mobile, project_id, site_id, site_name, remark):
    interakt_url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    # Mobile number clean karne
    clean_mobile = str(mobile).replace(" ", "").replace("+", "")
    if len(clean_mobile) == 10:
        clean_mobile = "91" + clean_mobile
        
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

# --- 3. UI SETUP ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking System")

# Navigation Tabs
tab1, tab2 = st.tabs(["➕ नवीन एन्ट्री (Add New)", "📋 चालू ट्रॅकिंग (Active List)"])

# --- TAB 1: ADD NEW ENTRY ---
with tab1:
    st.subheader("Search & Add Site for Tracking")
    
    # SEARCH & CLEAR functionality
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search_pid = st.text_input("📁 Project ID taka (उदा. VIS/P...)", key="main_search")
    with col_s2:
        st.write("##") # Alignment sathi
        if st.button("🧹 Clear Search", use_container_width=True):
            st.rerun()

    if search_pid:
        # 3000+ data aslyamule fakt match hoinara data fetch karne (Fast)
        res = supabase.table("VIS Portal Site Data").select("*").ilike("PROJECT ID", f"%{search_pid}%").execute()
        
        if res.data:
            # Match jhalela pahila data ghene
            s_info = res.data[0]
            st.success(f"✅ Site सापडली: {s_info.get('SITE NAME', 'N/A')}")
            
            # Team members fetch karne
            users = supabase.table("allowed_users").select("*").execute()
            
            with st.form("new_tracking_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Project ID", value=s_info.get('PROJECT ID', ''), disabled=True)
                    st.text_input("Site ID", value=s_info.get('SITE ID', ''), disabled=True)
                with c2:
                    st.text_input("Site Name", value=s_info.get('SITE NAME', ''), disabled=True)
                    u_names = [u['name'] for u in users.data] if users.data else ["No Users"]
                    sel_u = st.selectbox("Assign To (Team Member)", options=u_names)
                
                remark = st.text_area("काय काम बाकी आहे? (Remark for WhatsApp)")
                
                if st.form_submit_button("🚀 Start Tracking & Send Reminder"):
                    u_data = next((u for u in users.data if u['name'] == sel_u), None)
                    
                    entry = {
                        "project_id": s_info.get('PROJECT ID'),
                        "site_id": s_info.get('SITE ID'),
                        "site_name": s_info.get('SITE NAME'),
                        "remark": remark,
                        "user_name": sel_u,
                        "user_mobile_number": str(u_data['phone_number']) if u_data else "",
                        "status": "Open"
                    }
                    
                    try:
                        # 1. Supabase madhye save
                        supabase.table("site_tracking").insert(entry).execute()
                        
                        # 2. WhatsApp Message pathvane
                        if u_data:
                            send_to_interakt(u_data['phone_number'], s_info.get('PROJECT ID'), s_info.get('SITE ID'), s_info.get('SITE NAME'), remark)
                        
                        st.success(f"🎯 {sel_u} ला रिमाइन्डर पाठवला आणि ट्रॅकिंग सुरू झाले!")
                    except Exception as e:
                        st.error(f"Error: Supabase madhye 'site_tracking' table banva. {e}")
        else:
            st.warning("ह्या प्रोजेक्ट आयडीची माहिती सापडली नाही. कृपया आयडी तपासा.")

# --- TAB 2: ACTIVE TRACKING & CLOSE ---
with tab2:
    st.subheader("Current Active Follow-ups")
    
    # Active Search Filter
    search_active = st.text_input("🔍 Active list मध्ये शोधा (Site ID किंवा Team Name टाकून)")
    
    try:
        # Open cases fetch karne
        query = supabase.table("site_tracking").select("*").eq("status", "Open")
        
        if search_active:
            query = query.or_(f"site_id.ilike.%{search_active}%,user_name.ilike.%{search_active}%,project_id.ilike.%{search_active}%")
            
        active_res = query.execute()
        
        if active_res.data:
            # Reverse order sathi
            df_active = pd.DataFrame(active_res.data).sort_values(by='created_at', ascending=False)
            
            for _, t in df_active.iterrows():
                with st.expander(f"📍 {t['site_name']} | {t['project_id']} | {t['user_name']}"):
                    st.info(f"**Remark:** {t['remark']}")
                    st.write(f"**Assigned To:** {t['user_name']} ({t['user_mobile_number']})")
                    
                    # Close Button
                    if st.button(f"Close Tracking ✅", key=f"btn_{t['id']}"):
                        supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                        st.success(f"Tracking for {t['site_id']} is Closed!")
                        st.rerun()
        else:
            st.info("सध्या कोणतेही ट्रॅकिंग चालू नाही.")
            
    except Exception as e:
        st.error("Database मधून डेटा येत नाहीये. 'site_tracking' टेबल तपासा.")
