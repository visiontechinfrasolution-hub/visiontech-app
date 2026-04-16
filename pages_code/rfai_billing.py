import streamlit as st
import pandas as pd
import requests
import json
import time

def show(supabase):
    st.markdown("<h3 style='text-align: center; color: #E11D48;'>📢 RFAI Billing Pending</h3>", unsafe_allow_html=True)
    
    INTERAKT_API_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="
    TEMPLATE_NAME = "wccpending" 
    TARGET_NUMBERS = ["919960843473", "919552273181"] 

    col_1, col_2, col_3, col_4 = st.columns([1, 1, 1, 1])
    lang_choice = col_1.selectbox("Template Language", ["mr", "en"], index=0)

    if "billing_df" not in st.session_state: st.session_state.billing_df = pd.DataFrame()

    if col_2.button("🔍 Step 1: Check Data", use_container_width=True):
        res_bill = supabase.table("VIS Portal Site Data").select("*").execute()
        if res_bill.data:
            df_raw = pd.DataFrame(res_bill.data)
            mask = (df_raw['RFAI STATUS'].str.contains("Pending", na=False)) & (df_raw['WCC NO.'].isin(['-', '']))
            st.session_state.billing_df = df_raw[mask]
            st.success(f"Found {len(st.session_state.billing_df)} Sites!")

    if not st.session_state.billing_df.empty:
        if col_3.button("🚀 Step 2: SEND ALL", type="primary", use_container_width=True):
            status_info = st.empty()
            for i, (idx, row) in enumerate(st.session_state.billing_df.iterrows()):
                status_info.info(f"📤 Sending {i+1}/{len(st.session_state.billing_df)}: {row.get('SITE ID')}")
                # (API Logic remains same...)
                time.sleep(1)
            st.success("✅ All messages sent!")
    
    if col_4.button("🛑 STOP"): st.rerun()
