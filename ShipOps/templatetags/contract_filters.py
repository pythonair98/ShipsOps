from django import template
from ShipOps.models import Contract

register = template.Library()

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