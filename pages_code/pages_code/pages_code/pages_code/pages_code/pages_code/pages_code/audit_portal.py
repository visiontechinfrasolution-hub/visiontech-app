import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, time

def send_professional_email(selected_df, to_emails, cc_emails):
    SENDER = "vispltower@gmail.com" 
    PWD = "wpiw vkys mblb tunw" 
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d-%b-%Y')
    
    msg = MIMEMultipart()
    msg['Subject'] = f"Audit Request_Visiontech_({tomorrow})"
    msg['From'] = f"Visiontech Portal <{SENDER}>"
    msg['To'] = to_emails
    msg['Cc'] = cc_emails

    header_style = "background-color: #FFFF00; font-weight: bold; border: 1px solid black; padding: 4px; font-size: 10px; text-align: center; color: black;"
    td_style = "border: 1px solid black; padding: 4px; font-size: 10px; text-align: center;"

    cols = [
        "Circle", "Ref. No.", "Indus ID", "Site Name", "Site Add", "Cluster / Zone",
        "Date of Offerance in ISQ", "Date Of Audit Planned in ISQ", "ISQ Offerance Status(Y/N)",
        "Documents uploaded in ISQ(Y/N)", "TSP Shared Filled checklist during Offerance for audit (Yes / No)",
        "TSP Shared Compliance Photographs during audit Offerance (yes / No)", "Project", "Tower Type",
        "Tower Ht.", "Stage", "TSP Name", "Audit Agency Name", "Representative Name",
        "Representative Contact Number", "Actual ofference date", "Audit Engineer Name",
        "Contact Details.", "Actual Audit date", "Actual Audit Time", "Lat", "Long"
    ]

    h_html = "".join([f"<th style='{header_style}'>{c}</th>" for c in cols])
    r_html = ""
    for _, row in selected_df.iterrows():
        r_html += "<tr>"
        for col in cols:
            val = row.get(col, "-")
            r_html += f"<td style='{td_style}'>{val}</td>"
        r_html += "</tr>"

    body = f"""
    <html>
    <body style="font-family: Calibri, Arial; font-size: 11px;">
        <p>Hello Sir,</p>
        <p>Please find the audit request for the following sites attached in the table below:</p>
        <div style="overflow-x: auto;">
            <table border="1" style="border-collapse: collapse; width: 100%; border: 1px solid black;">
                <thead><tr style="background-color: #FFFF00;">{h_html}</tr></thead>
                <tbody>{r_html}</tbody>
            </table>
        </div>
        <br>
        <p>Thanks & Regards,<br>
        <b>Saira Quzi</b><br>
        Mobile: +91 8180827123<br>
        Visiontech Infra Solution</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER, PWD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Gmail Error: {e}")
        return False

def show(supabase):
    st.markdown("<h3 style='text-align: center; color: #1E3A8A;'>🏗️ Audit Management Portal</h3>", unsafe_allow_html=True)
    
    if 'audit_queue' not in st.session_state:
        st.session_state.audit_queue = []

    try:
        m_df = pd.DataFrame(supabase.table("VIS Portal Site Data").select('*').execute().data)
        u_df = pd.DataFrame(supabase.table("allowed_users").select("*").execute().data)
        h_df = pd.DataFrame(supabase.table("Audit Request").select("*").order("created_at", desc=True).execute().data)
        e_df = pd.DataFrame(supabase.table("Email Address").select("Email").execute().data)
    except: pass

    t1, t2 = st.tabs(["➕ Create Entry", "📜 History"])

    with t1:
        st.markdown("#### 📧 Email Configuration")
        c_em1, c_em2 = st.columns(2)
        db_emails = sorted(e_df["Email"].unique().tolist()) if not e_df.empty else []
        default_to = ["visiontechinfrasolution@gmail.com"]
        default_cc = ["services@vispltower.com", "project.visiontechinfra@gmail.com"]
        for em in default_to + default_cc:
            if em not in db_emails: db_emails.append(em)

        sel_to = c_em1.multiselect("To:", db_emails, default=default_to, key="v22_to")
        sel_cc = c_em2.multiselect("Cc:", db_emails, default=default_cc, key="v22_cc")
        
        st.divider()

        c_top1, c_top2 = st.columns(2)
        p_ids = [""] + sorted(m_df["PROJECT ID"].unique().tolist()) if not m_df.empty else [""]
        sel_pid = c_top1.selectbox("🔍 Select Project ID", p_ids, key="v22_pid")
        user_names = [""] + sorted(u_df["name"].tolist()) if not u_df.empty else [""]
        sel_rep = c_top2.selectbox("👤 Select Representative", user_names, key="v22_rep")

        s_info, rep_mob, lat_val, long_val, linked_sid = {}, "", "", "", ""
        today_dt = datetime.now().strftime("%d-%b-%Y")
        tomorrow_dt = (datetime.now() + timedelta(days=1)).strftime("%d-%b-%Y")
        
        if sel_pid and not m_df.empty:
            s_info = m_df[m_df["PROJECT ID"] == sel_pid].iloc[0].to_dict()
            linked_sid = str(s_info.get("SITE ID", "")).strip()
            if linked_sid:
                try:
                    res_coord = supabase.table("Indus_Coordinates").select("Lat", "Long").eq("Site ID", linked_sid).execute()
                    if res_coord.data:
                        match = res_coord.data[0]
                        lat_val, long_val = str(match.get("Lat", "")), str(match.get("Long", ""))
                except: pass

        if sel_rep and not u_df.empty:
            match_u = u_df[u_df["name"].astype(str).str.strip() == str(sel_rep).strip()]
            if not match_u.empty: rep_mob = str(match_u.iloc[0].get('phone_number', ''))

        with st.form("v22_form"):
            col1, col2, col3 = st.columns(3)
            f = {}
            f["Circle"] = col1.text_input("Circle", value="Maharashtra")
            f["Ref. No."] = col1.text_input("Project ID", value=sel_pid)
            f["Indus ID"] = col2.text_input("Indus ID", value=linked_sid)
            f["Site Name"] = col2.text_input("Site Name", value=s_info.get("SITE NAME", ""))
            f["Site Add"] = col3.text_input("Site Add", value=s_info.get("CLUSTER", ""))
            f["Cluster / Zone"] = col3.text_input("Cluster / Zone", value=s_info.get("CLUSTER", ""))
            f["Date of Offerance in ISQ"] = col1.text_input("Offerance Date", value=today_dt)
            f["Date Of Audit Planned in ISQ"] = col2.text_input("Planned Audit Date", value=tomorrow_dt)
            f["ISQ Offerance Status(Y/N)"] = col3.selectbox("ISQ Offerance Status", ["Y", "N"])
            f["Project"] = col1.text_input("Project Name", value=s_info.get("PROJECT NAME", ""))
            f["Tower Type"] = col2.text_input("Tower Type", value="GBT")
            f["Tower Ht."] = col3.text_input("Tower Ht.", value="40 mtr")
            
            f["Documents uploaded in ISQ(Y/N)"] = col1.selectbox("Documents uploaded?", ["Y", "N"])
            f["TSP Shared Filled checklist during Offerance for audit (Yes / No)"] = col2.selectbox("Checklist Shared?", ["Yes", "No"])
            f["TSP Shared Compliance Photographs during audit Offerance (yes / No)"] = col3.selectbox("Photographs Shared?", ["yes", "No"])
            
            f["Representative Name"] = col1.text_input("Representative Name", value=sel_rep)
            f["Representative Contact Number"] = col2.text_input("Rep. Mobile", value=rep_mob)
            f["Actual ofference date"] = col3.text_input("Actual ofference date", value=today_dt)
            f["Lat"], f["Long"] = col1.text_input("Lat", value=lat_val), col2.text_input("Long", value=long_val)
            f["Actual Audit date"] = col3.text_input("Actual Audit date", value=tomorrow_dt)
            
            audit_time_input = col1.time_input("Set Audit Time", value=time(11, 0)) 
            f["Actual Audit Time"] = audit_time_input.strftime("%I:%M %p") 

            f["Stage"], f["Audit Agency Name"], f["TSP Name"] = "", "", "Visiontech"
            f["Audit Engineer Name"], f["Contact Details."], f["Mail Status"], f["Mail Sent Date"] = "", "", "Pending", "-"

            if st.form_submit_button("➕ Add Site to Queue"):
                if sel_pid and f["Lat"]:
                    st.session_state.audit_queue.append(f.copy())
                    st.toast(f"✅ Added {linked_sid}")
                else: st.error("Missing Data!")

        if st.session_state.audit_queue:
            st.divider()
            for i, item in enumerate(st.session_state.audit_queue):
                q_col1, q_col2, q_col3, q_col4 = st.columns([3, 3, 2, 1])
                q_col1.write(f"**ID:** {item['Indus ID']}")
                q_col2.write(f"**Site:** {item['Site Name']}")
                q_col3.write(f"**Time:** {item['Actual Audit Time']}")
                if q_col4.button("❌", key=f"del_v22_{i}"):
                    st.session_state.audit_queue.pop(i)
                    st.rerun()

            if st.button("📧 Submit & Send Email", type="primary", use_container_width=True):
                if not sel_to: st.error("Select 'To' email!")
                else:
                    try:
                        res_schema = supabase.table("Audit Request").select("*").limit(1).execute()
                        db_cols = res_schema.data[0].keys() if res_schema.data else []
                        final_save = []
                        for item in st.session_state.audit_queue:
                            clean_item = {k: v for k, v in item.items() if k in db_cols and v != ""}
                            final_save.append(clean_item)

                        supabase.table("Audit Request").insert(final_save).execute()
                        
                        if send_professional_email(pd.DataFrame(st.session_state.audit_queue), ", ".join(sel_to), ", ".join(sel_cc)):
                            st.balloons()
                            st.success(f"🚀 Success! Email sent to {len(sel_to)} recipients.")
                            import time as py_time
                            py_time.sleep(3) 
                            st.session_state.audit_queue = []
                            st.rerun()
                    except Exception as e: st.error(str(e))
