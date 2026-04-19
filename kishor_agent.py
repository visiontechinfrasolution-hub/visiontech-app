import os
import requests
import re
from google import genai
from supabase import create_client
from datetime import datetime

# --- १. किशोरची अस्सल ओळख ---
KISHOR_PROMPT = """
तुझे नाव 'किशोर' आहे. तू 'Visiontech' चा सर्वात हुशार, विनोदी आणि अभ्यासू डिजिटल असिस्टंट आहेस. 
तुझे बोलणे अस्सल गावरान मराठी ठसक्याचे, सविस्तर आणि माहितीपूर्ण असावे.

[नियम]
- सुरुवात ठळक (Bold) आणि रंजक वाक्याने कर. 🔥
- माहिती किमान ५-६ मुद्द्यांत सविस्तर मांड. 📚
- युजरला "ओ मालक", "ओ साहेब" किंवा "अहो सरकार" असे संबोध. 😎
- चालू घडामोडी विचारल्यास आजच्या तारखेनुसार माहिती दे. 🗞️📅
"""

# --- २. कॉन्फिगरेशन ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
INTERAKT_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = genai.Client(api_key=GEMINI_KEY)

def kishor_process(user_query):
    today = datetime.now().strftime("%d %B %Y")
    
    # ३. डेटा सर्च
    site_id_match = re.search(r'\d{6,}', user_query)
    raw_info = "NOT_FOUND"
    
    if site_id_match:
        try:
            res = supabase.table("Indus Data").select("*").eq("Site ID", site_id_match.group()).execute()
            if res.data:
                raw_info = str(res.data[0])
        except Exception as e:
            # इथे चूक होती, ती आता दुरुस्त केली आहे (Proper Indentation)
            return f"अहो सरकार, सुपॅबेसमध्ये अडचण आलीय: {str(e)}"

    # ४. किशोरकडून रिस्पॉन्स
    full_prompt = f"{KISHOR_PROMPT}\nलक्षात ठेव, आजची तारीख {today} आहे.\n\n"
    if raw_info != "NOT_FOUND":
        full_prompt += f"ह्या साईटची माहिती मिळाली आहे: {raw_info}. ती किशोरच्या स्टाईलमध्ये मांड."
    else:
        full_prompt += f"युजरचा प्रश्न: '{user_query}'. यावर पूर्ण डिटेलमध्ये उत्तर दे."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=full_prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"अहो सरकार, जेमिनी API मध्ये अडचण आलीय: {str(e)}"

def send_wa_reply(phone, message):
    url = "https://api.interakt.ai/v1/public/message/"
    headers = {
        "Authorization": "Basic S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=",
        "Content-Type": "application/json"
    }
    payload = {
        "countryCode": "+91",
        "phoneNumber": phone[-10:],
        "type": "Text",
        "message": message
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"WhatsApp Status Code: {r.status_code}")
        if r.status_code not in [200, 201, 202]:
            print(f"Response Error: {r.text}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")

if __name__ == "__main__":
    MY_NUMBER = "9552273181" 
    test_query = "छत्रपती शिवाजी महाराज पूर्ण माहिती सांगा" 
    
    print(f"🤖 किशोर उत्तर तयार करत आहे...")
    final_ans = kishor_process(test_query)
    
    print(f"🚀 व्हॉट्सॲपवर पाठवत आहे...")
    send_wa_reply(MY_NUMBER, final_ans)
