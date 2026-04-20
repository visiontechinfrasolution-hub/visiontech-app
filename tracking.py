import streamlit as st
from supabase import create_client, Client
import requests
import pandas as pd

# --- CONFIGURATION ---
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

# --- UI SETUP ---
st.set_page_config(page_title="Visiontech Tracking", layout="wide")
st.title("🛰️ Visiontech Site Tracking Dashboard")

# Tabs banvun dashboard organize karne
tab1, tab2 = st.tabs(["➕ Navin Entry Kara", "📋 Active Tracking Bagha"])

# --- TAB 1: DATA ENTRY ---
with tab1:
    st.subheader("Navin Follow-up suru kara")
    
    # Data fetch karne
    sites = supabase.table("VIS Portal Site Data").select("*").execute()
    users = supabase.table("allowed_users").select("*").execute()
    
    with st.form("tracking_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            p_ids = [s['Project ID'] for s in sites.data] if sites.data else []
            selected_p = st.selectbox("Project ID निवडा", options=p_ids)
            
            s_info = next((s for s in sites.data if s['Project ID'] == selected_p), None)
            st.text_input("Site ID", value=s_info['Site ID'] if s_info else "", disabled=True)
            st.text_input("Site Name", value=s_info['Site Name'] if s_info else "", disabled=True)
        
        with col2:
            u_names = [u['name'] for u in users.data] if users.data else []
            selected_u = st.selectbox("Assign To (User)", options=u_names)
            remark = st.text_area("Remark / Pending Work Detail", placeholder="Kahi document baki asel tar ithe liha...")
        
        submit = st.form_submit_button("Tracking Suru Kara")
        
        if submit:
            u_data = next((u for u in users.data if u['name'] == selected_u), None)
            mobile = u_data['phone_number'] if u_data else None
            
            if mobile and s_info:
                # 1. Supabase madhye insert
                entry = {
                    "project_id": selected_p, "site_id": s_info['Site ID'], "site_name": s_info['Site Name'],
                    "remark": remark, "user_name": selected_u, "user_mobile_number": str(mobile), "status": "Open"
                }
                supabase.table("site_tracking").insert(entry).execute()
                
                # 2. Interakt Message
                send_to_interakt(mobile, selected_p, s_info['Site ID'], s_info['Site Name'], remark)
                st.success(f"✅ Entry saved! {selected_u} la reminder suru jhale.")
                st.rerun()
            else:
                st.error("Data bhalatana kahi tari chukle aahe!")

# --- TAB 2: MONITOR & CLOSE ---
with tab2:
    st.subheader("Current Active Follow-ups")
    
    # Open status aslele data ghene
    active_data = supabase.table("site_tracking").select("*").eq("status", "Open").order('created_at', descending=True).execute()
    
    if active_data.data:
        # Table format madhye baghnyasathi (Optional)
        df = pd.DataFrame(active_data.data)
        st.dataframe(df[['project_id', 'site_id', 'site_name', 'user_name', 'remark']], use_container_width=True)
        
        st.divider()
        st.write("### Actions: Kaam purna jhale asel tar 'Close' kara")
        
        # Grid format madhye active items dakhvane
        cols = st.columns(2)
        for i, t in enumerate(active_data.data):
            with cols[i % 2]:
                with st.expander(f"📍 {t['site_name']} ({t['user_name']})", expanded=True):
                    st.info(f"**Remark:** {t['remark']}")
                    st.write(f"**Site ID:** {t['site_id']} | **Project:** {t['project_id']}")
                    
                    if st.button(f"Close Tracking ✅", key=f"btn_{t['id']}"):
                        supabase.table("site_tracking").update({"status": "Closed"}).eq("id", t['id']).execute()
                        st.success(f"Site {t['site_id']} che tracking band jhale!")
                        st.rerun()
    else:
        st.info("Sadhya kontihi tracking active nahiye. Navin entry kara!")
