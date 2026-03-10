import pytest
import logging
from unittest.mock import patch, AsyncMock
import litellm.exceptions as exceptions
from summarizer import youtube_text_summarizer

class TestYoutubeTextSummarizer:
    """Tests the interaction with the Universal API Gateway (LiteLLM)."""

    @pytest.fixture(autouse=True)
    def setup_logging(self, caplog):
        """Testler sırasında sadece ERROR (hata) loglarını yakalar."""
        caplog.set_level(logging.ERROR) 

    @pytest.mark.asyncio
    @patch('summarizer.generate_content_safe', new_callable=AsyncMock)
    async def test_success(self, mock_generate):
        """Checks if we get a summary back when everything goes right."""
        # Dublörümüze diyoruz ki: Çağrıldığında bu metni dön.
        mock_generate.return_value = "Özetlenmiş metin"

        transcript = "Bu bir test video transkriptidir. İçeriği özetlenecektir."
        summary = await youtube_text_summarizer(transcript)
        
        assert summary == "Özetlenmiş metin"
        mock_generate.assert_called_once()

    @pytest.mark.asyncio
    @patch('summarizer.generate_content_safe', new_callable=AsyncMock)
    async def test_auth_error(self, mock_generate, caplog):
        """Ensures the app handles missing/invalid API keys gracefully."""
        # LiteLLM API anahtarı bulamazsa AuthenticationError fırlatır.
        mock_generate.side_effect = exceptions.AuthenticationError(
            message="API Key not found", 
            llm_provider="openai", 
            model="gpt-4o-mini"
        )

        transcript = "Bu bir test video transkriptidir."
        summary = await youtube_text_summarizer(transcript)
        
        assert summary is None
        assert "api key is missing or invalid" in caplog.text.lower()

    @pytest.mark.asyncio
    @patch('summarizer.generate_content_safe', new_callable=AsyncMock)
    async def test_token_limit_exceeded(self, mock_generate, caplog):
        """Tests if we handle the 'text too long' error without crashing."""
        mock_generate.side_effect = exceptions.ContextWindowExceededError(
            message="Token limit exceeded", 
            llm_provider="openai", 
            model="gpt-4o-mini"
        )

        transcript = "Bu bir test video transkriptidir."
        summary = await youtube_text_summarizer(transcript)
        
        assert summary is None
        assert "token limit exceeded" in caplog.text.lower()

    @pytest.mark.asyncio
    @patch('summarizer.generate_content_safe', new_callable=AsyncMock)
    async def test_rate_limit_error(self, mock_generate, caplog):
        """Tests if we inform the user correctly when the API quota runs out."""
        mock_generate.side_effect = exceptions.RateLimitError(
            message="Quota exceeded", 
            llm_provider="openai", 
            model="gpt-4o-mini"
        )

        transcript = "Bu bir test video transkriptidir."
        summary = await youtube_text_summarizer(transcript)

        assert summary is None
        assert "api quota exceeded or rate limited" in caplog.text.lower()

    @pytest.mark.asyncio
    @patch('summarizer.generate_content_safe', new_callable=AsyncMock)
    async def test_api_failure(self, mock_generate, caplog):
        """Checks handling of generic API errors."""
        error_message = "Generic API Error"
        mock_generate.side_effect = Exception(error_message)

        transcript = "Bu bir test video transkriptidir."
        summary = await youtube_text_summarizer(transcript)
        
        assert summary is None
        assert error_message in caplog.text