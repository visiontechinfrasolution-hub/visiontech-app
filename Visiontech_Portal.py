# =====================================================================
# 📊 PAGE 4: INDUS BASIC DATA (FIXED FOR FSE NAME)
# =====================================================================
elif menu_selection == "📊 Indus Basic Data":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>📊 Indus Basic Data Report</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>Search Site Details</p>", unsafe_allow_html=True)

    with st.form("indus_search_form"):
        col1, col2, col3 = st.columns(3)
        with col1: s_id = st.text_input("📍 Site ID")
        with col2: s_nm = st.text_input("🏢 Site Name")
        with col3: s_cl = st.text_input("🗺️ Cluster (Area Name)")
        submit_indus = st.form_submit_button("🔍 Search Indus Data")

    if submit_indus:
        if s_id or s_nm or s_cl:
            query = supabase.table("Indus Data").select("*")
            if s_id: query = query.ilike("Site ID", f"%{s_id.strip()}%")
            if s_nm: query = query.ilike("Site Name", f"%{s_nm.strip()}%")
            if s_cl: query = query.ilike("Area Name", f"%{s_cl.strip()}%")
            
            res = query.execute()
            if res.data:
                for row in res.data:
                    # FSE handle karne ke liye (space check kar raha hai)
                    fse_name = row.get('FSE ', row.get('FSE', ''))
                    
                    # Formatting data - Agar data khali hai toh '-' dikhayega
                    st.markdown(f"""
                    ---
                    **Site ID** :- {row.get('Site ID') or '-'}  
                    **Site Name** :- {row.get('Site Name') or '-'}  
                    **District** :- {row.get('District') or '-'}  
                    **Area Name** :- {row.get('Area Name') or '-'}  
                    **Tech Name** :- {row.get('Tech Name') or '-'}  
                    **Tech Number** :- {row.get('Tech Number') or '-'}  
                    **FSE** :- {fse_name or '-'}  
                    **FSE Number** :- {row.get('FSE Number') or '-'}  
                    **AOM Name** :- {row.get('AOM Name') or '-'}  
                    **AOM Number** :- {row.get('AOM Number') or '-'}  
                    **Lat - Long** :- {row.get('Lat') or ''} {row.get('Long') or ''}
                    """)
            else: st.warning("❌ Data nahi mila.")
        else: st.info("Kripya search karne ke liye detail bhariye.")
