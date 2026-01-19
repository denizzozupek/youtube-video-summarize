import pytest
from unittest.mock import MagicMock
from main import main
import google.generativeai as genai
import sys

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Automatically mocks API keys and models for all tests in this file."""
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
    mock_api = MagicMock(return_value=None)
    monkeypatch.setattr(genai, "configure", mock_api)

    mock_model = MagicMock()
    mock_model.generate_content.return_value.text = "Özetlenmiş metin"
    monkeypatch.setattr(genai, "GenerativeModel", mock_model)
    return mock_model

class TestSuccessScenarios:
    """Tests the happy paths where the program runs successfully."""
    def test_success_scenario(self, monkeypatch, capsys, tmp_path):
        """Tests the full flow: fetching, summarizing, and saving to a real temporary file."""
        
        test_url = "https://youtu.be/video123"
        test_args = ["main.py", test_url, "--save"]
        monkeypatch.setattr(sys, "argv", test_args)

        mock_text = MagicMock(return_value="This is a transcripted text")
        mock_summarize = MagicMock(return_value="This is an summary")
        mock_id = MagicMock(return_value="id123")

        monkeypatch.setattr("main.get_transcripted_text", mock_text)
        monkeypatch.setattr("main.youtube_text_summarizer", mock_summarize)
        monkeypatch.setattr("main.get_video_id_from_youtube_url", mock_id)
        
        monkeypatch.chdir(tmp_path)

        assert main() == 0
        
        captured = capsys.readouterr()

        assert "This is an summary" in captured.out
        assert "Summary saved to summary_id123.md" in captured.out
        
        saved_file = tmp_path / "summary_id123.md"
        assert saved_file.exists()
        assert saved_file.read_text(encoding="utf-8") == "This is an summary"

        mock_text.assert_called_once_with(test_url)
        mock_summarize.assert_called_once_with("This is a transcripted text")
        mock_id.assert_called_once_with(test_url)
    
    def test_success_with_timestamp_filename(self, monkeypatch, capsys, tmp_path):
        """Ensures we use a timestamp for the filename if video ID extraction fails."""
        test_args = ["main.py", "https://youtu.be/video123", "--save"]
        monkeypatch.setattr(sys, "argv", test_args)

        mock_text = MagicMock(return_value="This is a transcripted text")
        mock_summarize = MagicMock(return_value="This is an summary")
        mock_id = MagicMock(return_value=None)

        monkeypatch.setattr("main.get_transcripted_text", mock_text)
        monkeypatch.setattr("main.youtube_text_summarizer", mock_summarize)
        monkeypatch.setattr("main.get_video_id_from_youtube_url", mock_id)

        monkeypatch.chdir(tmp_path)

        mock_datetime = MagicMock()
        mock_datetime.now.return_value.strftime.return_value = "20251226_120000"
        monkeypatch.setattr("main.datetime", mock_datetime)

        assert main() == 0

        captured = capsys.readouterr()
        expected_filename = "summary_20251226_120000.md"
        assert f"Summary saved to {expected_filename}" in captured.out

        saved_file = tmp_path / expected_filename
        assert saved_file.exists()
        assert saved_file.read_text(encoding="utf-8") == "This is an summary"
    
class TestFailureScenarios:
    """Tests various error conditions to ensure the program exits gracefully."""

    def test_no_api_key_failure(self, monkeypatch, capsys):
        """Checks if the program exits with error code 1 when API key is missing."""
        test_args = ["main.py", "https://youtu.be/video123"]
        monkeypatch.setattr(sys, "argv", test_args)

        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        assert main() == 1

        captured = capsys.readouterr()
        assert "Error: GOOGLE_API_KEY not found" in captured.out
    
    def test_failed_because_transcript(self, monkeypatch, capsys):
        """Tests behavior when the transcript cannot be fetched."""
        test_args = ["main.py", "https://youtu.be/video123"]
        monkeypatch.setattr(sys, "argv", test_args)
        
        mock_transcripted_text = MagicMock(return_value=None)

        monkeypatch.setattr("main.get_transcripted_text", mock_transcripted_text)
        
        assert main() == 1

        captured = capsys.readouterr()
        assert "Error: Unable to fetch transcript for the provided video URL." in captured.out

        mock_transcripted_text.assert_called_once_with("https://youtu.be/video123")

    def test_failed_because_summary(self, monkeypatch, capsys):
        """Test fail when the summarization step fails"""
        test_args = ["main.py", "https://youtu.be/video123"]
        monkeypatch.setattr(sys, "argv", test_args)

        mock_text = MagicMock(return_value="This is a transcripted text")
        mock_summarize = MagicMock(return_value=None)

        monkeypatch.setattr("main.get_transcripted_text", mock_text)
        monkeypatch.setattr("main.youtube_text_summarizer", mock_summarize)

        assert main() == 1

        captured = capsys.readouterr()
        assert "Error: Summarization failed." in captured.out

        mock_text.assert_called_once()
        mock_summarize.assert_called_once()
    
    def test_failed_because_keyboard_interrupt(self, monkeypatch, capsys):
        """Clean exit if the user presses Ctrl+C."""
        test_args = ["main.py", "https://youtu.be/video123"]
        monkeypatch.setattr(sys, "argv", test_args)

        mock_interrupt = MagicMock(side_effect=KeyboardInterrupt)
        monkeypatch.setattr("main.get_transcripted_text", mock_interrupt)
       
        assert main() == 0

        captured = capsys.readouterr()
        assert "Process interrupted by user. Exiting..." in captured.out

    def test_failed_exception(self, monkeypatch, capsys):
        """Checks if unexpected errors are caught and logged."""
        test_args = ["main.py", "https://youtu.be/video123"]
        monkeypatch.setattr(sys, "argv", test_args)

        mock_error = MagicMock(side_effect=Exception("An unknown error occured"))
        monkeypatch.setattr("main.get_transcripted_text", mock_error)

        assert main() == 1

        captured = capsys.readouterr()

        assert "An unknown error occured" in captured.out