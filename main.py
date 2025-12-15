import os, sys
import argparse
from dotenv import load_dotenv
from datetime import datetime
from transcriber import get_transcripted_text, get_video_id_from_youtube_url
from summarizer import youtube_text_summarizer

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer (Turkish)")
    parser.add_argument("video_url", type=str, help="Youtube video URL")
    parser.add_argument("--save" , "-s" , help="Save the summary to a text file (optional)", action="store_true")

    args = parser.parse_args()

    #Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        sys.exit(1)
    
    print(f"Processing video: {args.video_url}")

    try:
        print(" Step 1/2: Fetching transcript...")
        transcript = get_transcripted_text(args.video_url)

        if not transcript:
            print("Error: Unable to fetch transcript for the provided video URL.")
            sys.exit(1)
        
        print(f"Transcript fetched successfully. Length: {len(transcript)} characters.")

        print(" Step 2/2: Summarizing transcript...")
        summary = youtube_text_summarizer(transcript)
        
        if not summary:
            print("Error: Summarization failed.")
            sys.exit(1)

        print("\n" + "="*50 + "\n")
        print(summary)
        print("\n" + "="*50 + "\n")

        if args.save:
            video_id = get_video_id_from_youtube_url(args.video_url)
            
            if video_id:
                filename = f"summary_{video_id}.md"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"summary_{timestamp}.md"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"Summary saved to {filename}")
    
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
