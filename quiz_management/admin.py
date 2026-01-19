from django.contrib import admin
from .models import Quiz, Question

class QuestionInline(admin.TabularInline):
    """
    Allows questions to be edited inline within the Quiz admin page.
    """
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Quiz model.
    Displays title, associated user, and creation timestamp.
    """
    list_display = ('title', 'user', 'created_at') 
    search_fields = ('title',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Question model.
    Displays the question text, the parent quiz, the correct answer, and creation timestamp.
    Includes filtering by quiz.
    """
    list_display = ('question_text', 'quiz', 'answer', 'created_at')
    list_filter = ('quiz',)

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)