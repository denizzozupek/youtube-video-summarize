import os 
from litellm import acompletion
import litellm
import litellm.exceptions as exceptions
from dotenv import load_dotenv
from PROMPTS import system_prompt
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential
import logging

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-nano")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
retry=retry_if_exception_type((exceptions.RateLimitError, exceptions.ServiceUnavailableError, exceptions.InternalServerError)))
async def generate_content_safe(messages: list):
    """Safely calls the api with retry logic for transient errors using LiteLLM's exceptions
    """
    logger.info("Sending request to the model...")
    response = await acompletion(model=MODEL_NAME, messages=messages)
    return response.choices[0].message.content

async def youtube_text_summarizer(youtube_video_text : str) -> str | None:
    """Generates a summary from the given YouTube video transcript using API.

    Args:
        youtube_video_text (str): The transcript text of the YouTube video.

    Returns:
        str | None: The summary text if successful, or None if an error occurs.
        
    """

    user_prompt = f"Here is the video transcript:\n\n{youtube_video_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        summary_text = await generate_content_safe(messages)
        logger.info("Summary generated successfully.")
        return summary_text

    except litellm.exceptions.ContextWindowExceededError:
        logger.error("The video transcript is too long for the model's context window (Token limit exceeded).")
        return None

    except litellm.exceptions.RateLimitError:
        logger.error("API quota exceeded or rate limited. Please try again later.")
        return None
    
    except litellm.exceptions.AuthenticationError:
        logger.error("Authentication Error: API Key is missing or invalid. Check your .env file!")
        return None
    
    except Exception as e:
        logger.error(f"An error occurred during the summarization process: {str(e)}")
        return None
