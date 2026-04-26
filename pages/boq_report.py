import streamlit as st
import pandas as pd
from supabase import create_client
import io
import random
from datetime import datetime, timedelta

# --- SUPABASE CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- BACK BUTTON ---
st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
if st.button("⬅️ Dashboard"):
    st.switch_page("Visiontech_Portal.py")
st.markdown("</div>", unsafe_allow_html=True)
st.divider()

# =====================================================================
# 🟩 TAB 1: BOQ REPORT (3 Dedicated Sections - 0% Logic Change)
# =====================================================================
st.markdown("""
    <style>
        [data-testid="stDataFrame"] { border: 2px solid #1E3A8A; border-radius: 12px; }
        div.stButton > button:first-child {
            height: 60px !important; font-size: 20px !important; font-weight: bold !important;
            background-color: #1E3A8A !important; color: white !important; border-radius: 12px !important;
            width: 100% !important;
        }
        .table-header { 
            background-color: #1E3A8A; color: white; padding: 10px; border-radius: 8px; 
            margin-top: 25px; text-align: center; font-weight: bold; 
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🔍 Visiontech Infra Solutions</h2>", unsafe_allow_html=True)

mera_sequence = ['Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ', 'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child', 'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number', 'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment']

# --- ०. तुमचे मूळ फंक्शन्स (०% बदल) ---
def process_boq_data(raw_data):
    if not raw_data: return pd.DataFrame()
    df_res = pd.DataFrame(raw_data)
    df_res.columns = [str(c).strip() for c in df_res.columns]
    qty_cols = ['Qty A', 'Qty B', 'Qty C']
    for col in qty_cols:
        if col in df_res.columns:
            df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0).astype(int)
    if 'Item Code' in df_res.columns and 'Project Number' in df_res.columns:
        df_res['TempKey'] = df_res.apply(lambda x: x.get('Sr. No.', random.random()) if str(x.get('Item Code','')).strip() == '' else x['Item Code'], axis=1)
        agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df_res.columns if col not in ['Project Number', 'TempKey']}
        df_res = df_res.groupby(['Project Number', 'TempKey'], as_index=False).agg(agg_dict)
    for col in ['Dispatch Date', 'BOQ Date']:
        if col in df_res.columns:
            df_res[col] = pd.to_datetime(df_res[col], errors='coerce').dt.strftime('%d-%b-%Y')
    return df_res.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')

def fetch_complete_data(query_builder):
    all_records = []
    page_size = 1000 
    offset = 0
    while True:
        response = query_builder.range(offset, offset + page_size - 1).execute()
        batch = response.data
        if not batch: break
        all_records.extend(batch)
        if len(batch) < page_size: break
        offset += page_size
    return all_records

# --- १. तुमच्या मागणीनुसार ३ मुख्य पेजेस (Tabs) ---
t1, t2, t3 = st.tabs([
    "🔎 Single Site Search", 
    "📅 Date Range Reports", 
    "📤 Bulk Project Upload"
])

# --- PAGE 1: Single Site / Project Search ---
with t1:
    with st.form("search_form_v27", clear_on_submit=False):
        st.markdown("#### 🔎 Single Site / Project Search")
        c1, c2, c3 = st.columns(3)
        with c1: project_query = st.text_input("📁 Project Number", key="boq_p_v27")
        with c2: site_query = st.text_input("📍 Site ID", key="boq_s_v27")
        with c3: boq_query = st.text_input("📄 BOQ Number", key="boq_b_v27")
        submit_search = st.form_submit_button("🔍 SEARCH SINGLE DATA")

    if submit_search:
        st.balloons()
        with st.spinner('शोधत आहे...'):
            query = supabase.table("BOQ Report").select("*")
            if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
            if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
            if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
            
            try:
                data = fetch_complete_data(query)
                df_final = process_boq_data(data)
            except Exception as e:
                st.error(f"Supabase Fetch Error: {e}")
                df_final = pd.DataFrame()
            
            if not df_final.empty:
                st.success(f"✅ {len(df_final)} Records Found!")

                # --- UPDATED LOGIC: STN STATUS (Qty B > 0 Only) ---
                try:
                    # Step 1: Filter Capex AND Parent items only
                    mask = (
                        df_final['Product'].astype(str).str.contains('Capex', case=False, na=False) & 
                        df_final['Parent/Child'].astype(str).str.contains('Parent', case=False, na=False)
                    )
                    df_status_check = df_final[mask].copy()

                    if not df_status_check.empty:
                        # Qty numeric conversion
                        df_status_check['Qty A'] = pd.to_numeric(df_status_check['Qty A'], errors='coerce').fillna(0)
                        df_status_check['Qty B'] = pd.to_numeric(df_status_check['Qty B'], errors='coerce').fillna(0)
                        df_status_check['Qty C'] = pd.to_numeric(df_status_check['Qty C'], errors='coerce').fillna(0)

                        # logic: Sirf wahi rows consider karo jahan Qty B > 0 hai (Material liya gaya hai)
                        df_dispatched = df_status_check[df_status_check['Qty B'] > 0]

                        if not df_dispatched.empty:
                            # Condition: Jitna liya (Qty B) utna hi mila (Qty C) hona chahiye
                            is_stn_done = all(df_dispatched['Qty B'] == df_dispatched['Qty C'])

                            if is_stn_done:
                                st.markdown("""
                                    <div style='background-color: #DCFCE7; padding: 20px; border-radius: 12px; border: 2px solid #166534; text-align: center;'>
                                        <h1 style='color: #166534; margin: 0;'>✅ STN Done</h1>
                                        <p style='color: #166534; margin: 0; font-weight: bold;'>Jitna material liya (Qty B), utna mil gaya (Qty C)!</p>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                    <div style='background-color: #FEE2E2; padding: 20px; border-radius: 12px; border: 2px solid #991B1B; text-align: center;'>
                                        <h1 style='color: #991B1B; margin: 0;'>❌ STN Pending</h1>
                                        <p style='color: #991B1B; margin: 0; font-weight: bold;'>Liya hua material (Qty B) aur mila hua material (Qty C) match nahi hai.</p>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("ℹ️ Is Project mein abhi koi Capex-Parent material 'Liya' (Qty B > 0) nahi gaya hai.")
                    else:
                        st.info("ℹ️ Is Search mein koi Capex-Parent item nahi mila.")
                    st.write("") 
                except Exception as e:
                    st.error(f"Logic Error: {e}")
                # --- END OF UPDATED LOGIC ---

                st.dataframe(df_final[[c for c in mera_sequence if c in df_final.columns]], use_container_width=True, hide_index=True, height=400)
            else: 
                st.warning("कोणतीही माहिती सापडली नाही.")

# --- PAGE 2: Date Range Dispatch Reports ---
with t2:
    with st.form("date_range_filter_v27"):
        st.markdown("#### 📅 Date Range Dispatch Reports")
        c_from, c_to, c_btn = st.columns([1.5, 1.5, 1])
        with c_from: start_date = st.date_input("From Date", value=datetime.now().date(), key="d_from_v27")
        with c_to: end_date = st.date_input("To Date", value=datetime.now().date(), key="d_to_v27")
        with c_btn: btn_range_gen = st.form_submit_button("🚀 GENERATE DATA")

    if btn_range_gen:
        st.balloons()
        delta = end_date - start_date
        date_list = [(start_date + timedelta(days=i)).strftime('%d-%b-%Y') for i in range(delta.days + 1)]
        with st.spinner('डेटा फेच होत आहे...'):
            try:
                query = supabase.table("BOQ Report").select("*").in_('"Dispatch Date"', date_list)
                data = fetch_complete_data(query)
                if data:
                    df_processed = process_boq_data(data)
                    
                    # Table 1: Transporter
                    df_trans = df_processed[df_processed['Transporter'].astype(str).str.contains('Visiotech|Visiontech', case=False, na=False)]
                    st.markdown(f"<div class='table-header'>📦 Transporter Report</div>", unsafe_allow_html=True)
                    if not df_trans.empty:
                        buffer1 = io.BytesIO()
                        with pd.ExcelWriter(buffer1, engine='xlsxwriter') as writer:
                            df_trans[[c for c in mera_sequence if c in df_trans.columns]].to_excel(writer, index=False)
                        st.download_button("📥 Download Transporter Excel", buffer1.getvalue(), f"Transporter_{start_date}_to_{end_date}.xlsx", key="dl_t1_p2")
                        st.dataframe(df_trans[[c for c in mera_sequence if c in df_trans.columns]], use_container_width=True, hide_index=True)

                    # Table 2: TSP Partner
                    df_tsp = df_processed[df_processed['TSP Partner Name'].astype(str).str.contains('Visiotech|Visiontech', case=False, na=False)]
                    st.markdown(f"<div class='table-header'>🏗️ TSP Partner Report</div>", unsafe_allow_html=True)
                    if not df_tsp.empty:
                        buffer2 = io.BytesIO()
                        with pd.ExcelWriter(buffer2, engine='xlsxwriter') as writer:
                            df_tsp[[c for c in mera_sequence if c in df_tsp.columns]].to_excel(writer, index=False)
                        st.download_button("📥 Download TSP Excel", buffer2.getvalue(), f"TSP_{start_date}_to_{end_date}.xlsx", key="dl_t2_p2")
                        st.dataframe(df_tsp[[c for c in mera_sequence if c in df_tsp.columns]], use_container_width=True, hide_index=True)
                else: st.error("डेटा सापडला नाही.")
            except Exception as e: st.error(f"Error: {e}")

# --- PAGE 3: Bulk Project ID Upload ---
with t3:
    st.markdown("#### 📤 Bulk Project ID Upload (Excel/CSV)")
    st.info("'Project Number' नावाचा कॉलम असलेली फाईल अपलोड करा.")
    up_file = st.file_uploader("Upload File", type=['xlsx', 'csv'], key="bulk_up_v28")
    
    if up_file:
        try:
            bulk_df = pd.read_excel(up_file, engine='openpyxl') if up_file.name.endswith('.xlsx') else pd.read_csv(up_file)
            bulk_df.columns = [str(c).strip() for c in bulk_df.columns]
            if 'Project Number' in bulk_df.columns:
                p_list = bulk_df['Project Number'].astype(str).str.strip().unique().tolist()
                
                bc1, bc2 = st.columns(2)
                with bc1: submit_bulk = st.button("🚀 SUBMIT & PROCESS", use_container_width=True, key="bulk_submit_p3")
                with bc2: clear_bulk = st.button("🧹 CLEAR", use_container_width=True, key="bulk_clear_p3")

                if clear_bulk: st.rerun()

                if submit_bulk:
                    st.balloons()
                    with st.spinner(f'{len(p_list)} प्रोजेक्ट्स शोधत आहे...'):
                        query = supabase.table("BOQ Report").select("*").in_("Project Number", p_list)
                        data = fetch_complete_data(query) 
                        df_final = process_boq_data(data)
                        if not df_final.empty:
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                                df_final[[c for c in mera_sequence if c in df_final.columns]].to_excel(writer, index=False)
                            st.download_button("📥 Download Bulk Excel", output.getvalue(), "Bulk_Report.xlsx")
                            st.dataframe(df_final[[c for c in mera_sequence if c in df_final.columns]], use_container_width=True, hide_index=True)
                        else: st.warning("डेटा सापडला नाही.")
            else: st.error("Project Number कॉलम सापडला नाही.")
        except Exception as e: st.error(f"Error: {e}. Check openpyxl.")
    st.markdown("""
    <style>
        [data-testid="stDataFrame"] { border: 2px solid #1E3A8A; border-radius: 12px; }
        
        /* स्क्रॉल बार को मोटा और पकड़ने में आसान बनाने के लिए */
        section[data-testid="stTableContainer"] > div {
            overflow: auto !important;
        }
        ::-webkit-scrollbar {
            width: 14px;  /* वर्टिकल स्क्रॉल बार की चौड़ाई */
            height: 14px; /* हॉरिजॉन्टल स्क्रॉल बार की ऊंचाई */
        }
        ::-webkit-scrollbar-thumb {
            background: #1E3A8A !important; /* आपका डार्क ब्लू कलर */
            border-radius: 10px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        div.stButton > button:first-child {
            height: 60px !important; font-size: 20px !important; font-weight: bold !important;
            background-color: #1E3A8A !important; color: white !important; border-radius: 12px !important;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)
