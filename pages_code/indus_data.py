import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>📊 Indus Basic Data</h3>", unsafe_allow_html=True)
    with st.form("ind_form_v5"):
        in_id = st.text_input("📍 Site ID Search")
        if st.form_submit_button("🔍 Search Indus"):
            res_ind = supabase.table("Indus Data").select("*").ilike("Site ID", f"%{in_id}%").execute()
            if res_ind.data: st.dataframe(pd.DataFrame(res_ind.data))
