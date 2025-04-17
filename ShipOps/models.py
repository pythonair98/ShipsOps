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
        created_at: Timestamp when the invoice was created.
        contract: One-to-one relation with a Contract (each contract has at most one invoice).
    """
    price_usd = models.FloatField(default=0.0, null=True, blank=True)
    price_usd_in_word = models.CharField(max_length=150, default="", null=True, blank=True)
    aed_price_in_word = models.CharField(max_length=150, default="", null=True, blank=True)
    aed_price = models.FloatField(default=0.0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    contract = models.OneToOneField(
        Contract,
        on_delete=models.CASCADE,
        related_name='invoice_obj'
    )

    def __str__(self):
        return f"Invoice #{self.id} for Contract #{self.contract.id}"


