from django.contrib import admin
from .models import (
    Contact,
    Contract,
    Invoice,
    Vessel,
    VesselDocument,
    VesselMaintenance,
    ReportTemplate,
    SavedReport,
    Dashboard,
    AnalyticsLog
)


# =============================================================================
# Contract Admin
# =============================================================================
@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Contract model.
    Provides customized display, search, filtering and ordering capabilities.
    """
    list_display = (
        'id',
        'vessel',
        'charterer',
        'owner',
        'state',
        'contract_start',
        'contract_end',
        'created_at',
    )
    search_fields = ('vessel', 'charterer', 'owner', 'cargo')
    list_filter = ('state', 'contract_start', 'contract_end', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# =============================================================================
# Invoice Admin
# =============================================================================
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Invoice model.
    Enables searching, filtering and sorting of invoice records.
    """
    list_display = ('id', 'contract', 'price_usd', 'aed_price', 'created_at')
    search_fields = (
        'contract__vessel',  # Search invoices by related contract's vessel name
        'price_usd_in_word',
        'aed_price_in_word',
    )
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'


# Register Vessel models
@admin.register(Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ('name', 'imo_number', 'vessel_type', 'status', 'owner')
    list_filter = ('status', 'vessel_type')
    search_fields = ('name', 'imo_number', 'owner')
    ordering = ('name',)

@admin.register(VesselDocument)
class VesselDocumentAdmin(admin.ModelAdmin):
    list_display = ('vessel', 'document_type', 'title', 'issue_date', 'expiry_date')
    list_filter = ('document_type',)
    search_fields = ('vessel__name', 'title')
    date_hierarchy = 'issue_date'

@admin.register(VesselMaintenance)
class VesselMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vessel', 'maintenance_type', 'scheduled_date', 'status')
    list_filter = ('status', 'maintenance_type')
    search_fields = ('vessel__name', 'description', 'vendor')
    date_hierarchy = 'scheduled_date'

# Register reporting models
@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'is_public', 'updated_at')
    list_filter = ('report_type', 'is_public', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'created_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)

@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_public', 'updated_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AnalyticsLog)
class AnalyticsLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp',)
