from django.db import models
from django.utils.text import slugify
from django.conf import settings

class News(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    source = models.CharField(max_length=100)
    article_url = models.URLField(max_length=1000, unique=True)
    published_date = models.DateField()
    category = models.CharField(
        max_length=50, 
        choices=settings.NEWS_CATEGORIES,
        default='Others'
    )
    summary = models.TextField(help_text="2-line TNPSC focused summary")
    keywords = models.JSONField(default=list, blank=True)
    
    # MCQ Fields
    mcq_question = models.TextField(blank=True, null=True)
    mcq_options = models.JSONField(default=dict, blank=True, help_text="Dictionary like {'A': '...', 'B': '...'}")
    mcq_answer = models.CharField(max_length=10, blank=True, null=True, help_text="Correct option key, e.g., 'A', 'B', 'C', 'D'")
    mcq_explanation = models.TextField(blank=True, null=True)
    
    # AI Extracted Entities
    # Expected format: {"schemes": [], "organizations": [], "places": [], "persons": [], "numbers": []}
    highlighted_entities = models.JSONField(default=dict, blank=True)
    revision_notes = models.TextField(blank=True, null=True, help_text="Bullet points for quick revision")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "News Articles"
        ordering = ['-published_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from title
            base_slug = slugify(self.title)
            # Ensure unique slug
            unique_slug = base_slug[:480]
            counter = 1
            while News.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug[:470]}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
