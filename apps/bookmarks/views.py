from django.views.generic import ListView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from apps.news.models import News
from .models import Bookmark

class BookmarksListView(ListView):
    model = Bookmark
    template_name = 'bookmarks/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 12

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Bookmark.objects.filter(user=self.request.user).select_related('news')
        else:
            session_key = self.request.session.session_key
            if not session_key:
                return Bookmark.objects.none()
            return Bookmark.objects.filter(session_key=session_key).select_related('news')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Store simple array of bookmarked IDs for template logic
        bookmarked_ids = []
        for b in context['bookmarks']:
            bookmarked_ids.append(b.news.id)
        context['bookmarked_ids'] = bookmarked_ids
        return context

def toggle_bookmark(request, news_id):
    """AJAX endpoint to add/remove article bookmark."""
    if request.method == 'POST':
        news = get_object_or_404(News, id=news_id)
        user = request.user if request.user.is_authenticated else None
        
        # Ensure session exists for anonymous users
        if not user and not request.session.session_key:
            request.session.create()
        session_key = None if user else request.session.session_key

        # Check if bookmark already exists
        if user:
            bookmark_filter = Bookmark.objects.filter(user=user, news=news)
        else:
            bookmark_filter = Bookmark.objects.filter(session_key=session_key, news=news)

        if bookmark_filter.exists():
            bookmark_filter.delete()
            is_bookmarked = False
        else:
            Bookmark.objects.create(user=user, session_key=session_key, news=news)
            is_bookmarked = True

        # Keep session-based cache list in sync for fast home page loads
        session_bookmarks = request.session.get('bookmarked_news_ids', [])
        if is_bookmarked:
            if news_id not in session_bookmarks:
                session_bookmarks.append(news_id)
        else:
            if news_id in session_bookmarks:
                session_bookmarks.remove(news_id)
        request.session['bookmarked_news_ids'] = session_bookmarks

        return JsonResponse({
            'status': 'success',
            'is_bookmarked': is_bookmarked,
            'message': 'Bookmark toggled'
        })
    return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
