from django import template

register = template.Library()

@register.filter
def percentage(value, total):
    """
    Calculate the percentage of a value relative to a total.
    Returns 0 if total is 0 to avoid division by zero.
    """
    try:
        return int((float(value) / float(total)) * 100) if total else 0
    except (ValueError, ZeroDivisionError):
        return 0 