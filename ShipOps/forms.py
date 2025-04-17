from django import forms
from .models import Contact, Contract, Invoice


class ContractForm(forms.ModelForm):
    """
    Form for creating or updating a Contract.
    
    This form maps to the Contract model and includes all relevant fields
    for contract creation and management.
    """

    class Meta:
        model = Contract
        fields = [
            'charter_party_dated', 'charterer', 'owner', 'charter_party_form', 'vessel',
            'charter_party_speed', 'last_three_cargoes', 'cargo', 'quantity', 'heating',
            'load_port', 'laycan', 'discharge_port', 'freight', 'demurrage', 'laytime',
            'payment_terms', 'payment_to', 'brokers', 'commission', 'state',
            'contract_start', 'contract_end'
        ]
        # Auto-managed fields like 'created_at' and 'updated_at' are excluded


class InvoiceForm(forms.ModelForm):
    """
    Form for creating or updating an Invoice.
    
    This form maps to the Invoice model and includes fields for price information
    in multiple currencies and the associated contract.
    """

    class Meta:
        model = Invoice
        fields = [
            'price_usd', 
            'price_usd_in_word', 
            'aed_price', 
            'aed_price_in_word', 
            'contract'
        ]
        # 'created_at' is auto-generated and excluded
