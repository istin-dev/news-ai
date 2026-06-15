"""
Django base settings for tnpsc_affairs project.
"""
import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'widget_tweaks',
]

LOCAL_APPS = [
    'apps.news',
    'apps.quiz',
    'apps.bookmarks',
    'apps.analytics',
    'apps.pdf_export',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.analytics.middleware.PageViewMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.news.context_processors.categories_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Gemini API
GEMINI_API_KEY = config('GEMINI_API_KEY', default='')
GROQ_API_KEY = config('GROQ_API_KEY', '')

# RSS Feed Sources
RSS_FEEDS = [
    {
        'name': 'PIB India',
        'url': 'https://www.pib.gov.in/ViewRss.aspx?lang=1&reg=1',
        'category_hint': 'Polity',
    },
    {
        'name': 'Indian Express UPSC',
        'url': 'https://indianexpress.com/section/upsc-current-affairs/feed/',
        'category_hint': None,
    },
    {
        'name': 'Times of India',
        'url': 'https://timesofindia.indiatimes.com/rssfeedstopstories.cms',
        'category_hint': None,
    },
    {
        'name': 'NDTV',
        'url': 'https://feeds.feedburner.com/ndtvnews-top-stories',
        'category_hint': None,
    },
    {
        'name': 'LiveMint',
        'url': 'https://www.livemint.com/rss/news',
        'category_hint': 'Economy',
    },
    {
        'name': 'The Wire',
        'url': 'https://thewire.in/rss',
        'category_hint': None,
    },
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}

# Pagination
NEWS_PER_PAGE = 12

# Categories
NEWS_CATEGORIES = [
    ('Polity', 'Polity & Governance'),
    ('Economy', 'Economy & Finance'),
    ('Science', 'Science & Technology'),
    ('International', 'International Relations'),
    ('Environment', 'Environment & Ecology'),
    ('Awards', 'Awards & Honours'),
    ('Sports', 'Sports'),
    ('Tamil Nadu', 'Tamil Nadu'),
    ('Others', 'Others'),
]
