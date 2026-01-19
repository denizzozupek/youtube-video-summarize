import pytest
from unittest.mock import MagicMock
import main
import sys
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

def test_end_to_end_flow(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key")
    mock_api_configure = MagicMock(return_value=None)
    monkeypatch.setattr(genai, "configure", mock_api_configure)
    monkeypatch.chdir(tmp_path)

    mock_transcript_obj = MagicMock()
    mock_transcript_obj.text = "This is a test transcript."
    mock_transcript_obj.start = 0.0
    mock_transcript_obj.duration = 5.0

    mock_transcript_data = [mock_transcript_obj]
    
    mock_transcript_item = MagicMock()
    mock_transcript_item.fetch.return_value = mock_transcript_data

    mock_transcript_list = MagicMock()
    mock_transcript_list.find_transcript.return_value = mock_transcript_item

    mock_api_instance = MagicMock()
    mock_api_instance.list_transcripts.return_value = mock_transcript_list

    mock_api_class = MagicMock(return_value=mock_api_instance)
    monkeypatch.setattr("transcriber.YouTubeTranscriptApi", mock_api_class)

    mock_response = MagicMock()
    mock_response.text = "This is a summarized text"

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    mock_model_configure = MagicMock(return_value=mock_model)
    monkeypatch.setattr(genai, "GenerativeModel", mock_model_configure)

    fake_video_id ="test_id"
    test_args = ["main.py", f"https://youtu.be/watch?v={fake_video_id}", "--save"]

    monkeypatch.setattr(sys, "argv", test_args)

    exit_code = main.main()

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Transcript fetched successfully" in captured.out
    assert "Summarizing transcript..." in captured.out
    assert "This is a summarized text" in captured.out 

    saved_file = tmp_path / f"summary_{fake_video_id}.md"
    assert saved_file.exists()
    assert saved_file.read_text(encoding="utf-8") == "This is a summarized text"

    mock_api_configure.assert_called_once_with(api_key="test_api_key")
    mock_api_instance.list_transcripts.assert_called_once_with(fake_video_id)
    mock_model_configure.assert_called_once()
    mock_model.generate_content.assert_called_once()

