import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>🧾 PO Report Search</h3>", unsafe_allow_html=True)
    if not st.session_state.get('po_unlocked', False):
        if st.text_input("Password PO:", type="password", key="p_lock_v5") == "1234":
            st.session_state.po_unlocked = True
            st.rerun()
    else:
        with st.form("po_form_v5"):
            c1, c2, c3, c4 = st.columns(4)
            with c1: s_po = st.text_input("📄 PO Number")
            with c2: s_sh = st.text_input("🚚 Shipment Number")
            with c3: s_re = st.text_input("🧾 Receipt Number")
            with c4: st.write(""); sub_po = st.form_submit_button("🔍 Search PO")
        if sub_po:
            res_po = supabase.table("PO Report").select("*").ilike("PO Number", f"%{s_po}%").execute()
            if res_po.data: st.dataframe(pd.DataFrame(res_po.data), use_container_width=True)
