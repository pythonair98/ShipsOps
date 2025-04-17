from django.urls import path
from .views import (
    contract_list,
    contract_new,
    invoice_list,
    invoice_new,
    contract_change_state,
    dashboard_home,
    invoice_edit,
    invoice_detail,
    invoice_delete
)

# URL patterns for the ShipOps application
urlpatterns = [
    # Dashboard URL
    path('', dashboard_home, name='home'),
    
    # Contract related URLs
    path('contract/', contract_list, name='contract_list'),
    path('contract/new/', contract_new, name='contract_new'),  # Added trailing slash for consistency
    
    # Invoice related URLs
    path('invoice/', invoice_list, name='invoice_list'),
    path('invoice/new/', invoice_new, name='invoice_new'),  # Added trailing slash for consistency
    path('invoice/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoice/edit/<int:invoice_id>/', invoice_edit, name='invoice_edit'),
    path('invoice/delete/<int:invoice_id>/', invoice_delete, name='invoice_delete'),
    
    # Contract state change URL
    path('contract/<int:contract_id>/change-state/', contract_change_state, name='contract_change_state'),
]