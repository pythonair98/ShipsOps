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
    contract_analytics_view,
    invoice_reports_view,
    vessel_performance_view,
    maintenance_report_view,
    invoice_report_view,
    landing_page,
)

# URL patterns for the ShipOps application
urlpatterns = [
    # Landing page URL (for non-authenticated users)
    path('', landing_page, name='landing'),
    
    # Dashboard URL (for authenticated users)
    path('dashboard/', dashboard_home, name='home'),
    
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
    path('invoice/<int:invoice_id>/report/', invoice_report_view, name='invoice_report'),
    
    # Contract state change URL
    path('contract/<int:contract_id>/change-state/', contract_change_state, name='contract_change_state'),
    
    # Vessel management URLs
    path('vessel/', vessel_list, name='vessel_list'),
    path('vessel/new/', vessel_create, name='vessel_create'),
    path('vessel/<int:vessel_id>/', vessel_detail, name='vessel_detail'),
    path('vessel/edit/<int:vessel_id>/', vessel_edit, name='vessel_edit'),
    path('vessel/delete/<int:vessel_id>/', vessel_delete, name='vessel_delete'),
    path('reports/contract-analytics/', contract_analytics_view, name='contract_analytics'),
    path('reports/invoice-reports/', invoice_reports_view, name='invoice_reports'),
    path('reports/vessel-performance/', vessel_performance_view, name='vessel_performance'),
    path('reports/maintenance-report/', maintenance_report_view, name='maintenance_report'),
    # Document management URLs
    path('vessel/<int:vessel_id>/document/new/', document_create, name='document_create'),
    path('document/<int:document_id>/delete/', document_delete, name='document_delete'),
    
    # Maintenance management URLs
    path('vessel/<int:vessel_id>/maintenance/new/', maintenance_create, name='maintenance_create'),
    path('maintenance/<int:maintenance_id>/edit/', maintenance_edit, name='maintenance_edit'),
    path('maintenance/<int:maintenance_id>/delete/', maintenance_delete, name='maintenance_delete'),
]