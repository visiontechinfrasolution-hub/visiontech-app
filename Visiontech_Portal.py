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
st.write("BOQ Report Search Engine")

# --- 3. SEARCH BAR ---
# Project ID ki jagah ab hum SITE ID search karenge
search_id = st.text_input("SITE ID enter karein (e.g. IN-1052232):")

if search_id:
    try:
        # Table Name: BOQ Report, Column Name: SITE ID
        response = supabase.table("BOQ Report").select("*").eq("SITE ID", search_id).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            # --- FORMATTING: Date (agar date ka column hai toh) ---
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%b-%Y')

            # --- FORMATTING: No NULLs ---
            df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType'], '')

            st.success("✅ Record Mil Gaya!")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.warning("❌ Ye SITE ID database mein nahi hai.")
            
    except Exception as e:
        st.error(f"Error detail: {e}")

else:
    st.info("Bhai, search box mein SITE ID likhiye.")
