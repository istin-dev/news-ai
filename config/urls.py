from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.news.urls', namespace='news')),
    path('quiz/', include('apps.quiz.urls', namespace='quiz')),
    path('bookmarks/', include('apps.bookmarks.urls', namespace='bookmarks')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
    path('pdf/', include('apps.pdf_export.urls', namespace='pdf_export')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
