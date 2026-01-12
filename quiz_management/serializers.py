from rest_framework import serializers
from .models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
    # Mapping internal field names to API specification
    question_title = serializers.CharField(source='question_text')
    question_options = serializers.JSONField(source='options')

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

class QuizResponseSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']

class CreateQuizRequestSerializer(serializers.Serializer):
    url = serializers.URLField()