import streamlit as st
import pandas as pd

def show(supabase, URL):
    st.markdown("<h3 style='text-align: center;'>📁 Document Entry</h3>", unsafe_allow_html=True)
    with st.form("doc_upload"):
        c1, c2 = st.columns(2)
        u_proj = c1.text_input("Project No.")
        u_indus = c2.text_input("Indus ID")
        u_files = st.file_uploader("Upload Files", accept_multiple_files=True)
        if st.form_submit_button("Upload"):
            if u_files and u_proj:
                for f in u_files:
                    fname = f"{u_proj}_{u_indus}_{f.name}"
                    supabase.storage.from_("site_documents").upload(path=fname, file=f.getvalue())
                st.success("Uploaded!")
