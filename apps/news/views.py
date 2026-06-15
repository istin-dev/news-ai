from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import News
from .serializers import NewsSerializer
from .filters import NewsFilter

class NewsListView(ListView):
    model = News
    template_name = 'news/index.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        return News.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add bookmarked ids from session to avoid DB lookup for each item
        context['bookmarked_ids'] = self.request.session.get('bookmarked_news_ids', [])
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/detail.html'
    context_object_name = 'news'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mark whether current article is bookmarked
        bookmarked_ids = self.request.session.get('bookmarked_news_ids', [])
        context['is_bookmarked'] = self.object.id in bookmarked_ids
        
        # Get related news (same category, excluding current)
        context['related_news'] = News.objects.filter(
            category=self.object.category, 
            is_published=True
        ).exclude(id=self.object.id)[:4]
        return context


class CategoryNewsListView(ListView):
    model = News
    template_name = 'news/category.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        # 1. Grab the raw category parameter out of your URL route path
        self.category_slug = self.kwargs.get('category_name', '').strip()

        # 2. Comprehensive mapping dictionary translating short template loop strings 
        # and clean slug parameters to their exact database counterpart formats.
        category_db_mapper = {
            # Short keys from template loop values
            'polity': 'Polity & Governance',
            'economy': 'Economy & Finance',
            'science': 'Science & Technology',
            'international': 'International Relations',
            'environment': 'Environment & Ecology',
            'awards': 'Awards & Honours',
            
            # Full hyphenated URL slugs
            'polity-governance': 'Polity & Governance',
            'economy-finance': 'Economy & Finance',
            'science-technology': 'Science & Technology',
            'international-relations': 'International Relations',
            'environment-ecology': 'Environment & Ecology',
            'awards-honours': 'Awards & Honours',
            
            # Unified keys
            'sports': 'Sports',
            'tamil nadu': 'Tamil Nadu',
            'tamil-nadu': 'Tamil Nadu',
            'others': 'Others'
        }

        # Convert to lowercase to perform a safe lookup. Fallback to title-case string if unmapped.
        self.target_category = category_db_mapper.get(
            self.category_slug.lower(), 
            self.category_slug.replace('-', ' ').title()
        )
        
        # 3. Query the database using a strict case-insensitive OR check for complete safety
        return News.objects.filter(
            Q(category__iexact=self.target_category) | Q(category__iexact=self.category_slug),
            is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Keep the raw slug so template condition tags track the active pill class accurately
        context['category_name'] = self.category_slug 
        
        # This correctly displays the full name like "Polity & Governance" in your <h1> template headings!
        context['category_display'] = self.target_category
        context['bookmarked_ids'] = self.request.session.get('bookmarked_news_ids', [])
        return context


class SearchNewsListView(ListView):
    model = News
    template_name = 'news/search.html'
    context_object_name = 'news_list'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return News.objects.filter(
                Q(title__icontains=query) |
                Q(summary__icontains=query) |
                Q(keywords__icontains=query) |
                Q(source__icontains=query),
                is_published=True
            )
        return News.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['bookmarked_ids'] = self.request.session.get('bookmarked_news_ids', [])
        return context


# DRF API ViewSet
class APINewsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class APINewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
    pagination_class = APINewsPagination
    filterset_class = NewsFilter
    lookup_field = 'slug'