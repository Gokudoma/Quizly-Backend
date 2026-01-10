from django.db import models

class Quiz(models.Model):
    """
    Model representing a quiz.
    Contains basic information like title and creation timestamp.
    """
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.title

class Question(models.Model):
    """
    Model representing a single question within a quiz.
    Linked to a specific Quiz instance.
    """
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    
    def __str__(self):
        return self.text

class Answer(models.Model):
    """
    Model representing an answer option for a question.
    Linked to a specific Question instance.
    Stores whether this answer is the correct one.
    """
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text