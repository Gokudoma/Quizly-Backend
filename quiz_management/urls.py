from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_quiz_view, name='generate_quiz'),
]