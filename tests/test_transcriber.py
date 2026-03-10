import pytest
import logging
from unittest.mock import MagicMock, AsyncMock
from transcriber import get_video_id_from_youtube_url, get_transcripted_text, TranscriptFetch
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound

@pytest.mark.parametrize("url, expected_id", [
        ("https://www.youtube.com/watch?v=6NQUbFiUYRw", "6NQUbFiUYRw" ),
        ("https://youtu.be/6NQUbFiUYRw", "6NQUbFiUYRw"),
        #youtube share url
        ("https://youtu.be/6NQUbFiUYRw?si=DEjTkGxb5EP2xBu7", "6NQUbFiUYRw"),
        ("https://google.com", None),
        ("", None),
        ("This is a string, not a link", None)
        ])

def test_video_id_extraction(url, expected_id):
    """Tests if we can correctly extract video IDs from different URL formats"""
    result = get_video_id_from_youtube_url(url)
    assert result == expected_id

class TestFetchTranscript:
    """Tests for the TranscriptFetch class to ensure it handles API responses correctly."""
    @pytest.fixture
    def fetcher(self):
        """Sets up a TranscriptFetch instance with a mocked API so we don't call the real YouTube.
        """
        mock_api = MagicMock()
        mock_list = MagicMock()
        mock_api.list.return_value = mock_list

        fetcher_mock = TranscriptFetch()
        fetcher_mock.ytt_api = mock_api
        
        fetcher_mock.mock_api = mock_api
        fetcher_mock.mock_list = mock_list
        return fetcher_mock
    
    @pytest.fixture(autouse=True)
    def setup_logging(self, caplog):
        caplog.set_level(logging.ERROR)
    
    @pytest.mark.asyncio
    async def test_get_manual_transcript_obj_success(self, fetcher):
        """Verifies that the manual transcript is retrieved if available."""
        fetcher.mock_list.find_transcript.return_value = "Manual Transcript Object"
        
        result = await fetcher.get_transcript_obj("valid_video_id")
        assert result == "Manual Transcript Object"
        fetcher.mock_list.find_transcript.assert_called_with(['tr', 'en'])

    @pytest.mark.asyncio
    async def test_get_transcript_object_success_generated(self, fetcher):
        """hecks if the code falls back to auto-generated transcripts when manual ones are missing."""
        fetcher.mock_list.find_transcript.side_effect = NoTranscriptFound("id", [], "")
        fetcher.mock_list.find_generated_transcript.return_value = "Generated Transcript"
        
        result = await fetcher.get_transcript_obj("valid_video_id")
        
        assert result == "Generated Transcript"
        fetcher.mock_list.find_generated_transcript.assert_called_with(['tr', 'en'])
    
    @pytest.mark.asyncio
    async def test_fetch_list_api_error(self, fetcher, caplog):
        """Verifies proper error handling when transcripts are disabled or not found."""
        fetcher.mock_api.list.side_effect = TranscriptsDisabled("Disabled")
        
        result = await fetcher.get_transcript_obj("valid_video_id")
        
        assert result is None
        assert "No transcripts found or disabled" in caplog.text
    
    @pytest.mark.asyncio
    async def test_neihter_transcript_found(self, fetcher, caplog):
        """Verifies that none is returned when neither manual nor generated transcripts exist."""
        fetcher.mock_list.find_transcript.side_effect = NoTranscriptFound("id", [], "")
        fetcher.mock_list.find_generated_transcript.side_effect = NoTranscriptFound("id", [], "")
        
        result = await fetcher.get_transcript_obj("valid_video_id")
        
        assert result is None
        assert "No transcript available for this video" in caplog.text

class TestGetTranscriptedText:
    """Integration style tests for the main get_transcripted_text function."""

    @pytest.mark.asyncio
    async def test_success(self, monkeypatch):
        """Tests the successful flow: ID extraction -> fetch -> format."""
        mock_id = MagicMock(return_value="valid_video_id")
        monkeypatch.setattr("transcriber.get_video_id_from_youtube_url",mock_id)
        
        mock_fetcher_instance = AsyncMock()
        mock_transcript_obj = MagicMock()
        
        mock_fetcher_instance.get_transcript_obj.return_value = mock_transcript_obj
        mock_transcript_obj.fetch.return_value = [{'text': 'Test Metni'}]
        
        mock_fetcher_class = MagicMock(return_value=mock_fetcher_instance)
        monkeypatch.setattr("transcriber.TranscriptFetch", mock_fetcher_class)
        
        mock_formatter = MagicMock()
        mock_formatter.format_transcript.return_value = "Test Metni"

        mock_formatter_class = MagicMock(return_value=mock_formatter)
        monkeypatch.setattr("transcriber.TextFormatter", mock_formatter_class)
        
        result = await get_transcripted_text("http://youtube.com/watch?v=valid_video_id")
        
        assert result == "Test Metni"

        mock_id.assert_called_once_with("http://youtube.com/watch?v=valid_video_id")
        mock_fetcher_class.assert_called_once()
        mock_formatter_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_fail_invalid_url(self, caplog):
        """Verifies immediate exit when an invalid URL is provided."""
        result = await get_transcripted_text("invalid_url")
        assert result is None
        assert "Invalid YouTube URL provided" in caplog.text


        