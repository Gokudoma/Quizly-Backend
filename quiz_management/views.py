import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
from django.contrib.auth.models import User
from .models import Quiz, Question, Answer

load_dotenv()

class AnswerAI(BaseModel):
    text: str
    is_correct: bool

class QuestionAI(BaseModel):
    text: str
    type: str
    points: int
    answers: list[AnswerAI]

class QuizAI(BaseModel):
    title: str
    description: str
    questions: list[QuestionAI]

@csrf_exempt
def generate_quiz_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', 'General Knowledge')
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({'error': 'API Key missing'}, status=500)

            client = genai.Client(api_key=api_key)

            prompt = f"Create a quiz about: '{topic}'. Language: German."

            response = client.models.generate_content(
                model='gemini-2.0-flash', 
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': QuizAI,
                }
            )

            quiz_data: QuizAI = response.parsed

            user = request.user if request.user.is_authenticated else None
            # Fallback to first user/admin if no user is logged in
            if not user:
                user = User.objects.first()
                if not user:
                     return JsonResponse({'error': 'No user found in database. Please create a superuser.'}, status=500)

            new_quiz = Quiz.objects.create(
                title=quiz_data.title,
                description=quiz_data.description,
                author=user
            )

            for q_data in quiz_data.questions:
                new_question = Question.objects.create(
                    quiz=new_quiz,
                    text=q_data.text,
                    question_type=q_data.type,
                    points=q_data.points
                )
                
                for a_data in q_data.answers:
                    Answer.objects.create(
                        question=new_question,
                        text=a_data.text,
                        is_correct=a_data.is_correct
                    )

            return JsonResponse({
                'message': 'Quiz created successfully', 
                'quiz_id': new_quiz.id, 
                'title': new_quiz.title
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)