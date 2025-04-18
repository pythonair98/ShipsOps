from django.urls import path
from .views import (
    contract_list,
    contract_new,
    contract_edit,
    contract_delete,
    contract_detail,
    invoice_list,
    invoice_new,
    contract_change_state,
    dashboard_home,
    invoice_edit,
    invoice_detail,
    invoice_delete,
    # Vessel management views
    vessel_list,
    vessel_detail,
    vessel_create,
    vessel_edit,
    vessel_delete,
    document_create,
    document_delete,
    maintenance_create,
    maintenance_edit,
    maintenance_delete,
    # Reporting views
    report_list,
    report_template_create,
    report_template_edit,
    report_template_delete,
    report_generate,
    report_save,
    report_view,
    report_export,
    report_delete,
    report_form,
    report_refresh
)

# URL patterns for the ShipOps application
urlpatterns = [
    # Dashboard URL
    path('', dashboard_home, name='home'),
    
    # Contract related URLs
    path('contract/', contract_list, name='contract_list'),
    path('contract/new/', contract_new, name='contract_new'),  # Added trailing slash for consistency
    path('contract/<int:contract_id>/', contract_detail, name='contract_detail'),
    path('contract/edit/<int:contract_id>/', contract_edit, name='contract_edit'),
    path('contract/delete/<int:contract_id>/', contract_delete, name='contract_delete'),
    
    # Invoice related URLs
    path('invoice/', invoice_list, name='invoice_list'),
    path('invoice/new/', invoice_new, name='invoice_new'),  # Added trailing slash for consistency
    path('invoice/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoice/edit/<int:invoice_id>/', invoice_edit, name='invoice_edit'),
    path('invoice/delete/<int:invoice_id>/', invoice_delete, name='invoice_delete'),
    
    # Contract state change URL
    path('contract/<int:contract_id>/change-state/', contract_change_state, name='contract_change_state'),
    
    # Vessel management URLs
    path('vessel/', vessel_list, name='vessel_list'),
    path('vessel/new/', vessel_create, name='vessel_create'),
    path('vessel/<int:vessel_id>/', vessel_detail, name='vessel_detail'),
    path('vessel/edit/<int:vessel_id>/', vessel_edit, name='vessel_edit'),
    path('vessel/delete/<int:vessel_id>/', vessel_delete, name='vessel_delete'),
    
    # Document management URLs
    path('vessel/<int:vessel_id>/document/new/', document_create, name='document_create'),
    path('document/<int:document_id>/delete/', document_delete, name='document_delete'),
    
    # Maintenance management URLs
    path('vessel/<int:vessel_id>/maintenance/new/', maintenance_create, name='maintenance_create'),
    path('maintenance/<int:maintenance_id>/edit/', maintenance_edit, name='maintenance_edit'),
    path('maintenance/<int:maintenance_id>/delete/', maintenance_delete, name='maintenance_delete'),
    
    # Reporting & Analytics URLs
    path('reports/', report_list, name='report-list'),
    
    # Report template URLs
    path('reports/template/new/', report_template_create, name='report_template_create'),
    path('reports/template/edit/<int:template_id>/', report_template_edit, name='report_template_edit'),
    path('reports/template/delete/<int:template_id>/', report_template_delete, name='report_template_delete'),
    
    # Report generation and management URLs
    path('reports/generate/', report_generate, name='report_generate_custom'),
    path('reports/generate/<int:template_id>/', report_generate, name='report_generate'),
    path('reports/new/', report_form, name='report_form'),
    path('reports/edit/<int:report_id>/', report_form, name='report_edit'),
    path('reports/save/', report_save, name='report_save'),
    path('reports/view/<int:report_id>/', report_view, name='report_view'),
    path('reports/export/<int:report_id>/', report_export, name='report_export'),
    path('reports/delete/<int:report_id>/', report_delete, name='report_delete'),
    path('reports/refresh/<int:report_id>/', report_refresh, name='report_refresh'),
]