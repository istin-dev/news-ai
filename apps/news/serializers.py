from rest_framework import serializers
from .models import News

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'source', 'article_url', 'published_date',
            'category', 'summary', 'keywords', 'mcq_question', 'mcq_options',
            'mcq_answer', 'mcq_explanation', 'highlighted_entities',
            'revision_notes', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']
