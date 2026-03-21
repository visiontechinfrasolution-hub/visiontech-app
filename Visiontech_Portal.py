import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")
st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

# --- 3. SINGLE LINE SEARCH BOXES & BUTTONS ---
with st.form("search_form"):
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.2, 1.2, 1.1, 1.3, 1.2, 0.8, 1.2, 0.9])
    
    with c1: project_query = st.text_input("📁 Project No.")
    with c2: site_query = st.text_input("📍 SITE ID")
    
    # DATE PICKER 
    with c3: dispatch_date = st.date_input("📅 Date", value=None)
    
    # TRANSPORTER DROPDOWN
    transporter_list = ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati", "Blue Dart"]
    with c4: transporter = st.selectbox("🚚 Transporter", transporter_list)
    
    with c5: tsp_partner = st.text_input("🤝 TSP Partner")
    
    with c6:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        submit_search = st.form_submit_button("🔍 Search")
        
    with c7:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        pending_report = st.form_submit_button("🚨 Pending Report")
        
    with c8:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        status_placeholder = st.empty() 

# --- 4. LOGIC FOR PENDING REPORT (VISIONTECH) ---
if pending_report:
    status_placeholder.empty()
    st.info("⏳ Visiontech ka STN Pending data nikal rahe hain, kripya thoda intezar karein...")
    try:
        response = supabase.table("BOQ Report").select("*").ilike("Transporter", "%visiontech%").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            if 'Project Number' in df.columns:
                grouped = df.groupby('Project Number', as_index=False)[qty_cols].sum()
                pending_mask = (grouped['Qty A'] > 0) & ((grouped['Qty A'] != grouped['Qty B']) | (grouped['Qty A'] != grouped['Qty C']))
                pending_df = grouped[pending_mask]
                
                if not pending_df.empty:
                    pending_df['Status'] = '❌ PENDING'
                    st.error(f"🚨 Visiontech ke {len(pending_df)} Projects ka STN Pending hai!")
                    for col in qty_cols:
                        pending_df[col] = pending_df[col].astype(int)
                    st.dataframe(pending_df, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ Wah! Visiontech ka koi bhi STN Pending nahi hai. Sab DONE hai!")
            else:
                st.warning("Database mein 'Project Number' column nahi mila.")
        else:
            st.warning("Visiontech ka koi data database mein nahi mila.")
    except Exception as e:
        st.error(f"Error fetching report: {e}")

# --- 5. LOGIC FOR NORMAL SEARCH ---
elif submit_search:
    has_filter = False
    query = supabase.table("BOQ Report").select("*")
    
    if project_query:
        query = query.ilike("Project Number", f"%{project_query.strip()}%")
        has_filter = True
    if site_query:
        query = query.ilike("SITE ID", f"%{site_query.strip()}%")
        has_filter = True
    if dispatch_date:
        # 🚨 YAHAN FIX KIYA HAI: 'ilike' hata kar exact Date match ('.eq') lagaya hai
        date_str = dispatch_date.strftime("%Y-%m-%d")
        query = query.eq("Dispatch Date", date_str)
        has_filter = True
    if transporter:
        query = query.ilike("Transporter", f"%{transporter.strip()}%")
        has_filter = True
    if tsp_partner:
        query = query.ilike("TSP Partner Name", f"%{tsp_partner.strip()}%")
        has_filter = True

    if has_filter:
        try:
            response = query.execute()
            
            if response.data:
                df = pd.DataFrame(response.data)

                # --- QTY SUM & DUPLICATE HATANA ---
                qty_cols = ['Qty A', 'Qty B', 'Qty C']
                for col in qty_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                if 'Item Code' in df.columns:
                    agg_funcs = {}
                    for col in df.columns:
                        if col in qty_cols:
                            agg_funcs[col] = 'sum'
                        elif col != 'Item Code':
                            agg_funcs[col] = 'first' 

                    df = df.groupby('Item Code', as_index=False).agg(agg_funcs)

                    original_cols = [c for c in response.data[0].keys() if c in df.columns]
                    df = df[original_cols]

                # --- STN DONE / PENDING LOGIC ---
                total_a = int(df['Qty A'].sum()) if 'Qty A' in df.columns else 0
                total_b = int(df['Qty B'].sum()) if 'Qty B' in df.columns else 0
                total_c = int(df['Qty C'].sum()) if 'Qty C' in df.columns else 0

                if total_a > 0:
                    if total_a == total_b and total_a == total_c:
                        status_placeholder.markdown("<div style='background-color: #d4edda; color: #155724; border: 1px solid #28a745; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px;'>✅ STN DONE</div>", unsafe_allow_html=True)
                    else:
                        status_placeholder.markdown("<div style='background-color: #f8d7da; color: #721c24; border: 1px solid #dc3545; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px;'>❌ STN PENDING</div>", unsafe_allow_html=True)

                # --- FORMATTING: DATE ---
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')

                # --- FORMATTING: DECIMALS HATANA (.0) ---
                for col in qty_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(int)

                df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')

                # --- 🎯 TABLE SEQUENCE CHANGE ---
                mera_sequence = [
                    'Sr. No.', 'SITE ID', 'Product', 'Transaction Type', 'Project Number', 'BOQ',
                    'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Parent',
                    'Dispatch Date', 'Line Status', 'Transporter', 'TSP Partner Name',
                    'LR Number', 'Challan Number', 'Vehicle Number', 'Item Category', 'SRN BOQ'
                ]
                
                final_cols = [c for c in mera_sequence if c in df.columns]
                bache_hue_cols = [c for c in df.columns if c not in final_cols]
                df = df[final_cols + bache_hue_cols]

                st.success(f"✅ Record Mil Gaya! ({len(df)} Unique Items)")
                
                # --- 🎯 ITEM DESCRIPTION WRAPPING ---
                st.dataframe(
                    df, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Item Description": st.column_config.TextColumn(
                            "Item Description",
                            width="large", 
                        )
                    }
                )
                
            else:
                st.warning("❌ Diye gaye filters par koi data nahi mila. Spelling check kar lijiye.")
                
        except Exception as e:
            st.error(f"Error detail: {e}")
    else:
        st.info("Kripya search karne ke liye kam se kam ek box mein detail bhariye.")
