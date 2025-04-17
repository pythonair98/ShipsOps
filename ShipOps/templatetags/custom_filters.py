from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary or list by index/key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    elif isinstance(dictionary, (list, tuple)) and isinstance(key, int):
        try:
            return dictionary[key]
        except IndexError:
            return None
    return None 