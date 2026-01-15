from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model.
    Maps internal model fields to API specification names.
    """
    question_title = serializers.CharField(source='question_text')
    question_options = serializers.JSONField(source='options')

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']


class QuizResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for sending Quiz data to the client.
    Includes nested questions.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
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
    """
    Serializer for validating the quiz creation request.
    Requires a valid YouTube URL.
    """
    url = serializers.URLField()