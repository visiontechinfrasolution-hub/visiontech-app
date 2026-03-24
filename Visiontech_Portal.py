import time
import os
import pyautogui
import pyperclip
import pandas as pd
from playwright.sync_api import sync_playwright
from supabase import create_client

# --- CONFIGURATION ---
URL = "https://sckyflvukpmdqmdzjzhs.supabase.co"
KEY = "sb_publishable_rAiegSkKYvM0Z9n7sUAI1w_WTgm1S4I"
supabase = create_client(URL, KEY)

TARGET_GROUP = "VISPL AUTOMATION REPORT"
AUTHORIZED_NUMBERS = ["9552273181", "9960843473", "7350533473"]
WHATSAPP_GROUP_NAME = "VISPL AUTOMATION REPORT" # Oracle report isi group mein jayegi

# Global Session Memory
session_data = {
    "query": None, 
    "waiting_for_option": False, 
    "waiting_for_oracle_date": False
}

# --- HELPERS ---
def safe_val(data_dict, key):
    v = data_dict.get(key)
    return str(v).strip() if v is not None else ""

def safe_num(val):
    try: return float(val) if val else 0.0
    except: return 0.0

def fmt_qty(num):
    if num == 0.0: return ""
    return str(int(num)) if num.is_integer() else str(num)

# --- DATABASE FUNCTIONS ---
def get_site_detail(query_str):
    res = supabase.table("Site Detail").select("*").or_(f'"PROJECT ID".ilike.%{query_str}%,"SITE ID".ilike.%{query_str}%').execute()
    if res.data:
        d = res.data[0]
        return (f"🏗️ *SITE DETAIL: {query_str}*\n"
                f"*Project Name* - {safe_val(d, 'PROJECT NAME')}\n"
                f"*Project Number* - {safe_val(d, 'PROJECT ID')}\n"
                f"*Site ID* - {safe_val(d, 'SITE ID')}\n"
                f"*Site Name* - {safe_val(d, 'SITE NAME')}\n"
                f"*Cluster* - {safe_val(d, 'CLUSTER')}\n"
                f"*Site Status* - {safe_val(d, 'SITE STATUS')}\n"
                f"*PO Detail* - {safe_val(d, 'PO NO.')} | {safe_val(d, 'PO DATE')} | {safe_val(d, 'PO STATUS')}\n"
                f"*RFAI STATUS* - {safe_val(d, 'RFAI STATUS')}\n"
                f"*WORK DESCRIPTION* - {safe_val(d, 'WORK DESCRIPTION')}\n"
                f"*TEAM NAME* - {safe_val(d, 'TEAM NAME')}\n"
                f"*PTW Detail* - {safe_val(d, 'PTW NO.')} | {safe_val(d, 'PTW DATE')} | {safe_val(d, 'PTW STATUS')}\n"
                f"*WCC Detail* - {safe_val(d, 'WCC NO.')} | {safe_val(d, 'WCC STATUS')}")
    return f"❌ '{query_str}' nahi mila."

def get_boq_status(query_str):
    res = supabase.table("BOQ Report").select("*").or_(f'"Project Number".ilike.%{query_str}%,"Site ID".ilike.%{query_str}%').execute()
    if res.data:
        site_name = ""
        try:
            site_res = supabase.table("Site Detail").select('"SITE NAME"').or_(f'"PROJECT ID".ilike.%{query_str}%,"SITE ID".ilike.%{query_str}%').execute()
            if site_res.data: site_name = safe_val(site_res.data[0], 'SITE NAME')
        except: pass
        
        response = f"📦 *BOQ REPORT: {query_str}*\n*Site Name* - {site_name}\n\n"
        merged_items = {}
        for d in res.data:
            if safe_val(d, 'Parent/Child').upper() != "PARENT": continue
            code = safe_val(d, 'Item Code')
            if code not in merged_items:
                merged_items[code] = {
                    'BOQ': safe_val(d, 'BOQ'), 'Desc': safe_val(d, 'Item Description'),
                    'A': safe_num(d.get('Qty A')), 'B': safe_num(d.get('Qty B')), 'C': safe_num(d.get('Qty C')),
                    'Status': safe_val(d, 'Line Status'), 'Date': safe_val(d, 'Dispatch Date'),
                    'Trans': safe_val(d, 'Transporter'), 'TSP': safe_val(d, 'TSP Partner Name'),
                    'IF': safe_val(d, 'Issue From'), 'SOF': safe_val(d, 'Source Of Fulfilment')
                }
            else:
                merged_items[code]['A'] += safe_num(d.get('Qty A'))
                merged_items[code]['B'] += safe_num(d.get('Qty B'))
                merged_items[code]['C'] += safe_num(d.get('Qty C'))

        for i, (code, item) in enumerate(merged_items.items(), 1):
            response += f"*{i}.*\n*Item Code* - {code}\n*Description* - {item['Desc']}\n"
            response += f"*BOQ Qty* - {fmt_qty(item['A'])}\n*Dispatched* - {fmt_qty(item['B'])}\n*STN* - {fmt_qty(item['C'])}\n"
            response += f"*Line Status* - {item['Status']}\n*Issue From* - {item['IF']}\n*Source* - {item['SOF']}\n"
            response += "-"*15 + "\n"
        return response.strip()
    return f"❌ BOQ data nahi mila."

def get_po_detail(query_str):
    try:
        res = supabase.table("PO Report").select("*").eq("PO Number", int(query_str)).execute()
        if res.data:
            resp = f"🧾 *PO REPORT: {query_str}*\n\n"
            for i, d in enumerate(res.data, 1):
                resp += f"*{i}.*\n*PO Number* - {safe_val(d, 'PO Number')}\n*WCC Number* - {safe_val(d, 'Shipment Number')}\n*Receipt Number* - {safe_val(d, 'Receipt Number')}\n"
                resp += "-"*15 + "\n"
            return resp.strip()
    except: pass
    return f"❌ PO '{query_str}' nahi mila."

# --- ORACLE SYNC ACTION ---
def run_oracle_process(target_date, page):
    try:
        # Step 1: Start Message
        send_reply(page, "🚀 *1. Run Started...*\nOracle se data fetch kiya ja raha hai...")
        time.sleep(2)
        
        # Step 2: Work in Progress
        send_reply(page, "⏳ *2. Work in progress...*\nData VISPL Tower par upload ho raha hai. Kripya mouse na chhuwein.")
        
        # --- [YAHAN AAPKA PURA ORACLE CODE PASTE KAREIN] ---
        # Note: target_date variable ko apne code mein use karein
        # Example: date_input_field.write(target_date)
        
        # --- PYAUTOGUI PART (Aapka Diya Hua) ---
        # ... (Aapka report generation logic yahan aayega) ...
        # uploaded_pos = [...]
        # msg = f"*PO REPORT...*"
        # pyperclip.copy(msg)
        # os.startfile("whatsapp:")
        # time.sleep(15)
        # pyautogui.hotkey('ctrl', 'f')... etc.
        # -----------------------------------------------

        time.sleep(5) # Simulation for progress
        send_reply(page, "✅ *3. Work Completed!*\nOracle report group mein bhej di gayi hai.")
        
    except Exception as e:
        send_reply(page, f"❌ *Error:* {str(e)}")

# --- WHATSAPP CORE ---
def send_reply(page, text):
    input_box = page.locator("div[contenteditable='true'][data-tab='10']")
    input_box.fill(text)
    page.keyboard.press("Enter")

def run_bot():
    global session_data
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(user_data_dir="./whatsapp_session", headless=False)
        page = context.pages[0]
        page.goto("https://web.whatsapp.com")
        print("📲 WhatsApp login ka intezar...")
        
        page.wait_for_selector('div[contenteditable="true"]', timeout=120000)
        print("✅ Login Successful! Group/Chat kholiye.")

        last_seen_msg = ""
        while True:
            try:
                # Chat open hai ya nahi check karein
                msg_elements = page.locator('div.copyable-text[data-pre-plain-text]').all()
                if not msg_elements: continue
                
                last_el = msg_elements[-1]
                full_text = last_el.inner_text().strip()
                meta = last_el.get_attribute("data-pre-plain-text") or ""
                
                # Bot ke apne messages ko ignore karein
                bot_keywords = ["Which Detail", "SITE DETAIL:", "BOQ REPORT:", "PO REPORT:", "🔄", "🚀", "⏳", "📅"]
                if any(k in full_text for k in bot_keywords) or full_text == last_seen_msg:
                    continue
                
                last_seen_msg = full_text
                
                # SECURITY: Sender Number nikalna
                is_authorized = any(num in meta for num in AUTHORIZED_NUMBERS)
                is_personal = "group" not in meta.lower() # Simple check for personal chat

                # 1. ORACLE RUN COMMAND (Strict Rules)
                if "oracle run" in full_text.lower():
                    if is_authorized: # Number check
                        session_data["waiting_for_oracle_date"] = True
                        send_reply(page, "📅 *Authorized!* Kripya wo Date batayein jiska process run karna hai?\n(Example: 23-03-2026)")
                    else:
                        send_reply(page, "❌ Aapko ye command chalane ki permission nahi hai.")
                    continue

                # 2. ORACLE DATE INPUT
                if session_data["waiting_for_oracle_date"]:
                    target_date = full_text
                    session_data["waiting_for_oracle_date"] = False
                    run_oracle_process(target_date, page)
                    continue

                # 3. NORMAL SEARCH (Site/BOQ/PO)
                if session_data["waiting_for_option"] and full_text in ["1", "2", "3"]:
                    q = session_data["query"]
                    if full_text == "1": resp = get_site_detail(q)
                    elif full_text == "2": resp = get_boq_status(q)
                    else: resp = get_po_detail(q)
                    
                    send_reply(page, f"{resp}\n\n🔄 *Aur detail chahiye {q} ki?*\nBas 1, 2, ya 3 reply karein.")
                else:
                    # Naya ID aaya
                    session_data["query"] = full_text
                    session_data["waiting_for_option"] = True
                    send_reply(page, f"🔍 Aapne '{full_text}' bheja.\n\nWhich Detail you required:\n1. Site Detail\n2. BOQ Status\n3. PO Detail")

            except Exception as e: pass
            time.sleep(2)

if __name__ == "__main__":
    run_bot()
