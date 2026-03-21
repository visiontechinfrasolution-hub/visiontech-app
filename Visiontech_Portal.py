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
st.write("BOQ Report - Smart Search Engine")

st.divider() 

# --- 3. SMART SEARCH BOXES (Bina Selection Ke) ---
st.subheader("Bhai, niche kisi bhi ek box mein ID daliye:")

# Do boxes ko aamne-saamne (side-by-side) rakhne ke liye
col1, col2 = st.columns(2)

with col1:
    project_query = st.text_input("📁 Project Number yahan enter karein:")

with col2:
    site_query = st.text_input("📍 SITE ID yahan enter karein:")

# --- 4. LOGIC & DATA FETCH ---
# Agar dono mein se kisi bhi ek box mein kuch likha hai
if project_query or site_query:
    try:
        # Pata lagate hain ki user ne kis box mein type kiya hai
        if project_query:
            search_type = "Project Number"
            clean_query = project_query.strip()
        else:
            search_type = "SITE ID"
            clean_query = site_query.strip()
            
        # Data database se nikalna
        response = supabase.table("BOQ Report").select("*").ilike(search_type, f"%{clean_query}%").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            # --- FORMATTING: DATE (17-Mar-2026 format) ---
            # Ye code har us column ko theek karega jiske naam mein 'date' likha hoga
            for col in df.columns:
                if 'date' in col.lower():
                    # Date ko proper format mein badalna
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
            
            # --- FORMATTING: NULLs ---
            # 'NaT' (Not a Time) ko bhi khali box banane ke liye add kiya hai
            df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')

            st.success(f"✅ Record Mil Gaya! (Searched by {search_type})")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.warning(f"❌ Ye {search_type} ('{clean_query}') database mein nahi mila.")
            
    except Exception as e:
        st.error(f"Error detail: {e}")

else:
    st.info("Kripya Project Number ya SITE ID mein se koi ek detail bhariye, data apne aap aa jayega.")
