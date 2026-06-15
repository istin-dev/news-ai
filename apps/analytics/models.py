from django.db import models
from apps.news.models import News

class Analytics(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='analytics')
    views = models.IntegerField(default=0)
    quiz_attempts = models.IntegerField(default=0)
    date = models.DateField()

    class Meta:
        unique_together = ('news', 'date')
        verbose_name_plural = "Analytics Data"

    def __str__(self):
        return f"Analytics for {self.news.title[:20]} on {self.date}"
