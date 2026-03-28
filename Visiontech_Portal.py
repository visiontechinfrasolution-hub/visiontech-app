with btn_col2:
            # --- 1. Header Details ---
            wa_msg = f"📦 *BOQ REPORT* : {p_val}\n"
            wa_msg += f"*Project Number* - {p_val}\n"
            wa_msg += f"*Site ID* - {s_id}\n"
            
            # Site Name agar available ho toh
            site_nm = df['Site Name'].iloc[0] if 'Site Name' in df.columns else "-"
            wa_msg += f"*Site Name* - {site_nm}\n\n"
            
            # --- 2. BOQ Items Loop (Numbered Format) ---
            for index, row in df.iterrows():
                wa_msg += f"{index + 1}.\n"
                wa_msg += f"*Transaction Type* - {row.get('Transaction Type', '-')}\n"
                wa_msg += f"*BOQ Number* - {row.get('BOQ', '-')}\n"
                wa_msg += f"*Item Code* - {row.get('Item Code', '-')}\n"
                wa_msg += f"*Item Description* - {row.get('Item Description', '-')}\n"
                wa_msg += f"*BOQ Qty* - {row.get('Qty A', '0')}\n"
                wa_msg += f"*Dispatched Qty* - {row.get('Qty B', '0')}\n"
                wa_msg += f"*STN Qty* - {row.get('Qty C', '0')}\n"
                wa_msg += f"*Parent* - {row.get('Parent/Child', '-')}\n"
                wa_msg += f"*Dispatched Date* - {row.get('Dispatch Date', '-')}\n"
                wa_msg += f"*Transporter Name* - {row.get('Transporter', '-')}\n"
                wa_msg += f"*TSP Name* - {row.get('TSP Partner Name', '-')}\n"
                wa_msg += "--------------------\n"
            
            # --- 3. Indus Site Data (Vertical Format) ---
            wa_msg += st.session_state.get('wa_indus_data', "")

            # URL Encode and Button
            st.markdown(f'<a href="whatsapp://send?text={urllib.parse.quote(wa_msg)}" target="_blank"><button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%;">🚀 Share Full Report</button></a>', unsafe_allow_html=True)
