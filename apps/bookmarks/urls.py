from django.urls import path
from .views import BookmarksListView, toggle_bookmark

app_name = 'bookmarks'

urlpatterns = [
    path('', BookmarksListView.as_view(), name='list'),
    path('toggle/<int:news_id>/', toggle_bookmark, name='toggle'),
]
