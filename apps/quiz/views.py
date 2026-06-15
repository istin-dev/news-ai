from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Max
from django.conf import settings
import random

from apps.news.models import News
from .models import QuizAttempt
from apps.analytics.models import Analytics

class QuizDashboardView(TemplateView):
    template_name = 'quiz/quiz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get count of articles with MCQs
        context['total_mcqs'] = News.objects.exclude(mcq_question__isnull=True).exclude(mcq_question='').count()
        # Group MCQ counts by category
        context['category_counts'] = {
            cat[0]: News.objects.filter(category=cat[0]).exclude(mcq_question__isnull=True).exclude(mcq_question='').count()
            for cat in settings.NEWS_CATEGORIES
        }
        return context

def get_quiz_questions(request):
    """API endpoint to get random MCQ questions based on category and count."""
    category = request.GET.get('category', 'All')
    count = int(request.GET.get('count', 10))

    queryset = News.objects.exclude(mcq_question__isnull=True).exclude(mcq_question='')
    if category != 'All':
        queryset = queryset.filter(category=category)

    # Convert queryset to list and sample randomly
    news_list = list(queryset)
    sample_size = min(len(news_list), count)
    random_news = random.sample(news_list, sample_size) if news_list else []

    questions = []
    for news in random_news:
        questions.append({
            'id': news.id,
            'title': news.title,
            'category': news.category,
            'question': news.mcq_question,
            'options': news.mcq_options,
            'answer': news.mcq_answer,
            'explanation': news.mcq_explanation,
            'url': news.get_absolute_url() if hasattr(news, 'get_absolute_url') else f"/news/{news.slug}/"
        })

    return JsonResponse({'questions': questions})

def submit_quiz_result(request):
    """API endpoint to record quiz results and increment analytics."""
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            category = data.get('category', 'All')
            total = data.get('total', 0)
            correct = data.get('correct', 0)
            question_ids = data.get('question_ids', [])

            # Record quiz attempt
            QuizAttempt.objects.create(
                category=category,
                total_questions=total,
                correct_answers=correct
            )

            # Update analytics table for each question
            for q_id in question_ids:
                try:
                    news = News.objects.get(id=q_id)
                    from django.utils.timezone import now
                    analytics, created = Analytics.objects.get_or_create(
                        news=news,
                        date=now().date(),
                        defaults={'views': 0, 'quiz_attempts': 1}
                    )
                    if not created:
                        analytics.quiz_attempts += 1
                        analytics.save()
                except News.DoesNotExist:
                    continue

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
