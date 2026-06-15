import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight_entities(text, entities):
    """
    Highlights entities inside the text by wrapping them with Bootstrap badges.
    entities is expected to be a dict:
    {"schemes": [...], "organizations": [...], "places": [...], "persons": [...], "numbers": [...]}
    """
    if not text or not entities:
        return text

    # Define color class mappings
    classes = {
        'schemes': 'bg-warning text-dark entity-scheme',            # Yellow
        'organizations': 'bg-primary text-white entity-org',       # Blue
        'places': 'bg-success text-white entity-place',            # Green
        'persons': 'bg-purple text-white entity-person',           # Purple (handled in CSS)
        'numbers': 'bg-danger text-white entity-number',           # Red
    }

    # Gather all phrases to replace, sorted by length descending (to avoid partial matches first)
    replacements = []
    for key, items in entities.items():
        if not items or key not in classes:
            continue
        badge_class = classes[key]
        for item in items:
            if item and len(item.strip()) > 1:
                replacements.append((item.strip(), badge_class))

    # Sort replacements by length descending
    replacements.sort(key=lambda x: len(x[0]), reverse=True)

    # Perform replacement
    # We use a pattern matching approach to avoid replacing within already replaced HTML tags
    # A simple way is to tokenize the text by HTML tags and only replace in text blocks
    # Since the input summary starts as plain text, we can just do regex replacement.
    # To prevent duplicate replacement of the same word or subwords, we can do it in one pass using a combined regex.
    if not replacements:
        return text

    # Escape each term for regex
    escaped_terms = []
    term_to_class = {}
    for term, cls in replacements:
        escaped = re.escape(term)
        escaped_terms.append(escaped)
        term_to_class[term.lower()] = cls

    # Build pattern: match full words/phrases
    # We want case insensitive matching
    pattern_str = '|'.join(escaped_terms)
    # Use word boundaries if possible, but some schemes/numbers might not end with word boundaries (e.g. symbols)
    # We will use simple case-insensitive matching with boundary awareness
    pattern = re.compile(rf'\b({pattern_str})\b', re.IGNORECASE)

    def replace_match(match):
        matched_text = match.group(0)
        cls = term_to_class.get(matched_text.lower())
        if not cls:
            # Try to find matching key case-insensitively
            for k, v in term_to_class.items():
                if k in matched_text.lower() or matched_text.lower() in k:
                    cls = v
                    break
        cls = cls or 'bg-secondary text-white'
        return f'<span class="badge {cls} mx-1">{matched_text}</span>'

    highlighted_text = pattern.sub(replace_match, text)
    return mark_safe(highlighted_text)

@register.filter
def get_entity_list(entities, key):
    """Safely extracts a list of entities by key from the entity dictionary."""
    if not entities or not isinstance(entities, dict):
        return []
    return entities.get(key, [])
