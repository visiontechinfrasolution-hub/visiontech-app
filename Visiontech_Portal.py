import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. CONNECTION (Aapka Data Maine Bhar Diya Hai) ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" # Hamesha 'anon/public' key use karein
supabase = create_client(URL, KEY)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")
st.title("🔍 Visiontech Industrial Solutions")
st.write("2.5 Lakh Rows Database Search Engine")

# --- 3. SEARCH BAR ---
# Maan lijiye aap Project ID se search karna chahte hain
search_id = st.text_input("Project ID enter karein:")

if search_id:
    try:
        # 'Automation' aapka table name ho sakta hai, agar alag hai toh yahan badal dein
        # Hum 'Automation' maan kar chal rahe hain
        response = supabase.table("Automation").select("*").eq("Project_ID", search_id).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            # --- FORMATTING: Date (21-Mar-2026) ---
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%b-%Y')

            # --- FORMATTING: No NULLs (Qty A, B, C ko blank karna) ---
            # Ye logic har column ke NULL ko khali box bana dega
            df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType'], '')

            st.success("✅ Record Mil Gaya!")
            # Table display
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.warning("❌ Ye Project ID database mein nahi hai.")
            
    except Exception as e:
        st.error(f"Error: Table ka naam sahi hai? (Error detail: {e})")

else:
    st.info("Bhai, search box mein ID likhiye.")