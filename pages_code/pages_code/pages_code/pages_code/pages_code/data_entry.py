import streamlit as st
import pandas as pd

def show(supabase, URL):
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Document Center & Tracker</h3>", unsafe_allow_html=True)
    doc_sub1, doc_sub2, doc_sub3 = st.tabs(["📤 Manager Upload", "🔍 Team Search", "📊 Tracker"])
    with doc_sub1:
        with st.form("doc_upload_final_v1", clear_on_submit=True):
            col_u1, col_u2 = st.columns(2)
            u_proj, u_indus = col_u1.text_input("📁 Project Number"), col_u2.text_input("📍 Indus ID")
            u_site, u_type = col_u1.text_input("🏢 Site Name"), col_u2.selectbox("📄 Doc Type", ["Photo", "SRC", "DC", "STN", "REPORT", "OTHER"])
            u_files = st.file_uploader("Select Files", accept_multiple_files=True)
            if st.form_submit_button("🚀 Upload All Files"):
                if u_files and u_proj:
                    for i, f in enumerate(u_files):
                        clean_p = u_proj.replace("/", "-").strip()
                        fname = f"{clean_p}_{u_indus}_{u_type}_{i}.{f.name.split('.')[-1]}"
                        supabase.storage.from_("site_documents").upload(path=fname, file=f.getvalue(), file_options={"x-upsert": "true"})
                        p_url = f"{URL}/storage/v1/object/public/site_documents/{fname}"
                        supabase.table("site_documents_master").upsert({"project_number": u_proj, "indus_id": u_indus, "site_name": u_site, "doc_type": u_type, "file_name": fname, "file_url": p_url}, on_conflict="file_name").execute()
                    st.success("✅ Files Uploaded!")

    with doc_sub2:
        q_s = st.text_input("🔍 Search Documents (Project, Indus, Site)")
        if q_s:
            res_db = supabase.table("site_documents_master").select("*").or_(f"project_number.ilike.%{q_s}%,indus_id.ilike.%{q_s}%,site_name.ilike.%{q_s}%").execute()
            if res_db.data:
                for row in res_db.data:
                    c1, c2, c3 = st.columns([2, 1, 1])
                    c1.write(row['file_name']); c2.info(row['doc_type']); c3.markdown(f'[📥 View]({row["file_url"]})')
                    st.divider()

    with doc_sub3:
        res_t = supabase.table("site_documents_master").select("*").execute()
        if res_t.data:
            df_t = pd.DataFrame(res_t.data)
            site_groups = df_t.groupby('indus_id')
            summary = []
            for ind_id, gp in site_groups:
                types = gp['doc_type'].str.upper().tolist()
                summary.append({"Project ID": gp.iloc[0]['project_number'], "Indus ID": ind_id, "Site Name": gp.iloc[0]['site_name'], "SRC": "✅" if "SRC" in types else "❌", "DC": "✅" if "DC" in types else "❌", "STN": "✅" if "STN" in types else "❌", "Report": "✅" if "REPORT" in types else "❌", "Photo": "✅" if "PHOTO" in types else "❌"})
            st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
