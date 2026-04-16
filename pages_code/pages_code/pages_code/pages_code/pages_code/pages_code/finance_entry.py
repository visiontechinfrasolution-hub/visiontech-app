import streamlit as st
import pandas as pd

def show(supabase):
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>💰 Finance Entry (PO Analyzer)</h3>", unsafe_allow_html=True)
    def clean_num_fixed(val):
        try:
            if val is None or str(val).strip().lower() in ['nan', 'none', '']: return 0.0
            n = str(val).replace('"', '').replace(',', '').strip()
            num = pd.to_numeric(n, errors='coerce')
            return float(num) if pd.notnull(num) else 0.0
        except: return 0.0

    with st.form("fin_upload_fixed", clear_on_submit=True):
        c1, c2 = st.columns([1, 2])
        u_po = c1.text_input("📄 Enter PO Number")
        p_file = c2.file_uploader("Upload 'export.tsv'", type=['tsv', 'txt'])
        if st.form_submit_button("🚀 Process & Overwrite Data", use_container_width=True):
            if u_po and p_file:
                try:
                    content = p_file.getvalue().decode('ISO-8859-1').splitlines()
                    h_idx = next((i for i, line in enumerate(content) if "Project Name" in line), -1)
                    if h_idx != -1:
                        p_file.seek(0)
                        df_r = pd.read_csv(p_file, sep='\t', skiprows=h_idx, quoting=3, encoding='ISO-8859-1', engine='python')
                        df_r.columns = [str(c).replace('"', '').strip() for c in df_r.columns]
                        for col in df_r.columns: df_r[col] = df_r[col].astype(str).str.replace('"', '').str.strip()
                        df_r['qty_tmp'] = df_r['Qty'].apply(clean_num_fixed)
                        df_cln = df_r[df_r['qty_tmp'] > 0].copy()
                        if not df_cln.empty:
                            supabase.table("po_line_items").delete().eq("po_number", str(u_po)).execute()
                            supabase.table("po_summaries").delete().eq("po_number", str(u_po)).execute()
                            items = []
                            for _, r in df_cln.iterrows():
                                items.append({"po_number": str(u_po), "line_no": str(r.get('Line', '')), "item_number": str(r.get('Item Num', '')), "description": str(r.get('Description', '')), "uom": str(r.get('UOM', '')), "qty": clean_num_fixed(r.get('Qty')), "price": clean_num_fixed(r.get('Price')), "amount": clean_num_fixed(r.get('Amount')), "site_id": str(r.get('Site ID', '')), "site_name": str(r.get('Site Name', '')), "project_name": str(r.get('Project Name', ''))})
                            supabase.table("po_line_items").insert(items).execute()
                            df_cln['amt_tmp'] = df_cln['Amount'].apply(clean_num_fixed)
                            sums = df_cln.groupby('Project Name')['amt_tmp'].sum().reset_index()
                            summary_list = [{"po_number": str(u_po), "project_name": str(sr['Project Name']), "total_amount": float(sr['amt_tmp'])} for _, sr in sums.iterrows()]
                            supabase.table("po_summaries").insert(summary_list).execute()
                            st.success(f"PO {u_po} Synced!")
                            st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    g_search = st.text_input("🔍 Search Database...", key="fin_g_search")
    f_t1, f_t2 = st.tabs(["📊 Summaries", "📋 Detailed Items"])
    with f_t1:
        res_s = supabase.table("po_summaries").select("*").order("created_at", desc=True).execute()
        if res_s.data:
            df_s = pd.DataFrame(res_s.data)
            if g_search: df_s = df_s[df_s.astype(str).apply(lambda x: x.str.contains(g_search, case=False)).any(axis=1)]
            st.dataframe(df_s[['po_number', 'project_name', 'total_amount']], use_container_width=True, hide_index=True)
    with f_t2:
        res_d = supabase.table("po_line_items").select("*").order("created_at", desc=True).limit(1000).execute()
        if res_d.data:
            df_d = pd.DataFrame(res_d.data)
            if g_search: df_d = df_d[df_d.astype(str).apply(lambda x: x.str.contains(g_search, case=False)).any(axis=1)]
            st.dataframe(df_d[['po_number', 'line_no', 'item_number', 'qty', 'amount', 'project_name', 'site_id']], use_container_width=True, hide_index=True)
