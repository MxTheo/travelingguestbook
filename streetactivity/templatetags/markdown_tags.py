import markdown
from django import template

register = template.Library()

@register.filter
def markdown_to_html(value):
    """Converts Markdown text to HTML using the markdown library with the 'nl2br' extension."""
    return markdown.markdown(value, extensions=['nl2br'])
