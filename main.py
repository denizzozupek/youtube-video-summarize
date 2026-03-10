from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from transcriber import get_transcripted_text, get_video_id_from_youtube_url
from summarizer import youtube_text_summarizer
import logging
from contextlib import asynccontextmanager
import aiosqlite

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_NAME = "video_summaries.db"


async def initialize_database():
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT UNIQUE,
                summary TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        await conn.commit()

async def worker(queue: asyncio.Queue[str]) -> None:
    """Asynchronous worker function which works on the background to process video URLs from the queue."""
    while True:
        video_url = await queue.get()
        video_id = get_video_id_from_youtube_url(video_url)
        logger.info(f"Processing video: {video_url}")
        
        try:
            async with aiosqlite.connect(DB_NAME) as conn:
                cursor = await conn.cursor()
                await cursor.execute('UPDATE summaries SET status = ? WHERE video_id = ?', ('processing', video_id))
                await conn.commit()

            transcript = await get_transcripted_text(video_url)
            if not transcript:
                logger.error(f"Unable to fetch transcript for the video URL: {video_url}")
                async with aiosqlite.connect(DB_NAME) as conn:
                    cursor = await conn.cursor()
                    await cursor.execute('UPDATE summaries SET status = ? WHERE video_id = ?', ('error', video_id))
                    await conn.commit()
                continue
            
            summary = await youtube_text_summarizer(transcript)

            if summary:
                async with aiosqlite.connect(DB_NAME) as conn:
                    cursor = await conn.cursor()
                    await cursor.execute('INSERT OR REPLACE INTO summaries (video_id, summary, status) VALUES (?, ?, ?)',
                                         (video_id, summary, 'completed'))
                    await conn.commit()

                logger.info(f"Summary generated successfully for video: {video_url}")

            else:
                logger.error(f"Summarization failed for video: {video_url}")
                async with aiosqlite.connect(DB_NAME) as conn:
                    cursor = await conn.cursor()
                    await cursor.execute('UPDATE summaries SET status = ? WHERE video_id = ?', ('error', video_id))
                    await conn.commit()

        except asyncio.CancelledError:
            logger.info("Worker task cancelled.")
            raise

        except Exception as e:
            logger.error(f"An error occurred while processing video URL: {video_url}. Error: {str(e)}")
            async with aiosqlite.connect(DB_NAME) as conn:
                cursor = await conn.cursor()
                await cursor.execute('UPDATE summaries SET status = ? WHERE video_id = ?', ('error', video_id))
                await conn.commit()
            continue

        finally:
            queue.task_done()

@asynccontextmanager
async def fastapi_queue(app: FastAPI):
    """Initialize database, background task to process video URLs from the queue."""
    logger.info("Initializing database...")
    await initialize_database()
    logger.info("Database initialized successfully.")

    # remove zombie tasks if any
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute('UPDATE summaries SET status = ? WHERE status IN (?, ?)', ('pending', 'processing', 'pending'))
    logger.info("Reset any pending or processing tasks to pending status.")

    app.state.queue = asyncio.Queue()
    app.state.queue_task = asyncio.create_task(worker(app.state.queue))
    logger.info("Background worker task started. Listening for video URLs...")

    yield

    app.state.queue_task.cancel()

    try:
        await app.state.queue_task
    except asyncio.CancelledError:
        pass

    logger.info("Background worker task cancelled successfully.")

app = FastAPI(lifespan=fastapi_queue)


class VideoURL(BaseModel):
    url: str

@app.post("/summarize")
async def summarize_video(video: VideoURL) -> dict:
    """Endpoint to receive a YouTube video URL and add it to the processing queue.
    """
    video_url = video.url
    logger.info(f"Received video URL: {video_url}")

    video_id = get_video_id_from_youtube_url(video_url)
    if not video_id:
        logger.error(f"Invalid YouTube URL provided: {video_url}")
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
    
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT status, summary FROM summaries WHERE video_id = ?', (video_id,))
        record = await cursor.fetchone()

        if record:
            status, summary = record
            if status == 'completed':
                logger.info(f"Summary already exists for video: {video_url}")
                return {"summary": summary}
            else:
                logger.info(f"Video is currently being processed: {video_url}")
                await cursor.execute('UPDATE summaries SET status = ? WHERE video_id = ?', ('processing', video_id))
                await conn.commit()
                await app.state.queue.put(video_url)
                return {"status": "processing", "message": "Video is currently being processed. Please check back later."}
        else:
            await cursor.execute('INSERT INTO summaries (video_id, status) VALUES (?, ?)', (video_id, 'pending'))
            await conn.commit()
            logger.info(f"New video URL added to the database with pending status: {video_url}")

    await app.state.queue.put(video_url)
    logger.info(f"Video URL added to the queue: {video_url}")
    return {"message": "Video URL received and added to the processing queue."}