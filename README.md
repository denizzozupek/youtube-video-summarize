
# 🎥 YouTube Video Summarizer (Powered by Gemini AI)

A powerful Python tool that analyzes YouTube videos to generate structured, educational summaries using **Google Gemini 1.5 Flash**.

This tool automatically retrieves video transcripts. If official captions are missing, it downloads the audio and transcribes it locally using **OpenAI Whisper** as a fallback. It then processes the text to extract key insights, learning points, and summaries.

## 🚀 Key Features

* **Automatic Transcript Retrieval:** Fetches official YouTube captions (if available) in seconds.
* **Smart Audio Fallback:** Automatically downloads audio and uses **OpenAI Whisper (Local)** for transcription if no captions are found.
* **AI-Powered Summarization:** Uses Google's **Gemini 1.5 Flash** model for fast and context-aware summaries.
* **Structured Output:** Generates clean Markdown reports including "Key Points," "Things to Learn," and "Conclusion."
* **File Export:** Option to save the summary to a `.md` file for later use.

## 🛠️ Tech Stack

* **Python 3.10+**
* **Google Gemini API (1.5 Flash)** - For summarization.
* **OpenAI Whisper** - For speech-to-text transcription.
* **yt-dlp** - For audio downloading.
* **YouTube Transcript API** - For fetching captions.

## ⚙️ Installation

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone [https://github.com/denizzozupek/youtube-video-summarize.git](https://github.com/denizzozupek/youtube-video-summarize.git)
cd youtube-video-summarize
````

### 2\. Set Up Virtual Environment

It is recommended to use a virtual environment.

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4\. Install FFmpeg (Crucial\!)

FFmpeg is required for processing audio files when captions are not available.

  * **Windows:** [Download FFmpeg](https://ffmpeg.org/download.html) and add it to your System PATH.
  * **macOS:** `brew install ffmpeg`
  * **Linux:** `sudo apt install ffmpeg`

### 5\. Configure API Key

Create a `.env` file in the root directory and add your Google AI Studio API key.

```ini
GOOGLE_API_KEY=AIzaSy... (Your actual key here)
```

*(You can refer to `.env.example`)*

##  Usage

Run the tool via the command line:

**Basic Usage:**

```bash
python main.py "[https://www.youtube.com/watch?v=VIDEO_ID](https://www.youtube.com/watch?v=VIDEO_ID)"
```

**Save Summary to File:**

```bash
python main.py "[https://www.youtube.com/watch?v=VIDEO_ID](https://www.youtube.com/watch?v=VIDEO_ID)" --save
```

##  Example Output

The tool generates a structured summary like this:

```text
# Video Title: The History of AI

##  Summary
This video explores the major milestones in Artificial Intelligence...

##  Key Points
* The invention of the perceptron in 1958.
* The AI winter and funding cuts.
* The rise of Deep Learning.

##  Things to Learn / Notes
* **Turing Test**: A test of a machine's ability to exhibit intelligent behavior.
* **Neural Networks**: Algorithms modeled after the human brain.
```

##  Disclaimer

This tool is for educational and personal use. Copyright of downloaded content belongs to the respective content creators.

---

