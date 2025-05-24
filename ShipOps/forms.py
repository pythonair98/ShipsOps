from django import forms
from .models import Contact, Contract, Invoice


class ContractForm(forms.ModelForm):
    """
    Form for creating or updating a Contract.
    
    This form maps to the Contract model and includes all relevant fields
    for contract creation and management.
    """

    # Define choices for the status field
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed')
    ]
    
    # Define choices for risk level field
    RISK_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    
    # Define choices for state field
    STATE_CHOICES = [
        (0, 'Pending'),
        (1, 'Finance'),
        (2, 'Billed'),
        (3, 'Completed')
    ]
    
    # Define choices for contract type field
    CONTRACT_TYPE_CHOICES = [
        ('voyage_charter', 'Voyage Charter'),
        ('time_charter', 'Time Charter'),
        ('bareboat_charter', 'Bareboat Charter'),
        ('contract_of_affreightment', 'Contract of Affreightment (COA)'),
        ('consecutive_voyage_charter', 'Consecutive Voyage Charter'),
        ('contract_carriage', 'Contract of Carriage'),
        ('tanker_charter', 'Tanker Charter'),
        ('bulk_carrier_charter', 'Bulk Carrier Charter'),
        ('container_charter', 'Container Vessel Charter'),
        ('ship_management', 'Ship Management Contract'),
        ('crew_management', 'Crew Management Contract'),
        ('ship_sale', 'Ship Sale Contract'),
        ('ship_purchase', 'Ship Purchase Contract'),
        ('ship_repair', 'Ship Repair Contract'),
        ('ship_building', 'Ship Building Contract'),
        ('other', 'Other')
    ]
    
    # Define choices for category field
    CATEGORY_CHOICES = [
        ('charter', 'Charter Agreement'),
        ('transport', 'Transport/Carriage'),
        ('management', 'Management Contract'),
        ('maintenance', 'Maintenance Contract'),
        ('purchase', 'Purchase Agreement'),
        ('sale', 'Sale Agreement'),
        ('repair', 'Repair Contract'),
        ('construction', 'Construction Contract'),
        ('leasing', 'Leasing Agreement'),
        ('insurance', 'Insurance Contract'),
        ('crew', 'Crew Management'),
        ('consulting', 'Consulting Services'),
        ('technical', 'Technical Services'),
        ('legal', 'Legal Services'),
        ('other', 'Other')
    ]
    
    # Define choices for tags field
    TAG_CHOICES = [
        ('urgent', 'Urgent'),
        ('priority', 'Priority'),
        ('long_term', 'Long-term'),
        ('short_term', 'Short-term'),
        ('tanker', 'Tanker'),
        ('bulk_carrier', 'Bulk Carrier'),
        ('container', 'Container'),
        ('passenger', 'Passenger'),
        ('lng', 'LNG'),
        ('lpg', 'LPG'),
        ('dry_bulk', 'Dry Bulk'),
        ('crude_oil', 'Crude Oil'),
        ('chemical', 'Chemical'),
        ('product', 'Product'),
        ('multi_purpose', 'Multi-purpose'),
        ('high_value', 'High Value'),
        ('sensitive', 'Sensitive'),
        ('strategic', 'Strategic'),
        ('seasonal', 'Seasonal'),
        ('new_client', 'New Client'),
        ('recurring_client', 'Recurring Client'),
        ('special_terms', 'Special Terms'),
        ('standard_terms', 'Standard Terms'),
        ('negotiation', 'Under Negotiation'),
        ('review_needed', 'Review Needed')
    ]
    
    # Override the status field to use our choices
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Override the risk_level field to use our choices
    risk_level = forms.ChoiceField(
        choices=RISK_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Override the state field to use our choices
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Override the contract_type field to use our choices
    contract_type = forms.ChoiceField(
        choices=CONTRACT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Override the category field to use our choices
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Override the tags field to use our choices (multiple selection)
    tags = forms.MultipleChoiceField(
        choices=TAG_CHOICES,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'})
    )

    class Meta:
        model = Contract
        fields = [
            'charter_party_dated', 'charterer', 'owner', 'charter_party_form', 'vessel',
            'charter_party_speed', 'last_three_cargoes', 'cargo', 'quantity', 'heating',
            'load_port', 'laycan', 'discharge_port', 'freight', 'demurrage', 'laytime',
            'payment_terms', 'payment_to', 'brokers', 'commission', 'state',
            'contract_start', 'contract_end', 'status', 'contract_number', 'contract_type',
            'category', 'risk_level', 'next_review_date', 'reminder_days', 'tags'
        ]
        # Auto-managed fields like 'created_at' and 'updated_at' are excluded
        widgets = {
            # Basic fields with form-control class
            'charter_party_dated': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'charterer': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.TextInput(attrs={'class': 'form-control'}),
            'charter_party_form': forms.TextInput(attrs={'class': 'form-control'}),
            'vessel': forms.TextInput(attrs={'class': 'form-control'}),
            'charter_party_speed': forms.TextInput(attrs={'class': 'form-control'}),
            'last_three_cargoes': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control'}),
            'heating': forms.TextInput(attrs={'class': 'form-control'}),
            'load_port': forms.TextInput(attrs={'class': 'form-control'}),
            'laycan': forms.TextInput(attrs={'class': 'form-control'}),
            'discharge_port': forms.TextInput(attrs={'class': 'form-control'}),
            'freight': forms.TextInput(attrs={'class': 'form-control'}),
            'demurrage': forms.TextInput(attrs={'class': 'form-control'}),
            'laytime': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_to': forms.TextInput(attrs={'class': 'form-control'}),
            'brokers': forms.TextInput(attrs={'class': 'form-control'}),
            'commission': forms.TextInput(attrs={'class': 'form-control'}),
            'contract_start': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'contract_end': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            
            # New fields
            'next_review_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'contract_number': forms.TextInput(attrs={'class': 'form-control'}),
            'reminder_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '90'})
        }


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
