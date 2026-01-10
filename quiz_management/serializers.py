from rest_framework import serializers
from .models import Quiz, Question, Answer

class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer for the Answer model.
    """
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Question model.
    Includes nested AnswerSerializer to show options.
    """
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'answers']

class QuizListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing quizzes.
    Shows basic info like title and question count.
    """
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at', 'question_count']

    def get_question_count(self, obj):
        """
        Returns the number of questions in the quiz.
        """
        return obj.questions.count()

class QuizDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed quiz view.
    Includes nested questions and answers.
    """
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at', 'questions']