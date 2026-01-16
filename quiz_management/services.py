import json
import os
import tempfile
from pathlib import Path

import whisper
import yt_dlp
from google import genai
from django.conf import settings

from .utils import extract_youtube_video_id, find_file_by_prefix, clean_ai_json_response


class QuizGenerationService:
    """
    Service class to handle the complex logic of generating a quiz from a YouTube URL.
    Delegates generic tasks to utils.py.
    """

    @staticmethod
    def generate_quiz_from_url(url):
        """
        Orchestrates the quiz generation process.
        """
        video_id = extract_youtube_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_filename_base = temp_path / f"audio_{video_id}"
            
            audio_path = QuizGenerationService._download_audio(url, temp_filename_base)
            transcript = QuizGenerationService._transcribe_audio(audio_path)
            quiz_data = QuizGenerationService._generate_with_gemini(transcript, url)
            
            return quiz_data

    @staticmethod
    def _download_audio(url, filename_base):
        """
        Downloads audio via yt-dlp and locates the resulting file using utils.
        """
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{filename_base}.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        directory = filename_base.parent
        prefix = filename_base.name
        
        audio_file = find_file_by_prefix(directory, prefix, ".mp3")
        
        if not audio_file:
            raise FileNotFoundError("Audio download failed or file not found.")
            
        return audio_file

    @staticmethod
    def _transcribe_audio(filepath):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
            
        model = whisper.load_model("base")
        result = model.transcribe(filepath, fp16=False)
        return result["text"]

    @staticmethod
    def _generate_with_gemini(transcript_text, video_url):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found.")
        
        client = genai.Client(api_key=api_key)
        short_transcript = transcript_text[:25000]

        prompt = f"""
        You are a quiz generator. Analyze the following TRANSCRIPT of a video (URL: {video_url}).
        
        TRANSCRIPT:
        "{short_transcript}"
        
        Create a quiz in GERMAN (Deutsch) based strictly on this text.
        Structure:
        {{
            "title": "Deutscher Titel",
            "description": "Kurze Beschreibung",
            "questions": [
                {{
                    "question_title": "Frage?",
                    "options": ["A", "B", "C", "D"],
                    "answer": "A"
                }}
            ]
        }}
        IMPORTANT: Respond ONLY with raw JSON (no markdown). All text must be German.
        """

        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        
        return json.loads(clean_ai_json_response(response.text))