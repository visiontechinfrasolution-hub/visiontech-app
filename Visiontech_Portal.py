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

# --- 3. SMART SEARCH OPTIONS ---
st.subheader("Bhai, kis column se dhoondhna hai?")
search_type = st.radio(
    "Option select karein:",
    ["Project Number", "SITE ID"],
    horizontal=True 
)

search_query = st.text_input(f"Apna {search_type} yahan enter karein (e.g. 1054561):")

# --- 4. LOGIC & DATA FETCH ---
if search_query:
    try:
        # User ke daale hue extra spaces (aage-peeche) hatane ke liye
        clean_query = search_query.strip()
        
        # ilike aur % lagane se partial match aur case-insensitive search hoga
        # Isse agar database mein "IN-1054561 " (space ke sath) hoga, toh bhi mil jayega
        response = supabase.table("BOQ Report").select("*").ilike(search_type, f"%{clean_query}%").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            # --- FORMATTING ---
            if 'Date' in df.columns:
                try:
                    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d-%b-%Y')
                except:
                    pass
            
            # NULLs ko saaf karna
            df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType'], '')

            st.success(f"✅ Record Mil Gaya! (Searched by {search_type})")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
        else:
            st.warning(f"❌ Ye {search_type} ('{clean_query}') database mein nahi mila. Ek baar spelling check kar lijiye.")
            
    except Exception as e:
        st.error(f"Error: Kya table mein '{search_type}' naam ka exact column hai? (Detail: {e})")

else:
    st.info("Upar detail daliye, poora data table niche aa jayega.")
