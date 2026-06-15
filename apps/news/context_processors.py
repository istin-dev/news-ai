from django.conf import settings

def categories_processor(request):
    return {
        'NEWS_CATEGORIES': settings.NEWS_CATEGORIES
    }
