# =====================================================================
# 🟩 TAB 1: BOQ REPORT (ONLY CHANGES: NO .0 IN NUMBERS & DATE FORMAT)
# =====================================================================
with tab1:
    # ... (form aur search logic same rahega)
    
    if submit_search:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        if project_query: query = query.ilike("Project Number", f"%{project_query.strip()}%")
        if site_query: query = query.ilike("Site ID", f"%{site_query.strip()}%")
        if boq_query: query = query.ilike("BOQ", f"%{boq_query.strip()}%")
        
        response = query.execute()
        if response.data:
            df = pd.DataFrame(response.data)
            
            # --- NUMBER FORMATTING (Removing .0) ---
            qty_cols = ['Qty A', 'Qty B', 'Qty C']
            for col in qty_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # Grouping Logic
            if 'Item Code' in df.columns:
                agg_dict = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col != 'Item Code'}
                df = df.groupby('Item Code', as_index=False).agg(agg_dict)

            # --- DATE FORMATTING (DD-Mon-YYYY) ---
            date_cols = ['Dispatch Date', 'BOQ Date']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')

            # Cleaning and Sequencing
            df = df.fillna('').astype(str).replace(['None', 'nan', 'NULL', 'NaT'], '')
            
            final_cols = [c for c in mera_sequence if c in df.columns]
            df = df[final_cols + [c for c in df.columns if c not in final_cols]]
            
            st.dataframe(df, use_container_width=True, hide_index=True)
