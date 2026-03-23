import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 2. UI SETUP & SIDEBAR MENU ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 Main Menu")
# Naya option "📊 Indus Basic Data" add kiya gaya hai
menu_selection = st.sidebar.radio("Apna Module Chunein:", ["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail", "📊 Indus Basic Data"])
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Industrial Solutions")

# =====================================================================
# 🟩 PAGE 1: BOQ REPORT (Same as before)
# =====================================================================
if menu_selection == "📦 BOQ Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
    # ... (BOQ Code remains same) ...
    # Note: Copy-paste your existing BOQ logic here if running full code

# =====================================================================
# 🟦 PAGE 2: PO REPORT (Same as before)
# =====================================================================
elif menu_selection == "🧾 PO Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Purchase Order (PO) Report</h3>", unsafe_allow_html=True)
    # ... (PO Code remains same) ...

# =====================================================================
# 🟨 PAGE 3: SITE DETAIL (Same as before)
# =====================================================================
elif menu_selection == "🏗️ Site Detail":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)
    # ... (Site Detail Code remains same) ...

# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA (NEW MODULE)
# =====================================================================
elif menu_selection == "📊 Indus Basic Data":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>Search by Site ID, Name, or Cluster</p>", unsafe_allow_html=True)

    # Column Sequence (Aapke table ke hisaab se)
    indus_sequence = ['Site ID', 'Site Name', 'District', 'Area Name', 'Tech Name', 'Tech Number', 'FSE ', 'FSE Number', 'AOM Name', 'AOM Number', 'Lat', 'Long']

    with st.form("indus_search_form"):
        col1, col2, col3 = st.columns(3)
        with col1: search_id = st.text_input("📍 Site ID")
        with col2: search_name = st.text_input("🏢 Site Name")
        with col3: search_cluster = st.text_input("🗺️ Cluster (Area Name)")
        
        submit_indus = st.form_submit_button("🔍 Search Indus Data")

    if submit_indus:
        has_filter = False
        query = supabase.table("Indus Data").select("*").limit(30000)
        
        if search_id:
            query = query.ilike("Site ID", f"%{search_id.strip()}%")
            has_filter = True
        if search_name:
            query = query.ilike("Site Name", f"%{search_name.strip()}%")
            has_filter = True
        if search_cluster:
            # Table mein Area Name ko Cluster maana gaya hai
            query = query.ilike("Area Name", f"%{search_cluster.strip()}%")
            has_filter = True

        if has_filter:
            try:
                response = query.execute()
                if response.data:
                    indus_df = pd.DataFrame(response.data)
                    
                    # Columns cleanup
                    indus_df = indus_df.astype(str).replace(['None', 'nan', 'NULL', '<NA>'], '')
                    
                    # Sequence arrange karna
                    final_cols = [c for c in indus_sequence if c in indus_df.columns]
                    bache_cols = [c for c in indus_df.columns if c not in final_cols]
                    indus_df = indus_df[final_cols + bache_cols]

                    st.success(f"✅ {len(indus_df)} Records mile.")
                    st.dataframe(indus_df, use_container_width=True, hide_index=True)
                    
                    csv = convert_df_to_csv(indus_df)
                    st.download_button("📥 Download CSV", data=csv, file_name="Indus_Basic_Data.csv", mime="text/csv")
                else:
                    st.warning("❌ Koi data nahi mila.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("Kripya search karne ke liye koi detail daalein.")
