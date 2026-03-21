import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# Excel Download Function
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")
st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

# 🎯 AAPKA EXACT TABLE SEQUENCE (Global)
mera_sequence = [
    'Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ',
    'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child',
    'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number',
    'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment'
]

# --- 3. MAIN SEARCH BOXES (LINE 1) ---
with st.form("search_form"):
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
    
    with c1: project_query = st.text_input("📁 Project No.")
    with c2: site_query = st.text_input("📍 Site ID")
    with c3: boq_query = st.text_input("📄 BOQ")
    with c4: dispatch_date = st.date_input("📅 Date", value=None)
    
    transporter_list = ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"]
    with c5: transporter = st.selectbox("🚚 Transporter", transporter_list)
    
    tsp_list = ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"]
    with c6: tsp_partner = st.selectbox("🤝 TSP Partner", tsp_list)
    
    with c7:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        submit_search = st.form_submit_button("🔍 Search")
        
    with c8:
        st.write("") 
        st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
        status_placeholder = st.empty() 

st.divider()

# --- 4. QUICK REPORTS SECTION (LINE 2) ---
st.markdown("#### 📊 Quick Reports & Downloads")
r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])

with r1:
    stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
with r2:
    boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed")
with r3:
    new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)


# --- LOGIC 1: STN PENDING SITES REPORT ---
if stn_pending_btn:
    status_placeholder.empty()
    st.info("⏳ Visiontech ka STN Pending data nikal rahe hain...")
    try:
        response = supabase.table("BOQ Report").select("*").ilike("Transporter", "%visiontech%").limit(10000).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            if 'Project Number' in df.columns and 'Item Code' in df.columns:
                # Pehle items ko merge karna
                agg_funcs = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col not in ['Project Number', 'Item Code']}
                items_df = df.groupby(['Project Number', 'Item Code'], as_index=False).agg(agg_funcs)

                # 🔥 STRICT EXACT LOGIC (Item Level Par)
                if 'Product' in items_df.columns and 'Issue From' in items_df.columns and 'Parent/Child' in items_df.columns:
                    pending_mask = (
                        (items_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & 
                        (items_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & 
                        (items_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent') &
                        (items_df['Qty A'] > 0) & 
                        (items_df['Qty B'] > 0) & 
                        (items_df['Qty C'] == 0)
                    )
                    
                    pending_df = items_df[pending_mask]
                    
                    if not pending_df.empty:
                        unique_projects = pending_df['Project Number'].nunique()
                        st.error(f"🚨 {unique_projects} Sites mein items ka STN Pending hai!")
                        
                        for col in qty_cols:
                            pending_df[col] = pending_df[col].astype(int)
                        
                        final_cols = [c for c in mera_sequence if c in pending_df.columns]
                        bache_hue_cols = [c for c in pending_df.columns if c not in final_cols]
                        pending_df = pending_df[final_cols + bache_hue_cols]

                        st.dataframe(pending_df, use_container_width=True, hide_index=True)
                        
                        csv = convert_df_to_csv(pending_df)
                        st.download_button(label="📥 Download Excel File", data=csv, file_name="STN_Pending_Sites.csv", mime="text/csv")
                    else:
                        st.success("✅ Wah! Visiontech ka koi bhi STN Pending nahi hai. Sab DONE hai!")
                else:
                    st.warning("Data mein 'Product', 'Issue From' ya 'Parent/Child' column missing hai.")
            else:
                st.warning("Database mein 'Project Number' ya 'Item Code' column nahi mila.")
        else:
            st.warning("Visiontech ka koi data database mein nahi mila.")
    except Exception as e:
        st.error(f"Error: {e}")

# --- LOGIC 2: NEW BOQ REPORT ---
elif new_boq_btn:
    if boq_date_input is None:
        st.warning("⚠️ Kripya 'Generate New BOQ' button ke theek pehle wale box mein Date select karein!")
    else:
        st.info(f"⏳ {boq_date_input.strftime('%d-%b-%Y')} ka BOQ data nikal rahe hain...")
        try:
            response = supabase.table("BOQ Report").select("*").limit(10000).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                
                if 'BOQ Date' in df.columns:
                    df['clean_date'] = df['BOQ Date'].astype(str).str.strip()
                    
                    d1 = boq_date_input.strftime("%d-%b-%Y")
                    d2 = boq_date_input.strftime("%Y-%m-%d")
                    d3 = boq_date_input.strftime("%d-%m-%Y")
                    d4 = boq_date_input.strftime("%d/%m/%Y")
                    
                    df['parsed'] = pd.to_datetime(df['clean_date'], errors='coerce').dt.date
                    
                    boq_df = df[
                        (df['parsed'] == boq_date_input) | 
                        (df['clean_date'].str.contains(d1, case=False, na=False)) |
                        (df['clean_date'].str.contains(d2, case=False, na=False)) |
                        (df['clean_date'].str.contains(d3, case=False, na=False)) |
                        (df['clean_date'].str.contains(d4, case=False, na=False))
                    ].copy()
                    
                    if not boq_df.empty:
                        if 'clean_date' in boq_df.columns: boq_df = boq_df.drop(columns=['clean_date'])
                        if 'parsed' in boq_df.columns: boq_df = boq_df.drop(columns=['parsed'])
                        
                        st.success(f"✅ Record Mil Gaya! ({len(boq_df)} Lines)")
                        
                        qty_cols = ['Qty A', 'Qty B', 'Qty C']
                        for col in qty_cols:
                            if col in boq_df.columns:
                                boq_df[col] = pd.to_numeric(boq_df[col], errors='coerce').fillna(0).astype(int)
                                
                        boq_df = boq_df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                        
                        final_cols = [c for c in mera_sequence if c in boq_df.columns]
                        bache_hue_cols = [c for c in boq_df.columns if c not in final_cols]
                        boq_df = boq_df[final_cols + bache_hue_cols]

                        st.dataframe(boq_df, use_container_width=True, hide_index=True)
                        
                        csv = convert_df_to_csv(boq_df)
                        st.download_button(label="📥 Download Excel File", data=csv, file_name=f"New_BOQ_{boq_date_input.strftime('%d-%b-%Y')}.csv", mime="text/csv")
                    else:
                        st.warning(f"❌ {boq_date_input.strftime('%d-%b-%Y')} ki date par koi data nahi mila. Supabase mein check karein ki data upload hua hai ya nahi.")
                else:
                    st.error("Database mein 'BOQ Date' column nahi mila.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- LOGIC 3: NORMAL SEARCH ---
elif submit_search:
    has_filter = False
    query = supabase.table("BOQ Report").select("*").limit(10000)
    
    if project_query:
        query = query.ilike("Project Number", f"%{project_query.strip()}%")
        has_filter = True
    if site_query:
        query = query.ilike("Site ID", f"%{site_query.strip()}%")
        has_filter = True
    if boq_query:
        query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        has_filter = True
    if dispatch_date:
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

                # Update Normal Search STN logic
                stn_df = df.copy()
                if 'Product' in stn_df.columns and 'Issue From' in stn_df.columns and 'Parent/Child' in stn_df.columns:
                    stn_df = stn_df[
                        (stn_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & 
                        (stn_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & 
                        (stn_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent')
                    ]

                total_a = int(stn_df['Qty A'].sum()) if 'Qty A' in stn_df.columns else 0
                total_b = int(stn_df['Qty B'].sum()) if 'Qty B' in stn_df.columns else 0
                total_c = int(stn_df['Qty C'].sum()) if 'Qty C' in stn_df.columns else 0

                if total_a > 0:
                    if total_a == total_b and total_c > 0:
                        status_placeholder.markdown("<div style='background-color: #d4edda; color: #155724; border: 1px solid #28a745; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px;'>✅ STN DONE</div>", unsafe_allow_html=True)
                    else:
                        status_placeholder.markdown("<div style='background-color: #f8d7da; color: #721c24; border: 1px solid #dc3545; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 14px;'>❌ STN PENDING</div>", unsafe_allow_html=True)

                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')

                for col in qty_cols:
                    if col in df.columns:
                        df[col] = df[col].astype(int)

                df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                
                final_cols = [c for c in mera_sequence if c in df.columns]
                bache_hue_cols = [c for c in df.columns if c not in final_cols]
                df = df[final_cols + bache_hue_cols]

                st.success(f"✅ Record Mil Gaya! ({len(df)} Unique Items)")
                st.dataframe(df, use_container_width=True, hide_index=True, column_config={"Item Description": st.column_config.TextColumn("Item Description", width="large")})
            else:
                st.warning("❌ Diye gaye filters par koi data nahi mila. Spelling check kar lijiye.")
        except Exception as e:
            st.error(f"Error detail: {e}")
    else:
        st.info("Kripya search karne ke liye kam se kam ek box mein detail bhariye.")
