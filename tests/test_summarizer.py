import pytest
import logging
from unittest.mock import MagicMock
from summarizer import youtube_text_summarizer
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument, ResourceExhausted


class TestYoutubeTextSummarizer:
    """Tests the interaction with the Google Gemini API."""

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Sets up a fake environment with a mock API key and Gemini model."""
        monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
        mock_api_configure = MagicMock(return_value=None)
        monkeypatch.setattr(genai, "configure", mock_api_configure)

        mock_model = MagicMock()
        mock_model.generate_content.return_value.text = "Özetlenmiş metin"

        mock_model_configure = MagicMock(return_value=mock_model)
        monkeypatch.setattr(genai, "GenerativeModel", mock_model_configure)
        
        return mock_model
    
    @pytest.fixture(autouse=True)
    def setup_logging(self, caplog):
        caplog.set_level(logging.ERROR) 

    def test_success(self , mock_env):
        """Checks if we get a summary back when everything goes right."""
        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        summary = youtube_text_summarizer(transcript)
        assert summary == "Özetlenmiş metin"

        mock_env.generate_content.assert_called_once()
        
    def test_no_api_key(self, monkeypatch):
        """Ensures the app crashes intentionally if the API key is missing."""
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        with pytest.raises(ValueError, match="GOOGLE_API_KEY not found."):
            youtube_text_summarizer(transcript)
    
    def test_token_limit_exceeded(self, mock_env, caplog):
        """Tests if we handle the 'text too long' error without crashing."""
        mock_env.generate_content.side_effect = InvalidArgument("Token limit exceeded")

        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        summary = youtube_text_summarizer(transcript)
        assert summary is None
        assert "token limit exceeded" in caplog.text.lower()

    def test_api_failure(self, mock_env, caplog):
        """Checks handling of generic API errors."""
        error_message = "Google API Error"
        mock_env.generate_content.side_effect = Exception(error_message)

        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        summary = youtube_text_summarizer(transcript)
        assert summary is None
        assert error_message in caplog.text
    
    def test_resource_exhausted(self, mock_env, caplog):
        """Tests if we inform the user correctly when the API quota runs out."""
        mock_env.generate_content.side_effect = ResourceExhausted("error_message")

        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        summary = youtube_text_summarizer(transcript)

        assert summary is None
        assert "API quota exceeded (Resource Exhausted)" in caplog.text