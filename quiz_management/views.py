from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz, Question
from .serializers import CreateQuizRequestSerializer, QuizResponseSerializer
from .services import QuizGenerationService


class CreateQuizView(APIView):
    """
    API View to handle the creation of a new quiz from a YouTube URL.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateQuizRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_url = serializer.validated_data['url']

        try:
            generated_data = QuizGenerationService.generate_quiz_from_url(raw_url)

            quiz = Quiz.objects.create(
                user=request.user,
                title=generated_data.get('title', 'Generated Quiz'),
                description=generated_data.get('description', ''),
                video_url=raw_url
            )

            for q_data in generated_data.get('questions', []):
                Question.objects.create(
                    quiz=quiz,
                    question_text=q_data['question_title'],
                    options=q_data['options'],
                    answer=q_data['answer']
                )

            response_serializer = QuizResponseSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Internal server error.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetQuizzesView(APIView):
    """
    API View to retrieve all quizzes for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            quizzes = Quiz.objects.filter(user=request.user).order_by('-created_at')
            serializer = QuizResponseSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Internal server error fetching quizzes.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizDetailView(APIView):
    """
    API View to handle operations on a single quiz instance.
    Supports GET (retrieve), PATCH (update), and DELETE (remove).
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Quiz.objects.get(pk=pk, user=user)
        except Quiz.DoesNotExist:
            return None

    def get(self, request, pk):
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = QuizResponseSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = QuizResponseSerializer(quiz, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        quiz = self.get_object(pk, request.user)
        if not quiz:
            return Response(
                {"error": "Quiz not found or not authorized."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)