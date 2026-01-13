import os
import json
import re
import yt_dlp
import whisper
from google import genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Quiz, Question
from .serializers import CreateQuizRequestSerializer, QuizResponseSerializer

class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Validate input
        serializer = CreateQuizRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_url = serializer.validated_data['url']
        
        # Extract Video ID to build the clean URL later
        video_id = self.extract_video_id(raw_url)
        if not video_id:
            return Response({"error": "Invalid YouTube URL"}, status=status.HTTP_400_BAD_REQUEST)

        # Helper variables
        clean_url = f"https://www.youtube.com/watch?v={video_id}"
        temp_audio_file = f"audio_{video_id}.mp3"

        try:
            # 2. Download Audio using yt_dlp
            print(f"Downloading audio for {video_id}...")
            self.download_audio(clean_url, temp_audio_file)

            # 3. Transcribe Audio using Whisper AI
            print("Transcribing audio (this may take a moment)...")
            transcript_text = self.transcribe_audio(temp_audio_file)

            # 4. Generate Quiz using Gemini
            print("Generating quiz with Gemini...")
            generated_data = self.generate_with_gemini(transcript_text, clean_url)

            # 5. Save to database
            quiz = Quiz.objects.create(
                user=request.user,
                title=generated_data.get('title', 'Generated Quiz'),
                description=generated_data.get('description', ''),
                video_url=clean_url  # Saving the clean format as requested
            )

            for q_data in generated_data.get('questions', []):
                Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question_title'], 
                    options=q_data['options'],              
                    answer=q_data['answer']
                )

            # 6. Cleanup: Remove the temporary audio file
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
                print("Temporary audio file removed.")

            # 7. Return response
            response_serializer = QuizResponseSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Cleanup on error too
            if os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            
            print(f"Error generating quiz: {e}") 
            return Response(
                {"error": "Internal server error during quiz generation.", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def extract_video_id(self, url):
        """Extracts the 11-character YouTube Video ID."""
        regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(regex, url)
        if match:
            return match.group(1)
        return None

    def download_audio(self, url, filename):
        """Downloads audio track using yt_dlp options."""
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": filename,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        
        # Strip .mp3 from filename for outtmpl to avoid double extension
        base_filename = filename.replace(".mp3", "")
        ydl_opts["outtmpl"] = base_filename

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def transcribe_audio(self, filename):
        """Transcribes the audio file using Whisper AI (Turbo model)."""
        model = whisper.load_model("turbo")
        result = model.transcribe(filename)
        return result["text"]

    def generate_with_gemini(self, transcript_text, video_url):
        """Sends the transcript to Gemini to generate the quiz."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found.")
        
        client = genai.Client(api_key=api_key)

        # Limit transcript length to avoid token limits
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
        
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text)


class GetQuizzesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves all quizzes for the authenticated user.
        Endpoint: GET /api/quizzes/
        """
        try:
            # 1. Retrieve all quizzes owned by the current user, ordered by newest first
            quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')
            
            # 2. Serialize the data
            serializer = QuizResponseSerializer(quizzes, many=True)
            
            # 3. Return the JSON response
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Internal server error fetching quizzes.", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Helper method to get the quiz only if it belongs to the user.
        """
        try:
            return Quiz.objects.get(pk=pk, user=user)
        except Quiz.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Retrieve a single quiz by ID.
        Endpoint: GET /api/quizzes/<id>/
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = QuizResponseSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """
        Update a single quiz by ID (Title, Description) partially.
        Endpoint: PATCH /api/quizzes/<id>/
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # partial=True is key here! It allows updating just the title OR description
        serializer = QuizResponseSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a single quiz by ID.
        Endpoint: DELETE /api/quizzes/<id>/
        """
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        quiz.delete()
        # Return 204 No Content with an empty body as specified
        return Response(status=status.HTTP_204_NO_CONTENT)