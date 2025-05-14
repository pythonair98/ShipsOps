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
    price_usd = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    aed_price = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'})
    )
    
    price_usd_in_word = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    
    aed_price_in_word = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = Invoice
        fields = [
            'contract',
            'price_usd',
            'price_usd_in_word',
            'aed_price',
            'aed_price_in_word',
            'status',
            'due_date',
            'notes'
        ]
        widgets = {
            'contract': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }
