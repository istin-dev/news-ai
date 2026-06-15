from django.urls import path
from .views import WeeklyReportHTMLView, download_weekly_pdf

app_name = 'pdf_export'

urlpatterns = [
    path('weekly/', WeeklyReportHTMLView.as_view(), name='weekly_html'),
    path('weekly/download/', download_weekly_pdf, name='weekly_download'),
]
