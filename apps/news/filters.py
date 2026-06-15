import django_filters
from .models import News

class NewsFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(choices=[])
    source = django_filters.CharFilter(lookup_expr='icontains')
    start_date = django_filters.DateFilter(field_name='published_date', lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name='published_date', lookup_expr='lte')

    class Meta:
        model = News
        fields = ['category', 'source', 'published_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamic import to prevent circular dependency
        from django.conf import settings
        self.filters['category'].extra['choices'] = settings.NEWS_CATEGORIES
