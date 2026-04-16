import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    in_id = st.text_input("Search Site ID")
    if st.button("Fetch Indus Data"):
        res = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
