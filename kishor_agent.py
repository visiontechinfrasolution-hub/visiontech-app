import os
import requests
import re
import google.generativeai as genai
from supabase import create_client
from datetime import datetime

# --- १. किशोरची ओळख (Identity) ---
KISHOR_PROMPT = """
तुझे नाव 'किशोर' आहे. तू 'Visiontech' चा सर्वात हुशार, विनोदी आणि अभ्यासू डिजिटल असिस्टंट आहेस. 
तुझे बोलणे अस्सल गावरान मराठी ठसक्याचे, सविस्तर आणि माहितीपूर्ण असावे.

[नियम]
१. सुरुवात ठळक (Bold) आणि रंजक वाक्याने कर. 🔥
२. माहिती मुद्द्यांनुसार (Bullet Points) सविस्तर मांड. 📚
३. युजरला "ओ मालक", "ओ साहेब" किंवा "अहो सरकार" असे संबोध. 😎
४. पूर्ण माहिती दे, विचारायचे मन खुश झाले पाहिजे. 🚩🦁
"""

# --- २. कॉन्फिगरेशन ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
INTERAKT_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo=" # तुमची Interakt Key

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_KEY)

def kishor_process(user_query):
    model = genai.GenerativeModel('gemini-1.5-flash')
    today = datetime.now().strftime("%d %B %Y")
    
    # ३. डेटा सर्च (Site ID तपासणे)
    site_id_match = re.search(r'\d{6,}', user_query)
    raw_info = "NOT_FOUND"
    
    if site_id_match:
        try:
            res = supabase.table("Indus Data").select("*").eq("Site ID", site_id_match.group()).execute()
            if res.data:
                raw_info = str(res.data[0])
        except: pass

    # ४. किशोरकडून रिस्पॉन्स तयार करणे
    full_prompt = f"{KISHOR_PROMPT}\nलक्षात ठेव, आजची खरी तारीख {today} आहे.\n\n"
    if raw_info != "NOT_FOUND":
        full_prompt += f"ह्या साईटची माहिती सापडली आहे: {raw_info}. ती किशोरच्या स्टाईलमध्ये नीट मांड."
    else:
        full_prompt += f"युजरचा प्रश्न: '{user_query}'. यावर सविस्तर (Full Detail) माहिती दे."

    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except:
        return "अहो मालक, रेंजचा प्रॉब्लेम दिसतोय, किशोर पुन्हा ट्राय करेल!"

if __name__ == "__main__":
    # टेस्टिंगसाठी सध्या फक्त प्रिंट करू, नंतर आपण Interakt सोबत कनेक्ट करू
    test_query = "शिवाजी महाराज सविस्तर माहिती सांगा" 
    print(kishor_process(test_query))
