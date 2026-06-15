from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg
from django.utils.timezone import now
from datetime import timedelta

from apps.news.models import News
from apps.quiz.models import QuizAttempt
from apps.bookmarks.models import Bookmark
from .models import Analytics

class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Date 7 days ago
        today = now().date()
        seven_days_ago = today - timedelta(days=7)

        # 1. Total Metrics
        context['total_views'] = Analytics.objects.aggregate(total=Sum('views'))['total'] or 0
        context['total_quiz_attempts'] = QuizAttempt.objects.count()
        context['total_bookmarks'] = Bookmark.objects.count()
        context['total_articles'] = News.objects.count()

        # 2. Daily views & quiz attempts (last 7 days)
        daily_stats = (
            Analytics.objects.filter(date__gte=seven_days_ago)
            .values('date')
            .annotate(views=Sum('views'), attempts=Sum('quiz_attempts'))
            .order_by('date')
        )
        
        # Build chronological arrays for Chart.js
        dates_list = []
        views_list = []
        attempts_list = []
        for i in range(7):
            d = seven_days_ago + timedelta(days=i)
            dates_list.append(d.strftime('%b %d'))
            # Find stats for this day
            day_stat = next((item for item in daily_stats if item['date'] == d), None)
            views_list.append(day_stat['views'] if day_stat else 0)
            attempts_list.append(day_stat['attempts'] if day_stat else 0)

        context['chart_dates'] = dates_list
        context['chart_views'] = views_list
        context['chart_attempts'] = attempts_list

        # 3. Category Distribution (based on article counts & views)
        category_counts = list(
            News.objects.values('category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        context['category_counts'] = category_counts

        # 4. Top 5 Most Popular Articles
        context['top_viewed_articles'] = (
            News.objects.annotate(total_views=Sum('analytics__views'))
            .filter(total_views__gt=0)
            .order_by('-total_views')[:5]
        )

        # 5. Top 5 Bookmarked Articles
        context['top_bookmarked_articles'] = (
            News.objects.annotate(total_bookmarks=Count('bookmarks'))
            .filter(total_bookmarks__gt=0)
            .order_by('-total_bookmarks')[:5]
        )

        # 6. Quiz stats
        quiz_stats = QuizAttempt.objects.aggregate(
            avg_correct=Avg('correct_answers'),
            avg_total=Avg('total_questions')
        )
        avg_correct = quiz_stats['avg_correct'] or 0
        avg_total = quiz_stats['avg_total'] or 0
        context['avg_quiz_score_pct'] = round((avg_correct / avg_total * 100), 1) if avg_total > 0 else 0

        return context
