from django import template
from django.template.defaultfilters import stringfilter
from ShipOps.models import Contract, Invoice

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

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces in a string."""
    return value.replace('_', ' ') if value else ''

@register.filter
def startswith(value, arg):
    """Check if the value starts with the argument."""
    return value.startswith(arg) if value else False

@register.filter
def endswith(value, arg):
    """Check if the value ends with the argument."""
    return value.endswith(arg) if value else False

@register.filter
def contains(value, arg):
    """Check if the value contains the argument."""
    return arg in value if value else False

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0 

@register.filter
def filter_contracts_without_invoice(contracts):
    """
    Filter a list of contracts to return only those without invoices.
    
    Args:
        contracts: A queryset or list of Contract objects
        
    Returns:
        A list of Contract objects that don't have associated invoices
    """
    return [contract for contract in contracts if not hasattr(contract, 'invoice_obj')]

@register.filter
def filter_invoices_by_status(invoices, status):
    """
    Filter a list of invoices by their status.
    Usage: {{ invoices|filter_invoices_by_status:"paid" }}
    """
    if not invoices:
        return []
    
    if status == 'all':
        return invoices
    
    return [invoice for invoice in invoices if invoice.status == status] 