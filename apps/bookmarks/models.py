from django.db import models
from django.conf import settings
from apps.news.models import News

class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['user', 'news'], ['session_key', 'news']]
        ordering = ['-created_at']

    def __str__(self):
        owner = self.user.username if self.user else f"Session {self.session_key[:8]}"
        return f"{owner} bookmarked {self.news.title[:30]}"
