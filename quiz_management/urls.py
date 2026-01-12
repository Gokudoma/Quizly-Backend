from django.urls import path
from .views import CreateQuizView

urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='create-quiz'),
]