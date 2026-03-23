# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA (WHATSAPP GROUP SEMI-AUTO)
# =====================================================================
elif menu_selection == "📊 Indus Basic Data":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    
    with st.form("indus_form"):
        i1, i2, i3 = st.columns(3)
        with i1: in_id = st.text_input("📍 Site ID", key="in_s")
        with i2: in_nm = st.text_input("🏢 Site Name", key="in_n")
        with i3: in_cl = st.text_input("🗺️ Cluster", key="in_c")
        sub_i = st.form_submit_button("🔍 Search Indus")
    
    if sub_i:
        if in_id or in_nm or in_cl:
            q = supabase.table("Indus Data").select("*")
            if in_id: q = q.ilike("Site ID", f"%{in_id.strip()}%")
            if in_nm: q = q.ilike("Site Name", f"%{in_nm.strip()}%")
            if in_cl: q = q.ilike("Area Name", f"%{in_cl.strip()}%")
            res = q.execute()
            
            if res.data:
                import urllib.parse
                for row in res.data:
                    fse_name = row.get('FSE ', row.get('FSE', '-'))
                    lat_long = f"{row.get('Lat', '')} {row.get('Long', '')}"
                    
                    # --- WhatsApp Message Format (Bold formatting ke sath) ---
                    wa_message = (
                        f"*Visiontech Site Report*\n"
                        f"---------------------------\n"
                        f"*Site ID* :- {row.get('Site ID', '-')}\n"
                        f"*Site Name* :- {row.get('Site Name', '-')}\n"
                        f"*District* :- {row.get('District', '-')}\n"
                        f"*Area Name* :- {row.get('Area Name', '-')}\n"
                        f"*Tech Name* :- {row.get('Tech Name', '-')}\n"
                        f"*Tech Number* :- {row.get('Tech Number', '-')}\n"
                        f"*FSE* :- {fse_name}\n"
                        f"*FSE Number* :- {row.get('FSE Number', '-')}\n"
                        f"*AOM Name* :- {row.get('AOM Name', '-')}\n"
                        f"*AOM Number* :- {row.get('AOM Number', '-')}\n"
                        f"*Lat - Long* :- {lat_long}"
                    )
                    
                    encoded_msg = urllib.parse.quote(wa_message)
                    
                    # WhatsApp Desktop App/Web Link
                    # Bina phone number ke ye 'Forward' option open karta hai
                    whatsapp_url = f"https://web.whatsapp.com/send?text={encoded_msg}"

                    # --- Display Data UI ---
                    st.markdown(f"""
                    ---
                    **Site ID** :- {row.get('Site ID') or '-'} | **Site Name** :- {row.get('Site Name') or '-'}
                    """)
                    
                    # WhatsApp Button
                    st.markdown(f"""
                        <a href="{whatsapp_url}" target="_blank">
                            <button style="
                                background-color: #25D366;
                                color: white;
                                border: none;
                                padding: 10px 20px;
                                border-radius: 5px;
                                cursor: pointer;
                                font-weight: bold;
                                width: 200px;">
                                📲 Send to Group
                            </button>
                        </a>
                    """, unsafe_allow_html=True)
            else:
                st.warning("❌ Data nahi mila.")
        else:
            st.info("Kripya search karne ke liye detail bhariye.")
