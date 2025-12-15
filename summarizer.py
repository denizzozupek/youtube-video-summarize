import os 
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def youtube_text_summarizer(youtube_video_text : str) -> str | None:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-pro")

    system_prompt = """Sen uzman bir video özetleyicisisin. Görevin, sana verilen video transkriptini analiz etmek ve kullanıcının
    öğrenmesi gereken en önemli bilgileri içeren bir özet sağlamaktır. 

    Çıktı tamamen TÜRKÇE olmalı ve aşağıdaki formatta olmalıdır:

    Başlık: [Videonun ana başlığı]

    # Video Özeti:
    [Videonun kısa ve öz özeti]

    # Önemli Noktalar:
    - [Önemli nokta 1]
    - [Önemli nokta 2]
    ...

    ## Öğrenilmesi Gerekenler / Notlar:
    (Burada videoda geçen teknik terimler, önemli tarihler, kişi isimleri veya spesifik konseptleri açıkla)
    - **[Terim/Kavram]**: [Açıklama]

    ## Sonuç
    [Videonun ana fikri veya çıkarılması gereken ders]

    ## Kaynaklar
    (Eğer video belirli kaynaklara, makalelere veya referanslara atıfta bulunuyorsa, bunları burada listele)
    - [Kaynak 1]
    ....
    """

    user_prompt = f"Here is the video transcript:\n\n{youtube_video_text[:100000]}"

    try:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = model.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"An error occurred during the summarization process: {e}")
        return None