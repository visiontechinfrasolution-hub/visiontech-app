import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- 1. CONNECTION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I" 
supabase = create_client(URL, KEY)

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 2. UI SETUP & SIDEBAR MENU ---
st.set_page_config(page_title="Visiontech Portal", layout="wide")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2942/2942813.png", width=80) 
st.sidebar.title("🧭 Main Menu")
# 🔥 UPDATE: Yahan "Site Detail" add kiya gaya hai
menu_selection = st.sidebar.radio("Apna Module Chunein:", ["📦 BOQ Report", "🧾 PO Report", "🏗️ Site Detail"])
st.sidebar.divider()
st.sidebar.caption("© 2026 Visiontech Industrial Solutions")

# =====================================================================
# 🟩 PAGE 1: BOQ REPORT
# =====================================================================
if menu_selection == "📦 BOQ Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🔍 Visiontech Industrial Solutions</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>BOQ Report - Advanced Search & STN Tracker</p>", unsafe_allow_html=True)

    mera_sequence = [
        'Sr. No.', 'Site ID', 'Product', 'Transaction Type', 'Issue From', 'Project Number', 'BOQ',
        'Item Code', 'Item Description', 'Qty A', 'Qty B', 'Qty C', 'Dispatch Date', 'Parent/Child',
        'Line Status', 'Transporter', 'TSP Partner Name', 'LR Number', 'Vehicle Number',
        'Challan Number', 'BOQ Date', 'Department', 'Item Category', 'Source Of Fulfilment'
    ]

    with st.form("search_form"):
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.1, 1.0, 1.1, 1.0, 1.1, 1.1, 0.8, 1.0])
        with c1: project_query = st.text_input("📁 Project No.")
        with c2: site_query = st.text_input("📍 Site ID")
        with c3: boq_query = st.text_input("📄 BOQ")
        with c4: dispatch_date = st.date_input("📅 Date", value=None)
        
        transporter_list = ["", "visiontech", "Safexpress", "Delhivery", "VRL Logistics", "TCI Express", "Gati"]
        with c5: transporter = st.selectbox("🚚 Transporter", transporter_list)
        
        tsp_list = ["", "visiontech", "Partner A", "Partner B", "Partner C", "Ericsson", "Nokia"]
        with c6: tsp_partner = st.selectbox("🤝 TSP Partner", tsp_list)
        
        with c7:
            st.write("") 
            st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            submit_search = st.form_submit_button("🔍 Search")
            
        with c8:
            st.write("") 
            st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
            status_placeholder = st.empty() 

    st.divider()

    st.markdown("#### 📊 Quick Reports & Downloads")
    r1, r2, r3, r4 = st.columns([2, 1.5, 2, 4])

    with r1:
        stn_pending_btn = st.button("🚨 STN Pending Sites", use_container_width=True)
    with r2:
        boq_date_input = st.date_input("Select Date", value=None, label_visibility="collapsed")
    with r3:
        new_boq_btn = st.button("📄 Generate New BOQ", use_container_width=True)

    # --- BOQ PENDING LOGIC ---
    if stn_pending_btn:
        status_placeholder.empty()
        st.info("⏳ Visiontech ka STN Pending data nikal rahe hain...")
        try:
            response = supabase.table("BOQ Report").select("*").ilike("Transporter", "%visiontech%").limit(50000).execute()
            if response.data:
                df = pd.DataFrame(response.data)
                qty_cols = ['Qty A', 'Qty B', 'Qty C']
                for col in qty_cols:
                    if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                if 'Project Number' in df.columns and 'Item Code' in df.columns:
                    agg_funcs = {col: 'sum' if col in qty_cols else 'first' for col in df.columns if col not in ['Project Number', 'Item Code']}
                    items_df = df.groupby(['Project Number', 'Item Code'], as_index=False).agg(agg_funcs)

                    if 'Product' in items_df.columns and 'Issue From' in items_df.columns and 'Parent/Child' in items_df.columns:
                        pending_mask = (
                            (items_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & 
                            (items_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & 
                            (items_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent') &
                            (items_df['Qty A'] > 0) & 
                            (items_df['Qty B'] > 0) & 
                            (items_df['Qty C'] == 0)
                        )
                        pending_df = items_df[pending_mask]
                        if not pending_df.empty:
                            st.error(f"🚨 {pending_df['Project Number'].nunique()} Sites mein items ka STN Pending hai!")
                            for col in qty_cols: pending_df[col] = pending_df[col].astype(int)
                            final_cols = [c for c in mera_sequence if c in pending_df.columns]
                            bache_hue_cols = [c for c in pending_df.columns if c not in final_cols]
                            pending_df = pending_df[final_cols + bache_hue_cols]
                            st.dataframe(pending_df, use_container_width=True, hide_index=True)
                            csv = convert_df_to_csv(pending_df)
                            st.download_button(label="📥 Download Excel File", data=csv, file_name="STN_Pending_Sites.csv", mime="text/csv")
                        else:
                            st.success("✅ Wah! Visiontech ka koi bhi STN Pending nahi hai. Sab DONE hai!")
                    else: st.warning("Columns missing for Pending Logic.")
        except Exception as e: st.error(f"Error: {e}")

    # --- BOQ DATE LOGIC ---
    elif new_boq_btn:
        if boq_date_input is None: st.warning("⚠️ Kripya Date select karein!")
        else:
            st.info(f"⏳ {boq_date_input.strftime('%d-%b-%Y')} ka data nikal rahe hain...")
            iso_date = boq_date_input.strftime("%Y-%m-%d")
            df = pd.DataFrame()
            try:
                res = supabase.table("BOQ Report").select("*").eq("Dispatch Date", iso_date).limit(50000).execute()
                if res.data: df = pd.DataFrame(res.data)
            except Exception: pass

            if df.empty:
                formats_to_try = [boq_date_input.strftime("%d-%b-%Y"), boq_date_input.strftime("%d-%b-%y"), boq_date_input.strftime("%d-%m-%Y"), boq_date_input.strftime("%d/%m/%Y")]
                for fmt in formats_to_try:
                    try:
                        res = supabase.table("BOQ Report").select("*").ilike("Dispatch Date", f"%{fmt}%").limit(10000).execute()
                        if res.data:
                            df = pd.DataFrame(res.data)
                            break
                    except Exception: continue

            if not df.empty:
                st.success(f"✅ Record Mil Gaya! ({len(df)} Lines)")
                qty_cols = ['Qty A', 'Qty B', 'Qty C']
                for col in qty_cols:
                    if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                for col in df.columns:
                    if 'date' in col.lower(): df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
                df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                final_cols = [c for c in mera_sequence if c in df.columns]
                bache_hue_cols = [c for c in df.columns if c not in final_cols]
                boq_df = df[final_cols + bache_hue_cols]
                st.dataframe(boq_df, use_container_width=True, hide_index=True)
                csv = convert_df_to_csv(boq_df)
                st.download_button("📥 Download Excel File", data=csv, file_name=f"New_BOQ_{boq_date_input.strftime('%d-%b-%Y')}.csv", mime="text/csv")
            else: st.warning("❌ Is date par koi dispatch nahi mila.")

    # --- BOQ NORMAL SEARCH ---
    elif submit_search:
        has_filter = False
        query = supabase.table("BOQ Report").select("*").limit(50000)
        
        if project_query: query, has_filter = query.ilike("Project Number", f"%{project_query.strip()}%"), True
        if site_query: query, has_filter = query.ilike("Site ID", f"%{site_query.strip()}%"), True
        if boq_query: query, has_filter = query.ilike("BOQ", f"%{boq_query.strip()}%"), True
        if dispatch_date: query, has_filter = query.eq("Dispatch Date", dispatch_date.strftime("%Y-%m-%d")), True
        if transporter: query, has_filter = query.ilike("Transporter", f"%{transporter.strip()}%"), True
        if tsp_partner: query, has_filter = query.ilike("TSP Partner Name", f"%{tsp_partner.strip()}%"), True

        if has_filter:
            try:
                response = query.execute()
                if response.data:
                    df = pd.DataFrame(response.data)
                    qty_cols = ['Qty A', 'Qty B', 'Qty C']
                    for col in qty_cols:
                        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    if 'Item Code' in df.columns:
                        agg_funcs = {c: 'sum' if c in qty_cols else 'first' for c in df.columns if c != 'Item Code'}
                        df = df.groupby('Item Code', as_index=False).agg(agg_funcs)

                    stn_df = df.copy()
                    if 'Product' in stn_df.columns and 'Issue From' in stn_df.columns and 'Parent/Child' in stn_df.columns:
                        stn_df = stn_df[(stn_df['Product'].astype(str).str.contains('capex', case=False, na=False)) & (stn_df['Issue From'].astype(str).str.contains('warehouse', case=False, na=False)) & (stn_df['Parent/Child'].astype(str).str.strip().str.lower() == 'parent')]
                    
                    total_a = int(stn_df['Qty A'].sum()) if 'Qty A' in stn_df.columns else 0
                    total_b = int(stn_df['Qty B'].sum()) if 'Qty B' in stn_df.columns else 0
                    total_c = int(stn_df['Qty C'].sum()) if 'Qty C' in stn_df.columns else 0

                    if total_a > 0:
                        if total_a == total_b and total_c > 0: status_placeholder.markdown("<div style='background-color: #d4edda; color: #155724; border: 1px solid #28a745; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold;'>✅ STN DONE</div>", unsafe_allow_html=True)
                        else: status_placeholder.markdown("<div style='background-color: #f8d7da; color: #721c24; border: 1px solid #dc3545; padding: 7px 5px; border-radius: 5px; text-align: center; font-weight: bold;'>❌ STN PENDING</div>", unsafe_allow_html=True)

                    for col in df.columns:
                        if 'date' in col.lower(): df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d-%b-%Y')
                    for col in qty_cols:
                        if col in df.columns: df[col] = df[col].astype(int)
                    df = df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                    
                    final_cols = [c for c in mera_sequence if c in df.columns]
                    bache_hue_cols = [c for c in df.columns if c not in final_cols]
                    df = df[final_cols + bache_hue_cols]

                    st.success(f"✅ Record Mil Gaya! ({len(df)} Unique Items)")
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else: st.warning("❌ Data nahi mila.")
            except Exception as e: st.error(f"Error detail: {e}")
        else: st.info("Kripya search karne ke liye kam se kam ek box mein detail bhariye.")

# =====================================================================
# 🟦 PAGE 2: PO REPORT
# =====================================================================
elif menu_selection == "🧾 PO Report":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🧾 Purchase Order (PO) Report</h3>", unsafe_allow_html=True)
    
    po_sequence = [
        'Organization', 'PO Number', 'Shipment Number', 'Receipt Number', 
        'Item', 'Description', 'UOM', 'Quantity Received'
    ]

    # --- PASSWORD LOCK ---
    if "po_unlocked" not in st.session_state:
        st.session_state.po_unlocked = False

    if not st.session_state.po_unlocked:
        st.markdown("<br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.warning("🔒 Ye page secure hai. Kripya password daalein.")
            pwd = st.text_input("Enter Password:", type="password")
            if st.button("Unlock 🔓", use_container_width=True):
                if pwd == "1234": 
                    st.session_state.po_unlocked = True
                    st.rerun()
                else:
                    st.error("❌ Galat Password!")
    else:
        # --- UNLOCKED VIEW ---
        c1, c2 = st.columns([8, 1])
        with c2:
            if st.button("🔒 Lock", help="Page ko wapas lock karein"):
                st.session_state.po_unlocked = False
                st.rerun()
                
        st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>Search and Manage PO Details</p>", unsafe_allow_html=True)

        with st.form("po_search_form"):
            col1, col2, col3, col4 = st.columns(4)
            with col1: search_po = st.text_input("📄 PO Number")
            with col2: search_shipment = st.text_input("🚚 Shipment Number")
            with col3: search_receipt = st.text_input("🧾 Receipt Number")
            with col4:
                st.write("") 
                st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
                submit_po_search = st.form_submit_button("🔍 Search PO")

        if submit_po_search:
            has_filter = False
            query = supabase.table("PO Report").select("*").limit(50000)
            
            if search_po:
                try:
                    query = query.eq("PO Number", int(search_po.strip()))
                    has_filter = True
                except ValueError:
                    st.error("❌ PO Number mein sirf numbers daalein!")
            
            if search_shipment:
                try:
                    query = query.eq("Shipment Number", int(search_shipment.strip()))
                    has_filter = True
                except ValueError:
                    st.error("❌ Shipment Number mein sirf numbers daalein!")
                    
            if search_receipt:
                try:
                    query = query.eq("Receipt Number", int(search_receipt.strip()))
                    has_filter = True
                except ValueError:
                    st.error("❌ Receipt Number mein sirf numbers daalein!")

            if has_filter:
                try:
                    response = query.execute()
                    if response.data:
                        po_df = pd.DataFrame(response.data)
                        po_df = po_df.astype(str).replace(['None', 'nan', 'NULL', '<NA>', 'NoneType', 'NaT'], '')
                        
                        final_cols = [c for c in po_sequence if c in po_df.columns]
                        bache_hue_cols = [c for c in po_df.columns if c not in final_cols]
                        po_df = po_df[final_cols + bache_hue_cols]

                        st.success(f"✅ Record Mil Gaya! ({len(po_df)} Lines)")
                        
                        st.dataframe(
                            po_df, 
                            use_container_width=True, 
                            hide_index=True,
                            column_config={
                                "Description": st.column_config.TextColumn("Description", width="large")
                            }
                        )
                        
                        csv = convert_df_to_csv(po_df)
                        st.download_button(label="📥 Download Excel File", data=csv, file_name=f"PO_Report_{datetime.now().strftime('%d%b%Y')}.csv", mime="text/csv")
                    else:
                        st.warning("❌ Data nahi mila. Kripya check karein ki number sahi hai ya nahi.")
                except Exception as e:
                    st.error(f"Error detail: {e}")
            else:
                st.info("Kripya search karne ke liye kam se kam ek box mein detail bhariye.")

# =====================================================================
# 🟨 PAGE 3: SITE DETAIL (NEW MODULE)
# =====================================================================
elif menu_selection == "🏗️ Site Detail":
    st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>🏗️ Site Detail Report</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: 20px;'>Search Site and Project Details from Site Detail Table</p>", unsafe_allow_html=True)

    # Site details columns sequence jo aapne mention ki thi
    site_sequence = [
        'PROJECT ID', 'SITE ID', 'PROJECT NAME', 'SITE NAME', 'CLUSTER',
        'SITE STATUS', 'TEAM NAME', 'WORK DESCRIPTION', 'PO NO.', 'PO DATE', 
        'PO STATUS', 'RFAI STATUS', 'PTW NO.', 'PTW DATE', 'PTW STATUS', 
        'WCC NO.', 'WCC STATUS'
    ]

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
