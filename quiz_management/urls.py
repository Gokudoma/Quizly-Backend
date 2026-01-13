from django.urls import path
from .views import CreateQuizView, GetQuizzesView

urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='create-quiz'),
    path('quizzes/', GetQuizzesView.as_view(), name='get-quizzes'),
]