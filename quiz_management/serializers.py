from rest_framework import serializers
from .models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
    # Map internal model fields to API specification names
    question_title = serializers.CharField(source='question_text')
    question_options = serializers.JSONField(source='options')

    class Meta:
        model = Question
        # Defined explicit order, removed timestamps for cleaner output
        fields = ['id', 'question_title', 'question_options', 'answer']

class QuizResponseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        # Explicit field order to match documentation
        fields = [
            'id', 
            'title', 
            'description', 
            'created_at', 
            'updated_at', 
            'video_url', 
            'questions'
        ]

class CreateQuizRequestSerializer(serializers.Serializer):
    url = serializers.URLField()