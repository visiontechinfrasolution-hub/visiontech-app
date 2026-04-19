import os
import requests
import re
from google import genai # लेटेस्ट लायब्ररी
from supabase import create_client
from datetime import datetime

# --- १. किशोरची अस्सल ओळख (The Identity) ---
KISHOR_PROMPT = """
तुझे नाव 'किशोर' आहे. तू 'Visiontech' चा सर्वात हुशार, विनोदी आणि अभ्यासू डिजिटल असिस्टंट आहेस. 
तुझे बोलणे अस्सल गावरान मराठी ठसक्याचे, सविस्तर आणि माहितीपूर्ण असावे.

[नियम]
१. सुरुवात ठळक (Bold) आणि रंजक वाक्याने कर. 🔥
२. माहिती मुद्द्यांनुसार (Bullet Points) सविस्तर मांड. 📚
३. युजरला "ओ मालक", "ओ साहेब" किंवा "अहो सरकार" असे संबोध. 😎
४. पूर्ण माहिती दे, विचारायचे मन खुश झाले पाहिजे. 🚩🦁
५. शिवाजी महाराज किंवा राजकीय व्यक्तीवर विचारले तर त्यांचा जन्म, कार्य, इतिहास पूर्ण दे.
"""

# --- २. कॉन्फिगरेशन (GitHub Secrets मधून येणार) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
INTERAKT_KEY = "S2pFcE5ETjE2NDhiQ1VIMEFjMVA5a3ZwdHB6X0diYXpRM2I2SWRxbGJWYzo="

# सुपॅबेस आणि जेमिनी क्लायंट सेटअप
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = genai.Client(api_key=GEMINI_KEY)

def kishor_process(user_query):
    today = datetime.now().strftime("%d %B %Y")
    
    # ३. डेटा सर्च (Site ID तपासणे)
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
        full_prompt += f"ह्या साईटची माहिती मिळाली आहे: {raw_info}. ती किशोरच्या स्टाईलमध्ये मांड."
    else:
        full_prompt += f"युजरचा प्रश्न: '{user_query}'. यावर सविस्तर (Full Detail) माहिती दे."

    try:
        # लेटेस्ट मॉडेल वापरून उत्तर घेणे
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=full_prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"अहो सरकार, थोडी तांत्रिक अडचण आलीय: {str(e)}"

if __name__ == "__main__":
    # टेस्टिंगसाठी प्रश्न
    test_query = "छत्रपती शिवाजी महाराज पूर्ण माहिती सांगा" 
    
    print(f"🤖 किशोर उत्तर तयार करत आहे...")
    final_ans = kishor_process(test_query)
    
    print("\n" + "="*30)
    print(f"🚩 किशोरचे उत्तर:\n\n{final_ans}")
    print("="*30)
