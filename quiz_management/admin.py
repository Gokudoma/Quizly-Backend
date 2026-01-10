from django.contrib import admin
from .models import Quiz, Question, Answer

class AnswerInline(admin.TabularInline):
    """
    Allows editing answers directly within the question admin page.
    """
    model = Answer
    extra = 4  # Default to showing 4 answer slots

class QuestionInline(admin.TabularInline):
    """
    Allows editing questions directly within the quiz admin page.
    """
    model = Question
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Questions.
    Includes inline editing for Answers.
    """
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    """
    Admin configuration for Quizzes.
    Includes inline editing for Questions.
    """
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)