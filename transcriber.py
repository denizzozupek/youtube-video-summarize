import traceback
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs

def get_video_id_from_youtube_url(youtube_url: str) -> str | None:
    """Extracts the video ID from a given YouTube URL.

    Args:
        youtube_url (str): The URL of the YouTube video.

    Returns:
        str | None: The extracted video ID (e.g., "6NQUbFiUYRw"), 
                    or None if the URL is invalid.
    """
    parsed_url = urlparse(youtube_url)

    if parsed_url.query:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v")

        if video_id:
            return video_id[0]
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return None

class TranscriptFetch:
    """A class to handle fetching transcripts (subtitles) from YouTube videos.
    
    It attempts to fetch manually created transcripts first. If not found, 
    it falls back to auto-generated transcripts.
    """
    LANGUAGES = ['tr', 'en']

    def __init__(self, api=None):
        """Initializes the TranscriptFetch instance.

        Args:
        api (optional): A mock API instance for testing purposes. 
                        If None, the real YouTubeTranscriptApi is used.
        """
        self.ytt_api = api or YouTubeTranscriptApi()

    def get_transcript_obj(self, video_id: str) -> list | None:
        """Orchestrates the retrieval of a transcript object for a given video ID.

        Args:
            video_id (str): The YouTube video ID.

        Returns:
            Transcript | None: The found transcript object, or None if not found/error.
        """

        try:
            transcript_list = self.ytt_api.list_transcripts(video_id)

        except (TranscriptsDisabled, NoTranscriptFound):
            print("No transcripts found or disabled.")
            return None
        
        except Exception as e:
            print(f"Error while fetching list: {e}")
            return None

        return self.find_transcript_in_list(transcript_list)
    
    def find_transcript_in_list(self, transcript_list):
        """Searches for a transcript in the provided list based on preferred languages.

        Args:
            transcript_list (TranscriptList): The list of transcripts returned by the API.

        Returns:
            Transcript | None: The matching transcript object, or None if no suitable match found.
        """

        #find manually created transcript
        try:
            return transcript_list.find_transcript(self.LANGUAGES)
        except NoTranscriptFound:
            pass

        #if no manually created transcripts, try to get generated ones
        try:
            return transcript_list.find_generated_transcript(self.LANGUAGES)    
        except NoTranscriptFound:
            print("No transcript available for this video.")
            return None
        
def get_transcripted_text(youtube_url: str) -> str | None:
    """Retrieves the full formatted text transcript from a YouTube URL.
    This function handles ID extraction, fetching, and formatting.

    Args:
        youtube_url (str): The URL of the YouTube video.

    Returns:
        str | None: The formatted transcript text, or None if any step fails.
    """
    video_id = get_video_id_from_youtube_url(youtube_url)

    if not video_id:
        print("Invalid YouTube URL provided.")
        return None
    
    transcript_fetcher = TranscriptFetch()

    transcript_obj = transcript_fetcher.get_transcript_obj(video_id)

    if not transcript_obj:
        return None
    
    # Format the transcript into plain text
    try:
        print("Fetching and formatting transcript...")
        transcripted_text = transcript_obj.fetch()
        
        formatter = TextFormatter()
        return formatter.format_transcript(transcripted_text)
    
    except Exception as e:
        print(f"An error occurred while formatting the transcript: {e}")
        return None
