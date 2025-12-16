from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs

def get_video_id_from_youtube_url(youtube_url: str) -> str | None:
    parsed_url = urlparse(youtube_url)

    if parsed_url.query:
        query_params = parse_qs(parsed_url.query)
        video_id = query_params.get("v")

        if video_id:
            return video_id[0]
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return None

def fetch_transcript_from_youtube_url(video_id: str):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        #first try to get manually created transcripts
        try:
            transcript = transcript_list.find_transcript(['tr', 'en'])
            return transcript
        except NoTranscriptFound:
            pass

        #if no manually created transcripts, try to get generated ones
        try:
            transcript = transcript_list.find_generated_transcript(['tr', 'en'])
            return transcript       
        except NoTranscriptFound:
            print("No transcript available for this video.")
            return None
    
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"Transcripts are disabled or not found for video ID: {video_id}")
        return None
    except Exception as e:
        print(f"An error occurred while fetching the transcript: {e}")
        return None
    
def get_transcripted_text(youtube_url: str) -> str | None:
    video_id = get_video_id_from_youtube_url(youtube_url)

    if not video_id:
        print("Invalid YouTube URL provided.")
        return None
    
    transcript_obj = fetch_transcript_from_youtube_url(video_id)

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
