import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now

from apps.pdf_export.utils import get_weekly_articles

class Command(BaseCommand):
    help = 'Pre-generates weekly current affairs PDF and saves it to media storage'

    def handle(self, *args, **options):
        articles = get_weekly_articles()
        report_date = now().date().strftime('%d-%b-%Y')
        
        self.stdout.write(f"Generating weekly report for date: {report_date}")
        self.stdout.write(f"Found {articles.count()} articles to compile.")

        if not articles.exists():
            self.stdout.write(self.style.WARNING("No articles found for the weekly range. Skipping PDF compilation."))
            return

        html_string = render_to_string('pdf_export/weekly_report.html', {
            'news_list': articles,
            'report_date': report_date,
            'is_pdf': True
        })

        # Ensure directory exists in media root
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'weekly_reports')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f"TNPSC_Weekly_Affairs_{report_date}.pdf")

        try:
            from weasyprint import HTML
            self.stdout.write("Compiling PDF with WeasyPrint...")
            HTML(string=html_string).write_pdf(pdf_path)
            self.stdout.write(self.style.SUCCESS(f"Successfully compiled weekly PDF to: {pdf_path}"))
        except Exception as e:
            self.stderr.write(f"Failed to compile PDF: {e}")
            self.stdout.write("Falling back: Saving raw HTML version for backup...")
            html_backup_path = pdf_path.replace('.pdf', '.html')
            with open(html_backup_path, 'w', encoding='utf-8') as f:
                f.write(html_string)
            self.stdout.write(self.style.SUCCESS(f"Saved HTML print backup to: {html_backup_path}"))
