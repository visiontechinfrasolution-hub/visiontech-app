# =====================================================================
# 🟨 PAGE 3: SITE DETAIL (NEW MODULE)
# =====================================================================
elif menu_selection == "🏗️ Site Detail":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)

    # Site details columns sequence
    site_sequence = [
        'PROJECT ID', 'SITE ID', 'PROJECT NAME', 'SITE NAME', 'CLUSTER',
        'SITE STATUS', 'TEAM NAME', 'WORK DESCRIPTION', 'PO NO.', 'PO DATE', 
        'PO STATUS', 'RFAI STATUS', 'PTW NO.', 'PTW DATE', 'PTW STATUS', 
        'WCC NO.', 'WCC STATUS'
    ]

    # --- PASSWORD LOCK LOGIC ---
    if "site_unlocked" not in st.session_state:
        st.session_state.site_unlocked = False

    if not st.session_state.site_unlocked:
        st.markdown("<br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.warning("🔒 Ye page secure hai. Kripya password daalein.")
            # Key add kiya hai taaki PO report wale password box se clash na ho
            pwd = st.text_input("Enter Password:", type="password", key="site_pwd")
            if st.button("Unlock 🔓", use_container_width=True, key="site_unlock_btn"):
                if pwd == "1234": # Yahan aap apna password change kar sakte hain
                    st.session_state.site_unlocked = True
                    st.rerun()
                else:
                    st.error("❌ Galat Password!")
    else:
        # --- UNLOCKED VIEW ---
        c1, c2 = st.columns([8, 1])
        with c2:
            if st.button("🔒 Lock", help="Page ko wapas lock karein", key="site_lock_btn"):
                st.session_state.site_unlocked = False
                st.rerun()
                
        st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>Search Site and Project Details from Site Detail Table</p>", unsafe_allow_html=True)

        with st.form("site_search_form"):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1: search_proj_id = st.text_input("📁 Project ID")
            with col2: search_site_id = st.text_input("📍 Site ID")
            with col3:
                st.write("") 
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                submit_site_search = st.form_submit_button("🔍 Search Site")

        if submit_site_search:
            has_filter = False
            query = supabase.table("Site Detail").select("*").limit(50000)
            
            if search_proj_id:
                query = query.ilike("PROJECT ID", f"%{search_proj_id.strip()}%")
                has_filter = True
                
            if search_site_id:
                query = query.ilike("SITE ID", f"%{search_site_id.strip()}%")
                has_filter = True

            if has_filter:
                try:
                    response = query.execute()
                    if response.data:
                        site_df = pd.DataFrame(response.data)
                        site_df = site_df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                        
                        # Columns arrange karna
                        final_cols = [c for c in site_sequence if c in site_df.columns]
                        bache_hue_cols = [c for c in site_df.columns if c not in final_cols]
                        site_df = site_df[final_cols + bache_hue_cols]

                        st.success(f"✅ Record Mil Gaya! ({len(site_df)} Sites)")
                        st.dataframe(site_df, use_container_width=True, hide_index=True)
                        
                        csv = convert_df_to_csv(site_df)
                        st.download_button(label="📥 Download Excel File", data=csv, file_name=f"Site_Detail_{datetime.now().strftime('%d%b%Y')}.csv", mime="text/csv")
                    else:
                        st.warning("❌ Data nahi mila. Kripya Project ID ya Site ID check karein.")
                except Exception as e:
                    st.error(f"Error detail: {e}")
            else:
                st.info("Kripya search karne ke liye Project ID ya Site ID bhariye.")
