from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source', 'published_date', 'is_published', 'created_at')
    list_filter = ('category', 'source', 'published_date', 'is_published')
    search_fields = ('title', 'summary', 'keywords', 'mcq_question')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Article Metadata', {
            'fields': ('title', 'slug', 'source', 'article_url', 'published_date', 'category', 'is_published')
        }),
        ('AI Analysis', {
            'fields': ('summary', 'keywords', 'highlighted_entities', 'revision_notes')
        }),
        ('MCQ Section', {
            'fields': ('mcq_question', 'mcq_options', 'mcq_answer', 'mcq_explanation')
        }),
        ('System Fields', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    actions = ['make_published', 'make_unpublished']

    def make_published(self, request, queryset):
        queryset.update(is_published=True)
    make_published.short_description = "Mark selected news as published"

    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
    make_unpublished.short_description = "Mark selected news as unpublished"
