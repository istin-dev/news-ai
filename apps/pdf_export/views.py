import logging
from django.views.generic import ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.timezone import now

from .utils import get_weekly_articles

logger = logging.getLogger(__name__)

class WeeklyReportHTMLView(ListView):
    """HTML print view for weekly current affairs. Renders a clean print layout."""
    template_name = 'pdf_export/weekly_report.html'
    context_object_name = 'news_list'

    def get_queryset(self):
        return get_weekly_articles()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_date'] = now().date().strftime('%d-%b-%Y')
        return context

def download_weekly_pdf(request):
    """
    Attempts to compile and download the weekly report as PDF via WeasyPrint.
    If OS dependencies for WeasyPrint are missing, it falls back to the HTML Print page.
    """
    articles = get_weekly_articles()
    report_date = now().date().strftime('%d-%b-%Y')
    
    html_string = render_to_string('pdf_export/weekly_report.html', {
        'news_list': articles,
        'report_date': report_date,
        'is_pdf': True
    })

    try:
        from weasyprint import HTML
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TNPSC_Weekly_Affairs_{report_date}.pdf"'
        
        # Compile HTML string to PDF
        HTML(string=html_string).write_pdf(response)
        return response
    except Exception as e:
        # Fallback to HTML Print page with user message
        logger.warning(f"WeasyPrint PDF generation failed: {e}. Falling back to browser print view.")
        messages.warning(
            request, 
            "Local PDF compiler is not available on this server. "
            "Please use your browser's 'Print -> Save as PDF' option from the layout page below."
        )
        return HttpResponseRedirect(reverse('pdf_export:weekly_html'))
