from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NewsListView, NewsDetailView, CategoryNewsListView,
    SearchNewsListView, APINewsViewSet
)

app_name = 'news'

router = DefaultRouter()
router.register(r'articles', APINewsViewSet, basename='api-news')

urlpatterns = [
    path('', NewsListView.as_view(), name='index'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='detail'),
    path('category/<str:category_name>/', CategoryNewsListView.as_view(), name='category'),
    path('search/', SearchNewsListView.as_view(), name='search'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
