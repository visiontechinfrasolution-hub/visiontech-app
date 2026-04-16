import streamlit as st
import pandas as pd
import requests
import json
import time

def show(supabase):
    st.markdown("<h3 style='text-align: center; color: #E11D48;'>📢 RFAI Billing Pending</h3>", unsafe_allow_html=True)
    
    # --- CONFIGURATION ---
    INTERAKT_API_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="
    TEMPLATE_NAME = "wccpending" 
    TARGET_NUMBERS = ["919960843473", "919552273181"] 

    rfai_list = [
        "Build Complete by BV", "Build Complete by PM", "Pending RFAI",
        "Post RFAI Hold", "RFAI Notice Accepted", 
        "RFAI Notice Deemed Accepted", "RFAI Notice Rejected"
    ]

    col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
    lang_choice = col_1.selectbox("Template Language", ["mr", "en"], index=0)

    if "billing_df" not in st.session_state:
        st.session_state.billing_df = pd.DataFrame()

    # पायरी १: डेटा तपासणे
    if col_2.button("🔍 Step 1: Check Data", use_container_width=True):
        try:
            res_bill = supabase.table("VIS Portal Site Data").select("*").execute()
            if res_bill.data:
                df_raw = pd.DataFrame(res_bill.data)
                df_raw.columns = df_raw.columns.str.strip()
                mask = (df_raw['RFAI STATUS'].isin(rfai_list)) & (df_raw['WCC NO.'].astype(str).str.strip().isin(['-', '', 'nan', 'None']))
                st.session_state.billing_df = df_raw[mask]
                if st.session_state.billing_df.empty:
                    st.warning("कोणतीही Pending साईट सापडली नाही.")
                else:
                    st.success(f"सापडल्या: {len(st.session_state.billing_df)} साईट्स")
        except Exception as e:
            st.error(f"Error: {e}")

    # पायरी २: मेसेज पाठवणे
    if not st.session_state.billing_df.empty:
        if col_3.button("🚀 Step 2: SEND ALL", type="primary", use_container_width=True):
            total_sites = len(st.session_state.billing_df)
            progress_bar = st.progress(0)
            status_info = st.empty()
            success_count = 0
            
            for i, (idx, row) in enumerate(st.session_state.billing_df.iterrows()):
                site_id = row.get('SITE ID', 'Unknown')
                status_info.info(f"📤 मेसेज पाठवत आहे ({i+1}/{total_sites}): {site_id}")

                body_values = [
                    str(row.get('DEPARTMENT', '-')), str(row.get('OPERATOR', '-')),
                    str(row.get('PROJECT ID', '-')), str(row.get('PROJECT NAME', '-')),
                    str(row.get('SITE ID', '-')), str(row.get('SITE NAME', '-')),
                    str(row.get('CLUSTER', '-')), str(row.get('SITE STATUS', '-')),
                    str(row.get('PRODUCT', '-')), str(row.get('PO NO.', '-')),
                    str(row.get('PO STATUS', '-')), str(row.get('RFAI STATUS', '-')),
                    str(row.get('WORK DESCRIPTION', '-'))
                ]

                for mobile in TARGET_NUMBERS:
                    url = "https://api.interakt.ai/v1/public/message/"
                    headers = {"Authorization": f"Basic {INTERAKT_API_KEY}", "Content-Type": "application/json"}
                    
                    payload = {
                        "fullPhoneNumber": mobile,
                        "type": "Template",
                        "template": {
                            "name": TEMPLATE_NAME,
                            "languageCode": lang_choice,
                            "bodyValues": body_values
                        }
                    }

                    try:
                        r = requests.post(url, headers=headers, data=json.dumps(payload))
                        if r.status_code in [200, 201, 202]:
                            success_count += 1
                        else:
                            st.error(f"❌ Error {site_id}: {r.json().get('message', r.text)}")
                    except: pass
                    time.sleep(1) 

                progress_bar.progress((i + 1) / total_sites)
                time.sleep(1) 

            status_info.empty()
            st.success(f"✅ पूर्ण झाले! यशस्वी मेसेज: {success_count}")

    if col_4.button("🛑 STOP"):
        st.rerun()

    st.divider()
    if not st.session_state.billing_df.empty:
        st.write("### Pending Billing List")
        st.dataframe(st.session_state.billing_df[['SITE ID', 'SITE NAME', 'RFAI STATUS', 'WCC NO.']], use_container_width=True, hide_index=True)
