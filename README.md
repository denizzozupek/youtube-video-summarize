# YouTube Video Summarizer API 🎥

<div align="center">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python" />
  <img src="https://img.shields.io/badge/fastapi-109989?style=for-the-badge&logo=FASTAPI&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
</div>

<br>

This project is an MVP (Minimum Viable Product) I developed to learn and practice **asynchronous programming (asyncio)**, background workers, and non-blocking API architectures in Python. 

It provides an asynchronous REST API that takes a YouTube URL, extracts the video transcript, and summarizes it using AI (OpenAI, Gemini, etc.) via LiteLLM.

## Why This Architecture? (Learning Outcomes)

AI models take time to generate responses (sometimes 30-40 seconds). If I had built a traditional, synchronous API, the client would be forced to wait for the entire process to finish, risking "Timeout" errors and blocking the server from handling other requests.

To solve this, I designed the system around an **Asynchronous Polling (Queue) Architecture**:
1. **The Receptionist (FastAPI):** Instantly accepts the URL, creates a database record with a "pending" status, and immediately returns a `{"status": "processing"}` response without blocking the main thread.
2. **The Queue (`asyncio.Queue`):** The URL is placed into an in-memory queue.
3. **The Worker (Background Task):** Running silently in the background, it picks up URLs from the queue, fetches transcripts, calls the LLM, and updates the database with the final summary.
4. **The Database (`aiosqlite`):** All database operations are fully asynchronous to prevent I/O bottlenecks.

## Technologies Used

* **FastAPI:** Modern, fast web framework for building async APIs.
* **asyncio & aiosqlite:** For background tasks and non-blocking database operations.
* **LiteLLM:** A standardized interface to call various LLMs (OpenAI, Anthropic, Gemini) using the same format.
* **YouTube Transcript API:** To extract subtitles/captions directly from YouTube videos.
* **pytest & pytest-asyncio:** For robust unit testing with database isolation.

## 🚀 Setup & Installation

Follow these steps to run the project locally.

**1. Clone the repository:**
```bash
git clone https://github.com/denizzozupek/youtube-video-summarize
cd youtube-video-summarize

```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

```

**3. Install dependencies:**

```bash
pip install -r requirements.txt

```

**4. Set up environment variables:**
Rename the `.env.example` file to `.env` in the root directory and add your API key:

```env
OPENAI_API_KEY=sk-your-api-key-here
MODEL_NAME=openai/gpt-4o-mini

```

**5. Start the application:**

```bash
uvicorn main:app --reload

```

## How to Use the API (Polling Logic)

Because the system is asynchronous, retrieving a summary is a two-step polling process:

**System Responses:**

* **First Request (Added to Queue):**
  ```json
  {
      "message": "Video URL received and added to the processing queue."
  }
  ```



* **If you ask again while processing:**
```json
{
    "status": "processing", 
    "message": "Video is currently being processed. Please check back later."
}

```


* **When it's done (Summary Ready):**
```json
{
    "summary": "The excellent AI-generated summary of the video will appear here..."
}

```

##  Testing

The project includes a test suite with database isolation to prevent state leakage between tests. To run the tests:

```bash
python -m pytest

```

## Future Improvements (Roadmap)

Since this is a learning MVP, some architectural decisions were kept simple. Future iterations could include:

* Replacing `asyncio.Queue` with **Redis or RabbitMQ** to prevent data loss in case of server crashes.
* Migrating from SQLite to **PostgreSQL** for a production-ready database.
* Implementing multiple background workers to enable horizontal scaling.

