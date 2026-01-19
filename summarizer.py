import os 
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument, ServiceUnavailable, DeadlineExceeded
from dotenv import load_dotenv
from PROMPTS import system_prompt
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

load_dotenv()

logger = logging.getLogger(__name__)

@retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry = retry_if_exception_type(((ServiceUnavailable, DeadlineExceeded, ConnectionError)))

)

def generate_content_safe(model, prompt):
    """Safely calls the api with retry logic for transient errors
    """
    return model.generate_content(prompt)

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
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        logger.info("Sending request to Google Gemini API...")
        response = generate_content_safe(model, full_prompt)
        logger.info("Summary generated successfully.")
        return response.text
    
    except InvalidArgument:
        logger.error("The video transcript is too long for the model's context window (Token limit exceeded).")
        return None

    except ResourceExhausted:
        logger.error("API quota exceeded (Resource Exhausted). Please try again later.")
        return None
    
    except Exception as e:
        logger.error(f"An error occurred during the summarization process: {e}", exc_info=True)
        return None