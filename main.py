import os, sys
import argparse
from dotenv import load_dotenv
from transcriber import get_transcript
from summarizer import summarize_text

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="YouTube Video Summarizer (Turkish)")
    parser.add_argument("video_url", type=str, help="Youtube video URL")
    parser.add_argument("--save" "-s" , help="Save the summary to a text file (optional)", action="store_true")

    args = parser.parse_args()

    #Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        sys.exit(1)
    
    print(f"Processing video: {args.video_url}")
    try:
        print(" Step 1/2: Fetching transcript...")
        transcript = get_transcript(args.video_url)

        if not transcript:
            print("Error: Unable to fetch transcript for the provided video URL.")
            sys.exit(1)
        
        print(f"Transcript fetched successfully. Length: {len(transcript)} characters.")

        print(" Step 2/2: Summarizing transcript...")
        summary = summarize_text(transcript)
        print("\n" + "="*50 + "\n")
        print(summary)
        print("\n" + "="*50 + "\n")

        if args.save:
            filename = "summary.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"Summary saved to {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
