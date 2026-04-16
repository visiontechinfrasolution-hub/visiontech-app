import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center;'>💰 Finance Entry</h3>", unsafe_allow_html=True)
    u_po = st.text_input("Enter PO Number for Finance")
    p_file = st.file_uploader("Upload export.tsv", type=['tsv'])
    if st.button("Process Finance Data"):
        st.info("Processing...")
        # Your Finance Logic Here
