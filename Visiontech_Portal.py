# --- 1. Naya Import (timedelta ki zaroorat hai kal ki date ke liye) ---
from datetime import datetime, timedelta

# --- 2. Button Layout Section (TAB 1) ---
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 2])
    with r1: stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2: boq_date_pick = st.date_input("Select Date", value=None, label_visibility="collapsed", key="boq_q_d_v5")
    
    gen_new_boq = False
    with r3:
        if st.button("📄 Generate New BOQ", use_container_width=True):
            if boq_date_pick:
                gen_new_boq = True
            else:
                st.warning("Select Date!")
    
    # Nayi Line: Update Button
    with r4: 
        update_click = st.button("🔄 Update", use_container_width=True)

# --- 3. Update Logic (Search Condition ke andar) ---
    if submit_search or stn_pending_btn or gen_new_boq or update_click:
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        if update_click:
            # Site Detail se Project Numbers ki list nikalna
            sd_data = supabase.table("Site Detail").select("Project Number").execute()
            if sd_data.data:
                p_list = [str(x['Project Number']) for x in sd_data.data if x.get('Project Number')]
                # Kal ki date aapke format (26-Mar-2026) mein
                yesterday_val = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
                # Filter: Project List mein ho AUR Dispatch Date kal ki ho
                query = query.in_("Project Number", p_list).eq("Dispatch Date", yesterday_val)
        
        elif gen_new_boq:
            formatted_date_str = boq_date_pick.strftime('%d-%b-%Y')
            query = query.eq("BOQ Date", formatted_date_str)
        # ... baaki purana logic as it is ...
