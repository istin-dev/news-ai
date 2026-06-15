from django.urls import path
from .views import QuizDashboardView, get_quiz_questions, submit_quiz_result

app_name = 'quiz'

urlpatterns = [
    path('', QuizDashboardView.as_view(), name='dashboard'),
    path('questions/', get_quiz_questions, name='questions'),
    path('submit/', submit_quiz_result, name='submit'),
]
