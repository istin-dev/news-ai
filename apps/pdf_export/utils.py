from django.utils.timezone import now
from datetime import timedelta
from apps.news.models import News

def get_weekly_articles():
    """Fetches articles from the last 7 days."""
    today = now().date()
    seven_days_ago = today - timedelta(days=7)
    return News.objects.filter(
        published_date__gte=seven_days_ago,
        is_published=True
    ).order_by('-published_date', '-created_at')
