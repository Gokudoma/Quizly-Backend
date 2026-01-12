import os
import json
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
        # 1. Validate input (URL)
        serializer = CreateQuizRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        video_url = serializer.validated_data['url']

        try:
            # 2. Call logic to generate quiz data via Gemini
            generated_data = self.generate_with_gemini(video_url)

            # 3. Save to database
            quiz = Quiz.objects.create(
                user=request.user,
                title=generated_data.get('title', 'Generated Quiz'),
                description=generated_data.get('description', ''),
                video_url=video_url
            )

            for q_data in generated_data.get('questions', []):
                Question.objects.create(
                    quiz=quiz,
                    # API prompt returns 'question_title'
                    question_text=q_data['question_title'], 
                    # API prompt returns 'options'
                    options=q_data['options'],              
                    answer=q_data['answer']
                )

            # 4. Return formatted response
            response_serializer = QuizResponseSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log error for server-side debugging
            print(f"Error generating quiz: {e}") 
            return Response(
                {"error": "Internal server error during quiz generation.", "details": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_with_gemini(self, video_url):
        """
        Interacts with the Google Gemini API (new SDK) to generate quiz questions.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise Exception("GEMINI_API_KEY not found in environment variables.")
        
        # Initialize the client with the new SDK syntax
        client = genai.Client(api_key=api_key)

        # Construct prompt enforcing strictly valid JSON
        prompt = f"""
        You are a quiz generator. Analyze the content or topic of this YouTube video URL: {video_url}.
        
        Create a quiz with a title, a short description, and 3 to 5 questions.
        Each question must have exactly 4 options.
        
        IMPORTANT: Respond ONLY with raw JSON. Do not use Markdown formatting (no ```json or ```).
        Use exactly this structure:
        {{
            "title": "Quiz Title",
            "description": "Short description of the topic",
            "questions": [
                {{
                    "question_title": "The question text?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A"
                }}
            ]
        }}
        The 'answer' field must exactly match one of the strings in the 'options' array.
        """

        # Generate content using the new client.models syntax
        # SELECTED MODEL: 'gemini-flash-latest' maps to the current stable version (likely 1.5)
        # This usually has a much higher free quota than the 2.0 series.
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt
        )
        
        # Parse and clean response
        response_text = response.text.strip()
        
        # Clean up potential markdown formatting if Gemini adds it despite instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        return json.loads(response_text)