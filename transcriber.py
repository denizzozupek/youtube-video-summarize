import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def get_transcript(url):
    """Fetch the transcript of a YouTube video given its URL."""
    video_id = get_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    print(f"Fetching transcript for video ID: {video_id}")

    try:
        yt_api = YouTubeTranscriptApi()

        transcript_list = yt_api.list(video_id)

        try:
            transcript = transcript_list.find_transcript(['tr', 'en'])
        except:
            transcript = transcript_list.find_generated_transcript(['tr', 'en'])
            if not transcript:
                transcript = next(iter(transcript_list))

        print(f"Found transcript: {transcript.language_code}")
        formatter = TextFormatter()
        return formatter.format_transcript(transcript.fetch())

    except Exception as e:
        print("Transcript not available for this video.")
        return None
