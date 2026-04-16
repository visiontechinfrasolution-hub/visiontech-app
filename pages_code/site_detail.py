import streamlit as st

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>🏗️ Site Detail</h3>", unsafe_allow_html=True)
    site_id = st.text_input("Enter Site ID")
    if st.button("Search Detail"):
        res = supabase.table("Site Data").select("*").ilike("SITE ID", f"%{site_id}%").execute()
        if res.data: st.write(res.data)
