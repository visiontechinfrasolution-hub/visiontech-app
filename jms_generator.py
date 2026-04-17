import streamlit as st
import pandas as pd
import random
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

def show(supabase):
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>📄 Realistic JMS Generator</h2>", unsafe_allow_html=True)
    
    # १. डेटाबेस मधून प्रोजेक्ट्सची माहिती आणणे
    try:
        site_res = supabase.table("VIS Portal Site Data").select("PROJECT ID, SITE NAME, CLUSTER, SITE ID").execute()
        jms_sites_df = pd.DataFrame(site_res.data)
    except:
        jms_sites_df = pd.DataFrame()

    if not jms_sites_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            sel_pid = st.selectbox("1️⃣ Select Project ID", [""] + jms_sites_df["PROJECT ID"].tolist())
        with col2:
            # तुमच्या signatures फोल्डरमधील फोटोंच्या नावांची लिस्ट
            # टीप: फोटोंची नावे '.png' शिवाय इथे लिहा
            auditors = ["Abhijeet Chougule", "Akib Patel", "Amit Kumar Sharma", "Arun D Chavan", "Azeem", "Faruq Khan"]
            sel_aud = st.selectbox("2️⃣ Select Auditor Name", [""] + auditors)
        
        uploaded_tsv = st.file_uploader("3️⃣ Upload export.tsv", type=['tsv', 'txt'])

        if st.button("🚀 Generate & Preview Realistic JMS"):
            if sel_pid and sel_aud and uploaded_tsv:
                try:
                    df_tsv = pd.read_csv(uploaded_tsv, sep='\t', quoting=3, encoding='ISO-8859-1')
                    df_tsv.columns = [str(c).replace('"', '').strip() for c in df_tsv.columns]
                    site_info = jms_sites_df[jms_sites_df["PROJECT ID"] == sel_pid].iloc[0].to_dict()
                    
                    # --- २. IMAGE ENGINE (Handwritten Look) ---
                    width, height = 1240, 1754
                    paper = Image.new('RGB', (width, height), (255, 255, 255))
                    draw = ImageDraw.Draw(paper)

                    # Header
                    draw.text((320, 80), "VISIONTECH INFRA SOLUTIONS", fill="black")
                    
                    # Qty Rule: Round & Tick
                    y = 450
                    for i, r in df_tsv.iterrows():
                        if i > 15: break
                        q1 = float(pd.to_numeric(r.get('Ordered',0), errors='coerce') or 0)
                        q2 = float(pd.to_numeric(r.get('Requested/Delivered',0), errors='coerce') or 0)
                        
                        if q1 != q2: draw.ellipse([820, y, 890, y+40], outline="red", width=3)
                        if q1 == q2: draw.line([(1075, y+15), (1085, y+35), (1105, y)], fill="green", width=5)
                        y += 55

                    # Auditor Signature
                    sign_path = f"signatures/{sel_aud}.png"
                    if os.path.exists(sign_path):
                        s_img = Image.open(sign_path).resize((180, 90))
                        paper.paste(s_img, (800, height-250), s_img if s_img.mode == 'RGBA' else None)

                    # Scan & Fold Effect
                    p_arr = np.array(paper)
                    noise = np.random.randint(0, 12, p_arr.shape, dtype='uint8')
                    paper = Image.fromarray(np.clip(p_arr.astype('int16') - noise, 0, 255).astype('uint8'))
                    
                    st.image(paper, caption="JMS Preview")
                    
                    pdf_io = io.BytesIO()
                    paper.save(pdf_io, format="PDF")
                    st.download_button("📥 Download JMS PDF", pdf_io.getvalue(), f"JMS_{sel_pid}.pdf")
                except Exception as e:
                    st.error(f"Error: {e}")
