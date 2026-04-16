import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        if st.text_input("Password:", type="password") == "1234":
            st.session_state.po_unlocked = True
            st.rerun()
    else:
        po_num = st.text_input("Enter PO Number")
        if st.button("Search"):
            res = supabase.table("PO Report").select("*").ilike("PO Number", f"%{po_num}%").execute()
            if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True)
