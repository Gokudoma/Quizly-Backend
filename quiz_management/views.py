from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz
from .serializers import QuizListSerializer, QuizDetailSerializer

class QuizListView(ListAPIView):
    """
    API View to retrieve the list of all quizzes.
    Uses QuizListSerializer to display basic information.
    """
    queryset = Quiz.objects.all().order_by('-created_at')
    serializer_class = QuizListSerializer

class QuizDetailView(RetrieveAPIView):
    """
    API View to retrieve a single quiz by ID.
    Uses QuizDetailSerializer to display full quiz details including questions.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    lookup_field = 'pk'