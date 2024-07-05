# appsimulation/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def intspace(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value
