import os 
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument
from dotenv import load_dotenv
from PROMPTS import system_prompt

load_dotenv()

def youtube_text_summarizer(youtube_video_text : str) -> str | None:
    """Extracts the video ID from a given YouTube URL.

    Args:
        youtube_url (str): The URL of the YouTube video.

    Returns:
        str | None: The summary text if successful, or None if an error occurs.
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-pro")

    user_prompt = f"Here is the video transcript:\n\n{youtube_video_text}"

    try:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        response = model.generate_content(full_prompt)
        return response.text
    
    except InvalidArgument:
        print("Error: The video transcript is too long for the model's context window (Token limit exceeded).")
        return None

    except ResourceExhausted:
        print("Error: API quota exceeded (Resource Exhausted). Please try again later.")
        return None
    
    except Exception as e:
        print(f"An error occurred during the summarization process: {e}")
        return None