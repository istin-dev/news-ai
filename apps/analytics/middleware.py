from django.utils.timezone import now
from apps.news.models import News
from apps.analytics.models import Analytics

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only increment views on successful GET request
        if request.method == 'GET' and response.status_code == 200:
            match = request.resolver_match
            if match and match.namespace == 'news' and match.url_name == 'detail':
                slug = match.kwargs.get('slug')
                if slug:
                    try:
                        news = News.objects.get(slug=slug)
                        analytics, created = Analytics.objects.get_or_create(
                            news=news,
                            date=now().date(),
                            defaults={'views': 1, 'quiz_attempts': 0}
                        )
                        if not created:
                            analytics.views += 1
                            analytics.save()
                    except News.DoesNotExist:
                        pass
        
        return response
