from django.contrib.auth.models import User
from django.db import models


class Quiz(models.Model):
    """
    Represents a quiz entity created by a user based on a YouTube video.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Represents a single question within a Quiz.
    
    Attributes:
        question_text: The actual question string.
        options: A JSON list of possible answers (e.g., ["A", "B"]).
        answer: The correct answer string.
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    question_text = models.CharField(max_length=500)
    options = models.JSONField()
    answer = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text