from django.contrib import admin
from .models import Quiz, Question

# Since we removed the 'Answer' model, we remove AnswerInline

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class QuizAdmin(admin.ModelAdmin):
    # 'author' is now 'user' in our new model
    list_display = ('title', 'user', 'created_at') 
    search_fields = ('title',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    # 'text' is now 'question_text'
    list_display = ('question_text', 'quiz', 'answer', 'created_at')
    list_filter = ('quiz',)

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)