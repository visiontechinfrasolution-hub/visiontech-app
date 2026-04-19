import os
import requests
import re
from google import genai
from supabase import create_client
from datetime import datetime

# --- १. किशोरची अस्सल ओळख (The Identity) ---
KISHOR_PROMPT = """
तुझे नाव 'किशोर' आहे. तू 'Visiontech' चा सर्वात हुशार, विनोदी आणि अभ्यासू डिजिटल असिस्टंट आहेस. 
तुझे बोलणे अस्सल गावरान मराठी ठसक्याचे, सविस्तर आणि माहितीपूर्ण असावे.

[बोलण्याचे नियम]
१. सुरुवात ठळक (Bold) आणि रंजक वाक्याने कर. 🔥
२. माहिती मुद्द्यांनुसार (Bullet Points) सविस्तर मांड. 📚
३. युजरला "ओ मालक", "ओ साहेब" किंवा "अहो सरकार" असे संबोधून सन्मान दे. 😎
४. माहिती इतकी पूर्ण दे की वाचणाऱ्याचे मन खुश झाले पाहिजे. 🚩🦁
५. जर बातमी किंवा माहिती माहित नसेल, तर मनाचे उत्तर देऊ नकोस.
"""

# --- २. कॉन्फिगरेशन (GitHub Secrets मधून) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
# तुमची Interakt Key (ही बदलू नका, जर काम करत असेल तर)
INTERAKT_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="

# क्लायंट सेटअप
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = genai.Client(api_key=GEMINI_KEY)

def kishor_process(user_query):
    today = datetime.now().strftime("%d %B %Y")
    
    # ३. डेटा सर्च (जर मेसेजमध्ये ६ अंकी किंवा त्यापेक्षा मोठा नंबर असेल तर साईट आयडी समजावा)
    site_id_match = re.search(r'\d{6,}', user_query)
    raw_info = "NOT_FOUND"
    
    if site_id_match:
        try:
            res = supabase.table("Indus Data").select("*").eq("Site ID", site_id_match.group()).execute()
            if res.data:
                raw_info = str(res.data[0])
        except Exception as e:
            print(f"Supabase Error: {e}")

    # ४. किशोरकडून रिस्पॉन्स तयार करणे (Gemini 2.0 Flash)
    full_prompt = f"{KISHOR_PROMPT}\nलक्षात ठेव, आजची खरी तारीख {today} आहे.\n\n"
    if raw_info != "NOT_FOUND":
        full_prompt += f"ह्या साईटची माहिती मिळाली आहे: {raw_info}. ती किशोरच्या फॉरमॅटमध्ये मांड."
    else:
        full_prompt += f"युजरचा प्रश्न: '{user_query}'. यावर सविस्तर (Full Detail) माहिती दे."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=full_prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"अहो सरकार, थोडी रेंजची अडचण आलीय: {str(e)}"

def send_wa_reply(phone, message):
    """व्हॉट्सॲपवर रिप्लाय पाठवण्यासाठी फंक्शन"""
    url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": f"Basic {INTERAKT_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "countryCode": "+91",
        "phoneNumber": phone[-10:],
        "type": "Text",
        "message": message
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"WhatsApp Sent Status: {r.status_code}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

if __name__ == "__main__":
    # ओ मालक, खाली तुमचा नंबर टाका आणि जो प्रश्न विचारायचा आहे तो टाका
    # टेस्टिंगसाठी सध्या मी तुमचा नंबर सेट केला आहे
    MY_NUMBER = "9552273181" 
    QUESTION = "छत्रपती शिवाजी महाराज पूर्ण माहिती सांगा" 
    
    print(f"🤖 किशोर डोकं चालवत आहे...")
    final_ans = kishor_process(QUESTION)
    
    print(f"🚀 उत्तर तयार झाले आहे, आता व्हॉट्सॲपवर पाठवत आहे...")
    send_wa_reply(MY_NUMBER, final_ans)
    
    print("\n--- किशोरचे उत्तर ---")
    print(final_ans)
    print("--------------------")
