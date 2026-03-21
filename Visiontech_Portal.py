import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")
st.title("🔍 Visiontech Industrial Solutions")
st.write("BOQ Report - Advanced Smart Search & STN Tracker")

st.divider() 

# --- 3. MULTIPLE SEARCH BOXES (FORM) ---
st.subheader("Bhai, yahan apni details bhariye (Koi bhi ek ya ek se zyada):")

# Form banaya taaki multiple detail bhar kar ek button daba sakein
with st.form("search_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        project_query = st.text_input("📁 Project Number")
    with col2:
        site_query = st.text_input("📍 SITE ID")
    with col3:
        dispatch_date = st.text_input("📅 Dispatch Date")

    col4, col5 = st.columns(2)
    with col4:
        transporter = st.text_input("🚚 Transporter (e.g. visiontech)")
    with col5:
        tsp_partner = st.text_input("🤝 TSP Partner Name")
        
    # Ye button dabane par hi search shuru hoga
    submit_search = st.form_submit_button("🔍 Search Data")

# --- 4. LOGIC & DATA FETCH ---
if submit_search:
    has_filter = False
    query = supabase.table("BOQ Report").select("*")
    
    # Jo box bhara hoga, code sirf usi ka filter lagayega
    if project_query:
        query = query.ilike("Project Number", f"%{project_query.strip()}%")
        has_filter = True
    if site_query:
        query = query.ilike("SITE ID", f"%{site_query.strip()}%")
        has_filter = True
    if dispatch_date:
        query = query.ilike("Dispatch Date", f"%{dispatch_date.strip()}%")
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

                # --- IMPORTANT 1: QTY SUM & DUPLICATE HATANA ---
                qty_cols = ['Qty A', 'Qty B', 'Qty C']
                for col in qty_cols:
                    if col in df.columns:
                        # Calculation ke liye number mein badalna
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                # 'Item Code' ke hisaab se line ko jodna (Sum karna)
                if 'Item Code' in df.columns:
                    agg_funcs = {}
                    for col in df.columns:
                        if col in qty_cols:
                            agg_funcs[col] = 'sum'
                        elif col != 'Item Code':
                            agg_funcs[col] = 'first' # Baaki info pehli wali rakhna

                    df = df.groupby('Item Code', as_index=False).agg(agg_funcs)

                    # Columns ka design wapas theek karna
                    original_cols = [c for c in response.data[0].keys() if c in df.columns]
                    df = df[original_cols]

                # --- IMPORTANT 2: STN DONE / PENDING LOGIC ---
                total_a = df['Qty A'].sum() if 'Qty A' in df.columns else 0
                total_b = df['Qty B'].sum() if 'Qty B' in df.columns else 0
                total_c = df['Qty C'].sum() if 'Qty C' in df.columns else 0

                # Box sirf tab dikhega jab Qty A mein kuch quantity ho
                if total_a > 0:
                    if total_a == total_b and total_a == total_c:
                        st.markdown("""
                        <div style='background-color: #d4edda; border: 2px solid #28a745; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                            <h1 style='color: #155724; margin: 0;'>✅ STN DONE</h1>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='background-color: #f8d7da; border: 2px solid #dc3545; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                            <h1 style='color: #721c24; margin: 0;'>❌ STN PENDING</h1>
                            <p style='color: #721c24; margin: 0; font-size: 18px; font-weight: bold;'>Mismatch - Qty A: {total_a} | Qty B: {total_b} | Qty C: {total_c}</p>
                        </div>
                        """, unsafe_allow_html=True)

                # --- FORMATTING: DATE ---
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')

                # --- FORMATTING: NULLs & ZEROS ---
                df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                for col in qty_cols:
                    if col in df.columns:
                        df[col] = df[col].replace('0.0', '0') # 0.0 ko simple 0 dikhane ke liye

                st.success(f"✅ Record Mil Gaya! ({len(df)} Unique Items)")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            else:
                st.warning("❌ Diye gaye filters par koi data nahi mila. Spelling check kar lijiye.")
                
        except Exception as e:
            st.error(f"Error: Kripya check karein ki Supabase mein columns ke naam ekdum exact ('Dispatch Date', 'Transporter', 'TSP Partner Name', 'Item Code') same hain ya nahi. (Detail: {e})")
    else:
        st.info("Kripya search karne ke liye kam se kam ek box mein detail bhariye aur 'Search Data' button dabaiye.")
