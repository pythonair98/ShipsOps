from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# =============================================================================
# Contact Model
# =============================================================================
class Contact(models.Model):
    """
    Stores contact information for a user.

    Fields:
        ar_name: Full Arabic name.
        en_name: Full English name.
        ar_fname: Arabic first name.
        ar_lname: Arabic last name.
        en_fname: English first name.
        en_lname: English last name.
        phone_number: Contact phone number.
        email: Contact email address.
        created_at: Timestamp for when the contact was created.
    """
    ar_name = models.CharField(max_length=200)
    en_name = models.CharField(max_length=200, null=True, blank=True)
    ar_fname = models.CharField(max_length=100, null=True, blank=True)
    ar_lname = models.CharField(max_length=100, null=True, blank=True)
    en_fname = models.CharField(max_length=100, null=True, blank=True)
    en_lname = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def ar_full_name(self):
        """
        Constructs and returns the full Arabic name.
        """
        return f"{self.ar_fname or ''} {self.ar_lname or ''}".strip()

    def __str__(self):
        return self.ar_name


# =============================================================================
# Contract Model
# =============================================================================
class Contract(models.Model):
    """
    Represents a ship reservation contract.

    Fields:
        charter_party_dated: Date when the charter party was dated.
        charterer: Name of the charterer.
        owner: Name of the vessel owner.
        charter_party_form: Form/type of the charter party.
        vessel: Vessel name.
        charter_party_speed: Speed details of the charter party.
        last_three_cargoes: Information about the last three cargoes.
        cargo: Description of the cargo.
        quantity: Cargo quantity details.
        heating: Heating information if applicable.
        load_port: Loading port details.
        laycan: Laycan details.
        discharge_port: Discharge port details.
        freight: Freight details.
        demurrage: Demurrage details.
        laytime: Laytime details.
        payment_terms: Payment terms.
        payment_to: Payment recipient details.
        brokers: Brokers involved.
        commission: Commission details.
        state: Current state/status of the contract (e.g., CONTRACT, TO_FIN, BILLED).
        contract_start: Start date of the contract.
        contract_end: End date of the contract.
        created_at: Timestamp for when the contract was created.
        updated_at: Timestamp for the last update.
    """
    charter_party_dated = models.DateTimeField(default=timezone.now)
    charterer = models.CharField(max_length=150, null=True, blank=True)
    owner = models.CharField(max_length=150, null=True, blank=True)
    charter_party_form = models.CharField(max_length=150, null=True, blank=True)
    vessel = models.CharField(max_length=150, null=True, blank=True)
    charter_party_speed = models.CharField(max_length=150, null=True, blank=True)
    last_three_cargoes = models.CharField(max_length=150, null=True, blank=True)
    cargo = models.CharField(max_length=150, null=True, blank=True)
    quantity = models.CharField(max_length=150, null=True, blank=True)
    heating = models.CharField(max_length=150, null=True, blank=True)
    load_port = models.CharField(max_length=150, null=True, blank=True)
    laycan = models.CharField(max_length=150, null=True, blank=True)
    discharge_port = models.CharField(max_length=150, null=True, blank=True)
    freight = models.CharField(max_length=150, null=True, blank=True)
    demurrage = models.CharField(max_length=150, null=True, blank=True)
    laytime = models.CharField(max_length=150, null=True, blank=True)
    payment_terms = models.CharField(max_length=150, null=True, blank=True)
    payment_to = models.CharField(max_length=150, null=True, blank=True)
    brokers = models.CharField(max_length=150, null=True, blank=True)
    commission = models.CharField(max_length=150, null=True, blank=True)
    state = models.IntegerField(default=0, null=True, blank=True)
    contract_start = models.DateTimeField(default=timezone.now, null=True, blank=True)
    contract_end = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def invoice(self):
        """
        Returns the invoice associated with this contract, if one exists.
        """
        return getattr(self, 'invoice_obj', None)
    
    @property
    def invoices(self):
        """
        Returns all invoices associated with this contract.
        """
        return Invoice.objects.filter(contract=self).all()

    @property
    def contract_value(self):
        """
        Calculates and returns the contract value in USD.
        
        Returns:
            float: The contract value in USD if an invoice exists, otherwise 0.0
        """
        if self.invoice and self.invoice.price_usd is not None:
            return float(self.invoice.price_usd)
        return 0.0

    @property
    def contract_value_aed(self):
        """
        Calculates and returns the contract value in AED.
        
        Returns:
            float: The contract value in AED if an invoice exists, otherwise 0.0
        """
        if self.invoice and self.invoice.aed_price is not None:
            return float(self.invoice.aed_price)
        return 0.0

    @property
    def contract_value_in_words(self):
        """
        Returns the contract value in words (USD).
        
        Returns:
            str: The contract value in words if an invoice exists, otherwise empty string
        """
        if self.invoice and self.invoice.price_usd_in_word:
            return self.invoice.price_usd_in_word
        return ""

    @property
    def contract_value_aed_in_words(self):
        """
        Returns the contract value in words (AED).
        
        Returns:
            str: The contract value in AED words if an invoice exists, otherwise empty string
        """
        if self.invoice and self.invoice.aed_price_in_word:
            return self.invoice.aed_price_in_word
        return ""

    def __str__(self):
        return f"Contract #{self.id} for vessel {self.vessel}"


# =============================================================================
# Invoice Model
# =============================================================================
class Invoice(models.Model):
    """
    Represents a financial invoice associated with a contract.

    Fields:
        price_usd: Price in USD.
        price_usd_in_word: Price in USD written in words.
        aed_price_in_word: Price in AED written in words.
        aed_price: Price in AED.
        status: Current status of the invoice (PENDING, PAID, OVERDUE, CANCELLED).
        due_date: The date payment is due.
        notes: Additional notes or comments about the invoice.
        created_at: Timestamp when the invoice was created.
        contract: One-to-one relation with a Contract (each contract has at most one invoice).
    """
    # Status choices
    STATUS_PENDING = 0
    STATUS_PAID = 1
    STATUS_OVERDUE = 2
    STATUS_CANCELLED = 3
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    price_usd = models.FloatField(default=0.0, null=True, blank=True)
    price_usd_in_word = models.CharField(max_length=150, default="", null=True, blank=True)
    aed_price_in_word = models.CharField(max_length=150, default="", null=True, blank=True)
    aed_price = models.FloatField(default=0.0, null=True, blank=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Current status of the invoice"
    )
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='invoice_obj'
    )

    def is_overdue(self):
        """
        Check if the invoice is overdue based on due_date
        """
        if self.due_date and self.status == self.STATUS_PENDING:
            return timezone.now().date() > self.due_date
        return False
    
    def get_status_display_class(self):
        """
        Returns Bootstrap class name for the status
        """
        status_classes = {
            self.STATUS_PENDING: 'warning',
            self.STATUS_PAID: 'success',
            self.STATUS_OVERDUE: 'danger',
            self.STATUS_CANCELLED: 'secondary',
        }
        return status_classes.get(self.status, 'secondary')

    def __str__(self):
        return f"Invoice #{self.id} for Contract #{self.contract.id}"


# Vessel Management Models
class Vessel(models.Model):
    name = models.CharField(max_length=100)
    imo_number = models.CharField(max_length=20, unique=True, verbose_name="IMO Number")
    vessel_type = models.CharField(max_length=50)
    built_year = models.IntegerField(null=True, blank=True)
    flag = models.CharField(max_length=50, blank=True)
    gross_tonnage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_tonnage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    length_overall = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Length Overall (m)")
    breadth = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    draft = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('repair', 'Under Repair'),
        ('docked', 'Docked'),
        ('unavailable', 'Unavailable')
    ], default='operational')
    owner = models.CharField(max_length=100, blank=True)
    operator = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.imo_number})"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Vessel'
        verbose_name_plural = 'Vessels'

class VesselDocument(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=[
        ('registration', 'Registration Certificate'),
        ('insurance', 'Insurance'),
        ('classification', 'Classification Certificate'),
        ('safety', 'Safety Certificate'),
        ('inspection', 'Inspection Report'),
        ('other', 'Other')
    ])
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='vessel_documents/')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.vessel.name} - {self.get_document_type_display()}"

class VesselMaintenance(models.Model):
    vessel = models.ForeignKey(Vessel, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=50)
    description = models.TextField()
    scheduled_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled')
    ], default='scheduled')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vendor = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vessel.name} - {self.maintenance_type} ({self.scheduled_date})"
    
    class Meta:
        ordering = ['-scheduled_date']
