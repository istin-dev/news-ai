import json
import logging
import feedparser
import time  # For lightweight rate-limiting pacing delays
from datetime import datetime
from time import mktime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import make_aware

# Official Groq Cloud SDK Interface
from groq import Groq
from apps.news.models import News

logger = logging.getLogger(__name__)

# Strict Category List matching your exact frontend UI Filter text choices
VALID_CATEGORIES = [
    "Polity & Governance", "Economy & Finance", "Science & Technology", 
    "International Relations", "Environment & Ecology", "Awards & Honours", 
    "Sports", "Tamil Nadu", "Others"
]

class Command(BaseCommand):
    help = 'Fetches RSS feeds, filters for exam relevance using Groq Llama 3.3, and saves to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Fetch and parse feeds without saving to DB or calling Groq API',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Limit the number of new articles to process per feed to save API quota',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']

        # Pulling unified configuration from base/development settings
        api_key = getattr(settings, 'GROQ_API_KEY', '')
        if not api_key and not dry_run:
            self.stderr.write("ERROR: GROQ_API_KEY settings is empty or not configured.")
            return

        client = None
        if not dry_run:
            client = Groq(api_key=api_key)

        feeds = getattr(settings, 'RSS_FEEDS', [])
        self.stdout.write(f"Starting feed processing. Found {len(feeds)} feeds to fetch.")

        for feed_config in feeds:
            self.process_feed(client, feed_config, dry_run, limit)

        self.stdout.write(self.style.SUCCESS("Feed processing completed successfully."))

    def process_feed(self, client, feed_config, dry_run, limit):
        name = feed_config['name']
        url = feed_config['url']
        category_hint = feed_config.get('category_hint')

        self.stdout.write(f"Fetching feed: {name} ({url})")
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            self.stderr.write(f"Failed to parse feed {name}: {e}")
            return

        new_entries = []
        for entry in feed.entries:
            link = getattr(entry, 'link', '')
            title = getattr(entry, 'title', '')

            if not link or not title:
                continue

            # Duplicate Prevention Block
            if News.objects.filter(article_url=link).exists() or News.objects.filter(title=title).exists():
                continue

            new_entries.append(entry)

        self.stdout.write(f"Found {len(new_entries)} new articles to process for {name}")

        processed_count = 0
        for entry in new_entries[:limit]:
            title = entry.title
            link = entry.link
            
            desc = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
            if hasattr(entry, 'content') and entry.content:
                desc = entry.content[0].value

            from django.utils.html import strip_tags
            desc_clean = strip_tags(desc)[:1500]

            # Parse timestamps safely
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                published_date = datetime.now()

            if published_date:
                try:
                    published_date = make_aware(published_date).date()
                except Exception:
                    published_date = published_date.date()

            if dry_run:
                self.stdout.write(f"[Dry Run] Would process: '{title}' from {name} dated {published_date}")
                continue

            self.stdout.write(f"Processing item with Groq (Llama 3.3 70B): '{title}'")
            
            # Isolated API Execution Block
            try:
                ai_data = self.process_with_groq(client, title, desc_clean, category_hint)
                
                # Active rate protection layout pacing delay
                self.stdout.write("Pacing pipeline... Cooling down for 2 seconds.")
                time.sleep(2)
            except Exception as api_err:
                self.stderr.write(f"Groq API processing dropped on '{title}': {api_err}")
                continue
            
            if not ai_data:
                self.stderr.write(f"Failed to process '{title}' with Groq. Skipping.")
                continue

            # CRITICAL FILTER CHECK: Drop non-relevant items early to keep dashboard clean
            if not ai_data.get('is_relevant', True):
                self.stdout.write(self.style.WARNING(f"⏩ Skipped (Not Exam Relevant): '{title}'"))
                continue

            try:
                # Direct database schema validation map
                News.objects.create(
                    title=title,
                    source=name,
                    article_url=link,
                    published_date=published_date,
                    category=ai_data.get('category', category_hint or 'Others'),
                    summary=ai_data.get('summary', ''),
                    keywords=ai_data.get('keywords', []),
                    mcq_question=ai_data.get('mcq_question', ''),
                    mcq_options=ai_data.get('mcq_options', {}),
                    mcq_answer=ai_data.get('mcq_answer', ''),
                    mcq_explanation=ai_data.get('mcq_explanation', ''),
                    highlighted_entities=ai_data.get('highlighted_entities', {}),
                    revision_notes=ai_data.get('revision_notes', ''),
                    is_published=True
                )
                processed_count += 1
                self.stdout.write(self.style.SUCCESS(f"Saved: '{title}'"))
            except Exception as e:
                self.stderr.write(f"Error saving article to DB: {e}")

        self.stdout.write(f"Processed and saved {processed_count} articles for {name}")

    def process_with_groq(self, client, title, description, category_hint=None):
        """Calls Groq using Llama 3.3 70B with highly refined TNPSC syllabus filtering constraints."""
        
        system_instruction = f"""
        You are a chief curriculum auditor for the TNPSC Group 2 (Tamil Nadu Public Service Commission) and UPSC civil services exams.
        Your task is to strictly evaluate if a news article title and description hold authentic academic value for an aspirant's syllabus.

        Strictly apply these core evaluation filters:

        1. Syllabus Alignment (is_relevant = true):
           - Indian Polity & Governance (Acts, Constitution, Judiciary, Panchayats, Citizen-centric schemes).
           - Economy & Finance (Union/State Budgets, Taxation, ITR rules, Banking, Inflation, Infrastructure like Jewar Airport, National Highways).
           - Science & Technology (Space missions like MAVEN, ISRO, defense updates, NCERT updates, AI ecosystem policies, core public health/diseases).
           - History, Culture & Geography (Indus Valley Civilization, Birsa Munda, UNESCO heritage sites, major climate alerts/IMD forecasts).
           - International Relations (Bilateral pacts, major geopolitical wars affecting global security or treaties).
           - Tamil Nadu Specifics (State governance, culture, development, achievements, local history).

        2. Non-Syllabus Fluff (is_relevant = false):
           - Lifestyle & Trivia: Wealth updates, personal living habits, or real estate choices of billionaires (e.g., Elon Musk renting a house, SpaceX valuation trivia).
           - Corporate Tech Gossip: Disney/Apple/Tesla internal management choices, software tool usage guidelines (e.g., Disney minimizing Claude/Cursor), or individual consumer complaints (e.g., fake watch deliveries).
           - Yellow Journalism & Localized Incidents: Minor scams, domestic neighborhood fights, celebrity drama, or entertainment media layoffs.
           - Basic Quotes: Generic "Quote of the day" articles without academic context.

        CRITICAL QUESTION QUALITY RULES:
        - The "mcq_question" MUST target core factual or conceptual points of the academic topic. Never quiz on the article text itself.
        - "category" MUST match exactly one item in this list: {VALID_CATEGORIES}. If it doesn't align cleanly, default to 'Others'.
        - "summary" must be exactly a 2-line high-yield statement.

        Output a completely clean, valid JSON object matching this schema precisely:
        {{
            "is_relevant": true_or_false,
            "summary": "string",
            "category": "string",
            "keywords": ["string"],
            "highlighted_entities": {{
                "schemes": ["string"],
                "organizations": ["string"],
                "places": ["string"],
                "persons": ["string"],
                "numbers": ["string"]
            }},
            "mcq_question": "string",
            "mcq_options": {{"A": "string", "B": "string", "C": "string", "D": "string"}},
            "mcq_answer": "A, B, C, or D",
            "mcq_explanation": "string",
            "revision_notes": "string"
        }}
        """

        user_content = f"Title: {title}\nDescription: {description}\nCategory Hint: {category_hint or 'None'}"

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.0,  # Zero temperature locks down maximum deterministic adherence to instructions
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"Groq processing breakdown: {e}")
            return None