from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import (
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
from .forms import ContractForm, InvoiceForm
from django.db import models
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q, Sum
from datetime import timedelta
import json
import csv
from django.http import HttpResponse
import xlsxwriter


@login_required
def contract_list(request):
    """
    View to display a list of all contracts.

    Retrieves all Contract objects from the database and passes them to the 'contract_list.html' template.
    Also initializes a blank ContractForm for adding a new contract.

    :param request: The HTTP request object.
    :return: Rendered 'contract_list.html' template with contract data and form.
    """
    # Get all contracts ordered by most recent first
    contracts = Contract.objects.all().order_by('-created_at')
    
    # Initialize an empty contract form
    form = ContractForm()
    
    # Prepare context dictionary for template rendering
    context = {
        'contracts': contracts,
        'form': form,
        'page_title': 'Contract Management'
    }
    
    return render(request, 'ShipOps/contract_list.html', context)


@login_required
def invoice_list(request):
    """
    View to display a list of all invoices.

    Retrieves all Invoice objects from the database and passes them to the 'invoice_list.html' template.

    :param request: The HTTP request object.
    :return: Rendered 'invoice_list.html' template with invoice data.
    """
    # Get all invoices
    invoices = Invoice.objects.all().order_by('-created_at')
    
    # Prepare context dictionary for template rendering
    context = {
        'invoices': invoices,
        'page_title': 'Invoice Management'
    }
    
    return render(request, 'ShipOps/invoice_list.html', context)


@login_required
def contract_new(request):
    """
    View to create a new contract.

    Handles both GET and POST requests. If the request method is POST, it validates and saves the form.
    If successful, a success message is displayed, and the user is redirected to the contract list.
    If the form is invalid, an error message with form errors is displayed.

    :param request: The HTTP request object.
    :return: Rendered 'contract_edit.html' template with form for contract creation.
    """
    if request.method == "POST":
        form = ContractForm(request.POST)
        if form.is_valid():
            contract = form.save()
            messages.success(request, 'Contract created successfully')
            return redirect("contract_list")
        else:
            messages.error(request, f'Error creating contract: {form.errors}')
    else:
        form = ContractForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Contract'
    }
    
    return render(request, 'ShipOps/contract_edit.html', context)


@login_required
def invoice_new(request):
    """
    View to create a new invoice.

    Handles both GET and POST requests. If the request method is POST, it validates and saves the form.
    If successful, a success message is displayed, and the user is redirected to the invoice list.
    If the form is invalid, an error message with form errors is displayed.

    :param request: The HTTP request object.
    :return: Rendered 'invoice_edit.html' template with form for invoice creation.
    """
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invoice created successfully')
            return redirect("invoice_list")
        else:
            messages.error(request, f'Error creating invoice: {form.errors}')
    else:
        form = InvoiceForm()
    
    context = {
        'form': form,
        'page_title': 'Create New Invoice'
    }
    
    return render(request, 'ShipOps/invoice_edit.html', context)

def contract_list(request):
    """
    View to display a list of all contracts.
    
    Retrieves all contracts from the database and displays them in a list view.
    
    :param request: The HTTP request object.
    :return: Rendered 'contract_list.html' template with all contracts.
    """
    contracts = Contract.objects.all()
    form = ContractForm()
    
    context = {
        'contracts': contracts,
        'form': form,
        'page_title': 'Contract List'
    }
    
    return render(request, 'ShipOps/contract_list.html', context)


@login_required(login_url='login')
def contract_edit(request, contract_id):
    """
    View to edit an existing contract.
    
    Handles both GET and POST requests. If the request method is POST, it validates and updates the contract.
    If successful, a success message is displayed, and the user is redirected to the contract list.
    If the form is invalid, an error message with form errors is displayed.
    
    :param request: The HTTP request object.
    :param contract_id: The ID of the contract to edit.
    :return: Rendered 'contract_edit.html' template with form for contract editing.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == "POST":
        form = ContractForm(request.POST, instance=contract)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contract updated successfully')
            return redirect("contract_list")
        else:
            messages.error(request, f'Error updating contract: {form.errors}')
    else:
        form = ContractForm(instance=contract)
    
    context = {
        'form': form,
        'contract': contract,
        'page_title': 'Edit Contract'
    }
    
    return render(request, 'ShipOps/contract_edit.html', context)


@login_required
def contract_delete(request, contract_id):
    """
    View to delete an existing contract.
    
    Handles POST requests to delete a contract. If successful, a success message is displayed,
    and the user is redirected to the contract list.
    
    :param request: The HTTP request object.
    :param contract_id: The ID of the contract to delete.
    :return: Redirect to the contract list page.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    
    if request.method == "POST":
        contract.delete()
        messages.success(request, 'Contract deleted successfully')
        return redirect("contract_list")
    
    return redirect("contract_list")


@login_required
def contract_detail(request, contract_id):
    """
    View to display details of a specific contract.
    
    Retrieves a specific contract from the database and displays its details.
    
    :param request: The HTTP request object.
    :param contract_id: The ID of the contract to display.
    :return: Rendered 'contract_detail.html' template with the contract details.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    
    context = {
        'contract': contract,
        'page_title': f'Contract Details: {contract}'
    }
    
    return render(request, 'ShipOps/contract_detail.html', context)

@login_required
def invoice_list(request):
    """
    View to display a list of all invoices.
    
    Retrieves all invoices from the database and displays them in a list view.
    
    :param request: The HTTP request object.
    :return: Rendered 'invoice_list.html' template with all invoices.
    """
    # Check if user is from finance department
    if not (request.user.ops_profile.is_finance or request.user.is_staff):
        messages.error(request, 'Access denied. Only finance department users can view invoices.')
        return redirect('home')  # Redirect to home or another appropriate page
    
    # Get user's profile to check permissions
    
    # Only show contracts with state TO_FIN (state=1)
    contracts = Contract.objects.filter(state=1)  # Assuming 1 represents TO_FIN state
    
    # Order contracts by most recent first
    contracts = contracts.order_by('-created_at')
    invoices = Invoice.objects.all()
    form = InvoiceForm()
    context = {
        'invoices': invoices,
        'form': form,
        'page_title': 'Invoice List'
    }
    
    return render(request, 'ShipOps/invoice_list.html', context)


@login_required
def invoice_edit(request, invoice_id):
    """
    View to edit an existing invoice.
    
    Handles both GET and POST requests. If the request method is POST, it validates and updates the invoice.
    If successful, a success message is displayed, and the user is redirected to the invoice list.
    If the form is invalid, an error message with form errors is displayed.
    
    :param request: The HTTP request object.
    :param invoice_id: The ID of the invoice to edit.
    :return: Rendered 'invoice_edit.html' template with form for invoice editing.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invoice updated successfully')
            return redirect("invoice_list")
        else:
            messages.error(request, f'Error updating invoice: {form.errors}')
    else:
        form = InvoiceForm(instance=invoice)
    
    context = {
        'form': form,
        'invoice': invoice,
        'page_title': 'Edit Invoice'
    }
    
    return render(request, 'ShipOps/invoice_edit.html', context)


@login_required
def invoice_delete(request, invoice_id):
    """
    View to delete an existing invoice.
    
    Handles POST requests to delete an invoice. If successful, a success message is displayed,
    and the user is redirected to the invoice list.
    
    :param request: The HTTP request object.
    :param invoice_id: The ID of the invoice to delete.
    :return: Redirect to the invoice list page.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == "POST":
        invoice.delete()
        messages.success(request, 'Invoice deleted successfully')
        return redirect("invoice_list")
    
    return redirect("invoice_list")


@login_required
def invoice_detail(request, invoice_id):
    """
    View to display details of a specific invoice.
    
    Retrieves a specific invoice from the database and displays its details.
    
    :param request: The HTTP request object.
    :param invoice_id: The ID of the invoice to display.
    :return: Rendered 'invoice_detail.html' template with the invoice details.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    context = {
        'invoice': invoice,
        'page_title': f'Invoice Details: {invoice}'
    }
    
    return render(request, 'ShipOps/invoice_detail.html', context)


@login_required
def contract_change_state(request, contract_id):
    """
    View to change the state of a contract.
    
    Handles GET requests to update a contract's state. If state=finance is specified,
    changes the contract state to indicate it's been sent to the finance department.
    
    :param request: The HTTP request object.
    :param contract_id: The ID of the contract to update.
    :return: Redirect to the contract list page.
    """
    contract = get_object_or_404(Contract, id=contract_id)
    state = request.GET.get('state')
    
    state_messages = {
        '0': 'marked as Pending',
        '1': 'sent to Finance Department',
        '2': 'marked as Billed',
        'finance': 'sent to Finance Department'
    }
    
    if state in state_messages:
        if state == 'finance':
            # For backward compatibility
            contract.state = 1
        else:
            contract.state = int(state)
        
        contract.save()
        messages.success(request, f"Contract #{contract.id} for {contract.vessel} {state_messages[state]}")
    
    return redirect("contract_list")


@login_required
def dashboard_home(request):
    """View for the dashboard home page"""
    # Get counts for key entities
    contract_count = Contract.objects.count()
    invoice_count = Invoice.objects.count()
    
    # Calculate total amounts
    total_usd = Invoice.objects.aggregate(total=models.Sum('price_usd'))['total'] or 0
    total_aed = Invoice.objects.aggregate(total=models.Sum('aed_price'))['total'] or 0
    
    # Get contract status distribution
    contract_status = {
        'Pending': Contract.objects.filter(state=0).count(),
        'Finance': Contract.objects.filter(state=1).count(),
        'Billed': Contract.objects.filter(state=2).count(),
        'Completed': Contract.objects.filter(state=3).count()
    }
    
    # Calculate percentages for progress bars
    total_contracts = contract_count or 1  # Avoid division by zero
    status_percentages = {
        status: round((count / total_contracts) * 100)
        for status, count in contract_status.items()
    }
    
    # Get recent contracts
    recent_contracts = Contract.objects.order_by('-created_at')[:5]
    
    # Get monthly data for contracts, invoices and revenue
    months = []
    contract_data = []
    invoice_data = []
    revenue_data = []
    
    # Generate data for the last 6 months
    for i in range(5, -1, -1):
        # Calculate the month
        month_date = timezone.now() - timezone.timedelta(days=30 * i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_name = month_date.strftime('%b')
        
        # Get next month for range
        if month_date.month == 12:
            next_month = month_date.replace(year=month_date.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = month_date.replace(month=month_date.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count contracts and invoices for the month
        month_contracts = Contract.objects.filter(created_at__gte=month_start, created_at__lt=next_month).count()
        month_invoices = Invoice.objects.filter(created_at__gte=month_start, created_at__lt=next_month).count()
        
        # Calculate revenue for the month (USD)
        month_revenue = Invoice.objects.filter(
            created_at__gte=month_start, 
            created_at__lt=next_month
        ).aggregate(total=models.Sum('price_usd'))['total'] or 0
        
        # Append data
        months.append(month_name)
        contract_data.append(month_contracts)
        invoice_data.append(month_invoices)
        revenue_data.append(month_revenue)
    
    # Monthly data for charts
    monthly_data = {
        'months': months,
        'contracts': contract_data,
        'invoices': invoice_data,
        'revenue': revenue_data
    }
    
    context = {
        'contract_count': contract_count,
        'invoice_count': invoice_count,
        'total_usd': total_usd,
        'total_aed': total_aed,
        'contract_status': contract_status,
        'status_percentages': status_percentages,
        'recent_contracts': recent_contracts,
        'monthly_data': monthly_data
    }
    
    return render(request, 'ShipOps/dashboard.html', context)

# ----- Vessel Management Views -----

@login_required
def vessel_list(request):
    """View to list all vessels with filtering capability"""
    # Get all vessels
    vessels = Vessel.objects.all()
    
    # Handle search and filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    if search_query:
        vessels = vessels.filter(
            Q(name__icontains=search_query) | 
            Q(imo_number__icontains=search_query) |
            Q(owner__icontains=search_query)
        )
    
    if status_filter:
        vessels = vessels.filter(status=status_filter)
        
    if type_filter:
        vessels = vessels.filter(vessel_type=type_filter)
    
    # Pagination
    paginator = Paginator(vessels, 10)  # Show 10 vessels per page
    page = request.GET.get('page')
    
    try:
        vessels_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        vessels_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        vessels_page = paginator.page(paginator.num_pages)
    
    # Get vessel types and statuses for filtering dropdowns
    vessel_types = Vessel.objects.values_list('vessel_type', flat=True).distinct()
    vessel_statuses = [choice[0] for choice in Vessel._meta.get_field('status').choices]
    
    # Prepare context for template
    context = {
        'vessels': vessels_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'vessel_types': vessel_types,
        'vessel_statuses': vessel_statuses,
        'total_vessels': Vessel.objects.count(),
        'operational_count': Vessel.objects.filter(status='operational').count(),
    }
    
    return render(request, 'ShipOps/vessel_list.html', context)

@login_required
def vessel_detail(request, vessel_id):
    """View to show details of a specific vessel"""
    vessel = get_object_or_404(Vessel, id=vessel_id)
    
    # Get related data
    documents = vessel.documents.all().order_by('-issue_date')
    maintenance_records = vessel.maintenance_records.all().order_by('-scheduled_date')
    contracts = Contract.objects.filter(vessel=vessel.name).order_by('-created_at')
    
    # Calculate statistics
    total_contracts = contracts.count()
    contracts_this_year = contracts.filter(created_at__year=timezone.now().year).count()
    maintenance_costs = vessel.maintenance_records.aggregate(total=Sum('cost'))['total'] or 0
    upcoming_maintenance = vessel.maintenance_records.filter(
        scheduled_date__gte=timezone.now().date(),
        status__in=['scheduled', 'in_progress']
    ).order_by('scheduled_date')
    
    # Expiring documents (documents expiring in the next 90 days)
    today = timezone.now().date()
    expiring_documents = vessel.documents.filter(
        expiry_date__isnull=False,
        expiry_date__gte=today,
        expiry_date__lte=today + timedelta(days=90)
    ).order_by('expiry_date')
    
    context = {
        'vessel': vessel,
        'documents': documents,
        'maintenance_records': maintenance_records,
        'contracts': contracts,
        'total_contracts': total_contracts,
        'contracts_this_year': contracts_this_year,
        'maintenance_costs': maintenance_costs,
        'upcoming_maintenance': upcoming_maintenance,
        'expiring_documents': expiring_documents,
    }
    
    return render(request, 'ShipOps/vessel_detail.html', context)

@login_required
def vessel_create(request):
    """View to create a new vessel"""
    if request.method == 'POST':
        # Process the form data
        name = request.POST.get('name')
        imo_number = request.POST.get('imo_number')
        vessel_type = request.POST.get('vessel_type')
        built_year = request.POST.get('built_year') or None
        flag = request.POST.get('flag', '')
        gross_tonnage = request.POST.get('gross_tonnage') or None
        net_tonnage = request.POST.get('net_tonnage') or None
        length_overall = request.POST.get('length_overall') or None
        breadth = request.POST.get('breadth') or None
        draft = request.POST.get('draft') or None
        status = request.POST.get('status')
        owner = request.POST.get('owner', '')
        operator = request.POST.get('operator', '')
        
        # Validate required fields
        if not name or not imo_number or not vessel_type:
            messages.error(request, 'Please provide all required fields.')
            return redirect('vessel_create')
        
        # Check if vessel with IMO number already exists
        if Vessel.objects.filter(imo_number=imo_number).exists():
            messages.error(request, f'Vessel with IMO number {imo_number} already exists.')
            return redirect('vessel_create')
            
        # Create the vessel
        vessel = Vessel(
            name=name,
            imo_number=imo_number,
            vessel_type=vessel_type,
            built_year=built_year,
            flag=flag,
            gross_tonnage=gross_tonnage,
            net_tonnage=net_tonnage,
            length_overall=length_overall,
            breadth=breadth,
            draft=draft,
            status=status,
            owner=owner,
            operator=operator
        )
        vessel.save()
        
        messages.success(request, f'Vessel {name} has been created successfully.')
        return redirect('vessel_detail', vessel_id=vessel.id)
    
    # For GET request, display the form
    vessel_types = Vessel.objects.values_list('vessel_type', flat=True).distinct()
    vessel_statuses = [choice for choice in Vessel._meta.get_field('status').choices]
    
    context = {
        'vessel_types': vessel_types,
        'vessel_statuses': vessel_statuses,
    }
    
    return render(request, 'ShipOps/vessel_form.html', context)

@login_required
def vessel_edit(request, vessel_id):
    """View to edit an existing vessel"""
    vessel = get_object_or_404(Vessel, id=vessel_id)
    
    if request.method == 'POST':
        # Process the form data
        vessel.name = request.POST.get('name')
        vessel.imo_number = request.POST.get('imo_number')
        vessel.vessel_type = request.POST.get('vessel_type')
        vessel.built_year = request.POST.get('built_year') or None
        vessel.flag = request.POST.get('flag', '')
        vessel.gross_tonnage = request.POST.get('gross_tonnage') or None
        vessel.net_tonnage = request.POST.get('net_tonnage') or None
        vessel.length_overall = request.POST.get('length_overall') or None
        vessel.breadth = request.POST.get('breadth') or None
        vessel.draft = request.POST.get('draft') or None
        vessel.status = request.POST.get('status')
        vessel.owner = request.POST.get('owner', '')
        vessel.operator = request.POST.get('operator', '')
        
        # Validate required fields
        if not vessel.name or not vessel.imo_number or not vessel.vessel_type:
            messages.error(request, 'Please provide all required fields.')
            return redirect('vessel_edit', vessel_id=vessel_id)
        
        # Check if vessel with IMO number already exists (excluding this vessel)
        if Vessel.objects.filter(imo_number=vessel.imo_number).exclude(id=vessel_id).exists():
            messages.error(request, f'Another vessel with IMO number {vessel.imo_number} already exists.')
            return redirect('vessel_edit', vessel_id=vessel_id)
            
        # Save the updated vessel
        vessel.save()
        
        messages.success(request, f'Vessel {vessel.name} has been updated successfully.')
        return redirect('vessel_detail', vessel_id=vessel.id)
    
    # For GET request, display the form with vessel data
    vessel_types = Vessel.objects.values_list('vessel_type', flat=True).distinct()
    vessel_statuses = [choice for choice in Vessel._meta.get_field('status').choices]
    
    context = {
        'vessel': vessel,
        'vessel_types': vessel_types,
        'vessel_statuses': vessel_statuses,
        'is_edit': True,
    }
    
    return render(request, 'ShipOps/vessel_form.html', context)

@login_required
def vessel_delete(request, vessel_id):
    """View to delete a vessel"""
    vessel = get_object_or_404(Vessel, id=vessel_id)
    
    if request.method == 'POST':
        vessel_name = vessel.name
        vessel.delete()
        messages.success(request, f'Vessel {vessel_name} has been deleted successfully.')
        return redirect('vessel_list')
    
    # For GET request, ask for confirmation
    return render(request, 'ShipOps/vessel_confirm_delete.html', {'vessel': vessel})

@login_required
def document_create(request, vessel_id):
    """View to add a document to a vessel"""
    vessel = get_object_or_404(Vessel, id=vessel_id)
    
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        title = request.POST.get('title')
        issue_date = request.POST.get('issue_date')
        expiry_date = request.POST.get('expiry_date') or None
        notes = request.POST.get('notes', '')
        file = request.FILES.get('file')
        
        # Validate required fields
        if not document_type or not title or not issue_date or not file:
            messages.error(request, 'Please provide all required fields.')
            return redirect('document_create', vessel_id=vessel_id)
            
        # Create the document
        document = VesselDocument(
            vessel=vessel,
            document_type=document_type,
            title=title,
            issue_date=issue_date,
            expiry_date=expiry_date,
            notes=notes,
            file=file
        )
        document.save()
        
        messages.success(request, f'Document {title} has been added successfully.')
        return redirect('vessel_detail', vessel_id=vessel_id)
    
    # For GET request, display the form
    document_types = [choice for choice in VesselDocument._meta.get_field('document_type').choices]
    
    context = {
        'vessel': vessel,
        'document_types': document_types,
    }
    
    return render(request, 'ShipOps/document_form.html', context)

@login_required
def document_delete(request, document_id):
    """View to delete a vessel document"""
    document = get_object_or_404(VesselDocument, id=document_id)
    vessel_id = document.vessel.id
    
    if request.method == 'POST':
        document_title = document.title
        document.delete()
        messages.success(request, f'Document {document_title} has been deleted successfully.')
        return redirect('vessel_detail', vessel_id=vessel_id)
    
    # For GET request, ask for confirmation
    return render(request, 'ShipOps/document_confirm_delete.html', {'document': document})

@login_required
def maintenance_create(request, vessel_id):
    """View to add a maintenance record to a vessel"""
    vessel = get_object_or_404(Vessel, id=vessel_id)
    
    if request.method == 'POST':
        maintenance_type = request.POST.get('maintenance_type')
        description = request.POST.get('description')
        scheduled_date = request.POST.get('scheduled_date')
        completion_date = request.POST.get('completion_date') or None
        status = request.POST.get('status')
        cost = request.POST.get('cost') or None
        vendor = request.POST.get('vendor', '')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not maintenance_type or not description or not scheduled_date:
            messages.error(request, 'Please provide all required fields.')
            return redirect('maintenance_create', vessel_id=vessel_id)
            
        # Create the maintenance record
        maintenance = VesselMaintenance(
            vessel=vessel,
            maintenance_type=maintenance_type,
            description=description,
            scheduled_date=scheduled_date,
            completion_date=completion_date,
            status=status,
            cost=cost,
            vendor=vendor,
            notes=notes
        )
        maintenance.save()
        
        messages.success(request, f'Maintenance record has been added successfully.')
        return redirect('vessel_detail', vessel_id=vessel_id)
    
    # For GET request, display the form
    maintenance_statuses = [choice for choice in VesselMaintenance._meta.get_field('status').choices]
    
    context = {
        'vessel': vessel,
        'maintenance_statuses': maintenance_statuses,
    }
    
    return render(request, 'ShipOps/maintenance_form.html', context)

@login_required
def maintenance_edit(request, maintenance_id):
    """View to edit a maintenance record"""
    maintenance = get_object_or_404(VesselMaintenance, id=maintenance_id)
    vessel_id = maintenance.vessel.id
    
    if request.method == 'POST':
        # Process the form data
        maintenance.maintenance_type = request.POST.get('maintenance_type')
        maintenance.description = request.POST.get('description')
        maintenance.scheduled_date = request.POST.get('scheduled_date')
        maintenance.completion_date = request.POST.get('completion_date') or None
        maintenance.status = request.POST.get('status')
        maintenance.cost = request.POST.get('cost') or None
        maintenance.vendor = request.POST.get('vendor', '')
        maintenance.notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not maintenance.maintenance_type or not maintenance.description or not maintenance.scheduled_date:
            messages.error(request, 'Please provide all required fields.')
            return redirect('maintenance_edit', maintenance_id=maintenance_id)
            
        # Save the updated maintenance record
        maintenance.save()
        
        messages.success(request, f'Maintenance record has been updated successfully.')
        return redirect('vessel_detail', vessel_id=vessel_id)
    
    # For GET request, display the form with maintenance data
    maintenance_statuses = [choice for choice in VesselMaintenance._meta.get_field('status').choices]
    
    context = {
        'maintenance': maintenance,
        'vessel': maintenance.vessel,
        'maintenance_statuses': maintenance_statuses,
        'is_edit': True,
    }
    
    return render(request, 'ShipOps/maintenance_form.html', context)

@login_required
def maintenance_delete(request, maintenance_id):
    """View to delete a maintenance record"""
    maintenance = get_object_or_404(VesselMaintenance, id=maintenance_id)
    vessel_id = maintenance.vessel.id
    
    if request.method == 'POST':
        maintenance.delete()
        messages.success(request, f'Maintenance record has been deleted successfully.')
        return redirect('vessel_detail', vessel_id=vessel_id)
    
    # For GET request, ask for confirmation
    return render(request, 'ShipOps/maintenance_confirm_delete.html', {'maintenance': maintenance})

# ----- Reporting & Analytics Views -----

@login_required
def report_list(request):
    """View to list all report templates and saved reports"""
    # Get report templates
    templates = ReportTemplate.objects.filter(
        models.Q(created_by=request.user) | models.Q(is_public=True)
    ).order_by('-updated_at')
    
    # Get saved reports
    saved_reports = SavedReport.objects.filter(
        created_by=request.user
    ).order_by('-created_at')
    
    # Log the action
    AnalyticsLog.objects.create(
        user=request.user,
        action='view_report',
        details={'page': 'report-list'}
    )
    
    context = {
        'templates': templates,
        'saved_reports': saved_reports,
        'report_types': dict(ReportTemplate._meta.get_field('report_type').choices)
    }
    
    return render(request, 'ShipOps/reports/reports_list.html', context)

@login_required
def report_template_create(request):
    """View to create a new report template"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        report_type = request.POST.get('report_type')
        is_public = request.POST.get('is_public') == 'on'
        
        # Get configuration fields based on the report type
        configuration = {}
        
        if report_type == 'contract':
            configuration['fields'] = request.POST.getlist('contract_fields')
            configuration['filters'] = {
                'date_range': request.POST.get('contract_date_range') == 'on',
                'state': request.POST.get('contract_state') == 'on',
                'charterer': request.POST.get('contract_charterer') == 'on',
                'vessel': request.POST.get('contract_vessel') == 'on'
            }
            configuration['grouping'] = request.POST.get('contract_grouping', '')
            
        elif report_type == 'invoice':
            configuration['fields'] = request.POST.getlist('invoice_fields')
            configuration['filters'] = {
                'date_range': request.POST.get('invoice_date_range') == 'on',
                'status': request.POST.get('invoice_status') == 'on',
                'currency': request.POST.get('invoice_currency') == 'on',
                'contract': request.POST.get('invoice_contract') == 'on'
            }
            configuration['grouping'] = request.POST.get('invoice_grouping', '')
            
        elif report_type == 'vessel':
            configuration['fields'] = request.POST.getlist('vessel_fields')
            configuration['filters'] = {
                'status': request.POST.get('vessel_status') == 'on',
                'type': request.POST.get('vessel_type') == 'on',
                'flag': request.POST.get('vessel_flag') == 'on'
            }
            configuration['grouping'] = request.POST.get('vessel_grouping', '')
            
        elif report_type == 'financial':
            configuration['chart_type'] = request.POST.get('chart_type', 'bar')
            configuration['time_period'] = request.POST.get('time_period', 'monthly')
            configuration['metrics'] = request.POST.getlist('financial_metrics')
            configuration['currency'] = request.POST.get('currency', 'USD')
            
        # Create the template
        template = ReportTemplate(
            name=name,
            description=description,
            report_type=report_type,
            created_by=request.user,
            is_public=is_public,
            configuration=configuration
        )
        template.save()
        
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='create_report',
            details={'template_id': template.id, 'report_type': report_type}
        )
        
        messages.success(request, f'Report template "{name}" has been created successfully.')
        return redirect('report_generate', template_id=template.id)
    
    # Prepare context for the form
    context = {
        'report_types': ReportTemplate._meta.get_field('report_type').choices,
        'contract_fields': [
            ('id', 'Contract ID'),
            ('charterer', 'Charterer'),
            ('vessel', 'Vessel'),
            ('owner', 'Owner'),
            ('start_date', 'Start Date'),
            ('end_date', 'End Date'),
            ('state', 'State'),
            ('created_at', 'Created Date')
        ],
        'invoice_fields': [
            ('id', 'Invoice ID'),
            ('contract', 'Contract'),
            ('invoice_number', 'Invoice Number'),
            ('invoice_date', 'Invoice Date'),
            ('due_date', 'Due Date'),
            ('invoice_amount', 'Amount'),
            ('invoice_currency', 'Currency'),
            ('status', 'Status')
        ],
        'vessel_fields': [
            ('name', 'Vessel Name'),
            ('imo_number', 'IMO Number'),
            ('vessel_type', 'Vessel Type'),
            ('built_year', 'Built Year'),
            ('flag', 'Flag'),
            ('status', 'Status'),
            ('owner', 'Owner'),
            ('operator', 'Operator')
        ],
        'financial_metrics': [
            ('contract_value', 'Contract Value'),
            ('invoice_amount', 'Invoice Amount'),
            ('paid_amount', 'Paid Amount'),
            ('outstanding_amount', 'Outstanding Amount'),
            ('maintenance_cost', 'Maintenance Cost')
        ]
    }
    
    return render(request, 'ShipOps/reports/report_template_form.html', context)

@login_required
def report_generate(request, template_id=None):
    """View to generate a report based on a template or custom parameters"""
    template = None
    if template_id:
        template = get_object_or_404(ReportTemplate, id=template_id)
        # Check if user has access to the template
        if not (template.created_by == request.user or template.is_public):
            messages.error(request, "You don't have permission to access this report template.")
            return redirect('report-list')
    
    # Default report type is contract if no template is provided
    report_type = template.report_type if template else request.GET.get('report_type', 'contract')
    
    # Initialize variables for the report data
    data = []
    chart_data = {}
    parameters = {}
    
    if request.method == 'GET' and ('generate' in request.GET or template):
        # Extract parameters from the request or template
        if template:
            # Use template configuration as defaults
            configuration = template.configuration
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            status_filter = request.GET.get('status', '')
            grouping = configuration.get('grouping', '')
            
            # Store parameters for potential saving
            parameters = {
                'template_id': template.id,
                'start_date': start_date,
                'end_date': end_date,
                'status': status_filter,
                'grouping': grouping
            }
        else:
            # No template, use request parameters directly
            configuration = {
                'fields': request.GET.getlist('fields'),
                'filters': {},
                'grouping': request.GET.get('grouping', '')
            }
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            status_filter = request.GET.get('status', '')
            grouping = request.GET.get('grouping', '')
            
            # Store parameters for potential saving
            parameters = {
                'report_type': report_type,
                'fields': request.GET.getlist('fields'),
                'start_date': start_date,
                'end_date': end_date,
                'status': status_filter,
                'grouping': grouping
            }
        
        # Generate report data based on the report type
        if report_type == 'contract':
            queryset = Contract.objects.all()
            
            # Apply filters
            if start_date and end_date:
                queryset = queryset.filter(
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date
                )
                
            if status_filter:
                queryset = queryset.filter(state=status_filter)
            
            # Apply grouping if specified
            if grouping == 'charterer':
                data = list(queryset.values('charterer').annotate(
                    count=models.Count('id'),
                    total_value=models.Sum('price_usd')
                ).order_by('-count'))
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['charterer'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Contracts',
                            'data': [item['count'] for item in data]
                        }
                    ]
                }
            elif grouping == 'vessel':
                data = list(queryset.values('vessel').annotate(
                    count=models.Count('id'),
                    total_value=models.Sum('price_usd')
                ).order_by('-count'))
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['vessel'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Contracts',
                            'data': [item['count'] for item in data]
                        }
                    ]
                }
            elif grouping == 'month':
                # Group by month
                month_data = {}
                for contract in queryset:
                    month_key = contract.created_at.strftime('%Y-%m')
                    month_name = contract.created_at.strftime('%b %Y')
                    
                    if month_key not in month_data:
                        month_data[month_key] = {
                            'month': month_name,
                            'count': 0,
                            'total_value': 0
                        }
                    
                    month_data[month_key]['count'] += 1
                    month_data[month_key]['total_value'] += contract.price_usd
                
                # Convert to list and sort by month
                data = list(month_data.values())
                data.sort(key=lambda x: x['month'])
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['month'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Contracts',
                            'data': [item['count'] for item in data]
                        }
                    ]
                }
            else:
                # No grouping, just list the contracts
                data = list(queryset.values())
        
        elif report_type == 'invoice':
            # Similar implementation for invoice reports
            queryset = Invoice.objects.all()
            
            # Apply filters
            if start_date and end_date:
                queryset = queryset.filter(
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date
                )
                
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Apply grouping if specified
            if grouping == 'contract':
                data = list(queryset.values('contract__id', 'contract__charterer').annotate(
                    count=models.Count('id'),
                    total_amount=models.Sum('invoice_amount')
                ).order_by('-count'))
            elif grouping == 'month':
                # Group by month
                month_data = {}
                for invoice in queryset:
                    month_key = invoice.created_at.strftime('%Y-%m')
                    month_name = invoice.created_at.strftime('%b %Y')
                    
                    if month_key not in month_data:
                        month_data[month_key] = {
                            'month': month_name,
                            'count': 0,
                            'total_amount': 0
                        }
                    
                    month_data[month_key]['count'] += 1
                    if invoice.invoice_currency == 'USD':
                        month_data[month_key]['total_amount'] += invoice.invoice_amount
                
                # Convert to list and sort by month
                data = list(month_data.values())
                data.sort(key=lambda x: x['month'])
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['month'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Invoices',
                            'data': [item['count'] for item in data],
                            'backgroundColor': 'rgba(54, 162, 235, 0.5)'
                        },
                        {
                            'label': 'Total Amount (USD)',
                            'data': [item['total_amount'] for item in data],
                            'backgroundColor': 'rgba(255, 99, 132, 0.5)'
                        }
                    ]
                }
            else:
                # No grouping, just list the invoices
                data = list(queryset.values())
        
        elif report_type == 'vessel':
            # Implementation for vessel reports
            queryset = Vessel.objects.all()
            
            # Apply filters
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Apply grouping if specified
            if grouping == 'status':
                data = list(queryset.values('status').annotate(
                    count=models.Count('id')
                ).order_by('-count'))
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['status'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Vessels',
                            'data': [item['count'] for item in data],
                            'backgroundColor': [
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(255, 159, 64, 0.5)',
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(153, 102, 255, 0.5)'
                            ]
                        }
                    ]
                }
            elif grouping == 'type':
                data = list(queryset.values('vessel_type').annotate(
                    count=models.Count('id')
                ).order_by('-count'))
                
                # Prepare chart data
                chart_data = {
                    'labels': [item['vessel_type'] for item in data],
                    'datasets': [
                        {
                            'label': 'Number of Vessels',
                            'data': [item['count'] for item in data],
                            'backgroundColor': [
                                'rgba(75, 192, 192, 0.5)',
                                'rgba(255, 159, 64, 0.5)',
                                'rgba(255, 99, 132, 0.5)',
                                'rgba(54, 162, 235, 0.5)',
                                'rgba(153, 102, 255, 0.5)',
                                'rgba(201, 203, 207, 0.5)'
                            ]
                        }
                    ]
                }
            else:
                # No grouping, just list the vessels
                data = list(queryset.values())
        
        # Log the report generation
        AnalyticsLog.objects.create(
            user=request.user,
            action='generate_report',
            details={
                'report_type': report_type,
                'template_id': template.id if template else None,
                'parameters': parameters
            }
        )
    
    # Prepare context
    context = {
        'template': template,
        'report_type': report_type,
        'data': data,
        'chart_data': chart_data,
        'parameters': parameters,
        'report_types': dict(ReportTemplate._meta.get_field('report_type').choices)
    }
    
    return render(request, 'ShipOps/reports/report_create.html', context)

@login_required
def report_save(request):
    """View to save a generated report"""
    if request.method != 'POST':
        return redirect('report-list')
    
    # Get report data from the form
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    report_type = request.POST.get('report_type')
    template_id = request.POST.get('template_id')
    parameters = json.loads(request.POST.get('parameters', '{}'))
    data = json.loads(request.POST.get('data', '[]'))
    
    # Create file if chart data is available
    file = None
    
    # Create the saved report
    template = None
    if template_id:
        template = get_object_or_404(ReportTemplate, id=template_id)
    
    saved_report = SavedReport(
        name=name,
        description=description,
        report_type=report_type,
        template=template,
        created_by=request.user,
        parameters=parameters,
        data=data,
        file=file
    )
    saved_report.save()
    
    # Log the action
    AnalyticsLog.objects.create(
        user=request.user,
        action='save_report',
        details={'report_id': saved_report.id, 'report_type': report_type}
    )
    
    messages.success(request, f'Report "{name}" has been saved successfully.')
    return redirect('report_view', report_id=saved_report.id)

@login_required
def report_view(request, report_id):
    """View to display a saved report"""
    report = get_object_or_404(SavedReport, id=report_id)
    
    # Check if user has access to the report
    if report.created_by != request.user:
        messages.error(request, "You don't have permission to view this report.")
        return redirect('report-list')
    
    # Log the action
    AnalyticsLog.objects.create(
        user=request.user,
        action='view_report',
        details={'report_id': report.id, 'report_type': report.report_type}
    )
    
    context = {
        'report': report,
        'data': report.data,
        'parameters': report.parameters,
        'report_types': dict(SavedReport._meta.get_field('report_type').choices)
    }
    
    return render(request, 'ShipOps/reports/report_view.html', context)

@login_required
def report_export(request, report_id):
    """View to export a report as CSV or Excel"""
    report = get_object_or_404(SavedReport, id=report_id)
    
    # Check if user has access to the report
    if report.created_by != request.user:
        messages.error(request, "You don't have permission to export this report.")
        return redirect('report-list')
    
    format_type = request.GET.get('format', 'csv')
    
    # Get report data
    data = report.data
    
    if format_type == 'csv':
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report.name}.csv"'
        
        # Write CSV data
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='export_report',
            details={'report_id': report.id, 'format': 'csv'}
        )
        
        return response
    
    elif format_type == 'excel':
        # Create Excel response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{report.name}.xlsx"'
        
        # Create workbook
        workbook = xlsxwriter.Workbook(response)
        worksheet = workbook.add_worksheet()
        
        # Write headers
        if data:
            headers = list(data[0].keys())
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Write data
            for row, item in enumerate(data, start=1):
                for col, key in enumerate(headers):
                    worksheet.write(row, col, item.get(key, ''))
        
        workbook.close()
        
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='export_report',
            details={'report_id': report.id, 'format': 'excel'}
        )
        
        return response
    
    # If not CSV or Excel, redirect back to the report
    return redirect('report_view', report_id=report.id)

@login_required
def report_template_edit(request, template_id):
    """View to edit an existing report template"""
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Check if user has permission to edit this template
    if template.created_by != request.user:
        messages.error(request, "You don't have permission to edit this template.")
        return redirect('reports_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        report_type = request.POST.get('report_type')
        is_public = request.POST.get('is_public') == 'on'
        
        # Get configuration fields based on the report type
        configuration = {}
        
        if report_type == 'contract':
            configuration['fields'] = request.POST.getlist('contract_fields')
            configuration['filters'] = {
                'date_range': request.POST.get('contract_date_range') == 'on',
                'state': request.POST.get('contract_state') == 'on',
                'charterer': request.POST.get('contract_charterer') == 'on',
                'vessel': request.POST.get('contract_vessel') == 'on'
            }
            configuration['grouping'] = request.POST.get('contract_grouping', '')
            
        elif report_type == 'invoice':
            configuration['fields'] = request.POST.getlist('invoice_fields')
            configuration['filters'] = {
                'date_range': request.POST.get('invoice_date_range') == 'on',
                'status': request.POST.get('invoice_status') == 'on',
                'currency': request.POST.get('invoice_currency') == 'on',
                'contract': request.POST.get('invoice_contract') == 'on'
            }
            configuration['grouping'] = request.POST.get('invoice_grouping', '')
        
        # Update the template
        template.name = name
        template.description = description
        template.report_type = report_type
        template.is_public = is_public
        template.configuration = configuration
        template.save()
        
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='edit_report_template',
            details={'template_id': template.id}
        )
        
        messages.success(request, f'Report template "{name}" has been updated successfully.')
        return redirect('reports_list')
    
    # Prepare context for the form
    context = {
        'template': template,
        'report_types': ReportTemplate._meta.get_field('report_type').choices,
        'contract_fields': [
            ('id', 'Contract ID'),
            ('charterer', 'Charterer'),
            ('vessel', 'Vessel'),
            ('owner', 'Owner'),
            ('start_date', 'Start Date'),
            ('end_date', 'End Date'),
            ('state', 'State'),
            ('created_at', 'Created Date')
        ],
        'invoice_fields': [
            ('id', 'Invoice ID'),
            ('contract', 'Contract'),
            ('invoice_number', 'Invoice Number'),
            ('invoice_date', 'Invoice Date'),
            ('due_date', 'Due Date'),
            ('invoice_amount', 'Amount'),
            ('invoice_currency', 'Currency'),
            ('status', 'Status')
        ],
        'vessel_fields': [
            ('name', 'Vessel Name'),
            ('imo_number', 'IMO Number'),
            ('vessel_type', 'Vessel Type'),
            ('built_year', 'Built Year'),
            ('flag', 'Flag'),
            ('status', 'Status'),
            ('owner', 'Owner'),
            ('operator', 'Operator')
        ]
    }
    
    return render(request, 'ShipOps/reports/report_template_form.html', context)

@login_required
def report_template_delete(request, template_id):
    """View to delete a report template"""
    template = get_object_or_404(ReportTemplate, id=template_id)
    
    # Check if user has permission to delete this template
    if template.created_by != request.user:
        messages.error(request, "You don't have permission to delete this template.")
        return redirect('reports_list')
    
    if request.method == 'POST':
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='delete_report_template',
            details={'template_id': template.id, 'template_name': template.name}
        )
        
        # Delete the template
        template_name = template.name
        template.delete()
        
        messages.success(request, f'Report template "{template_name}" has been deleted successfully.')
    
    return redirect('reports_list')

@login_required
def report_form(request, report_id=None):
    """View to create a new report or edit an existing one"""
    report = None
    if report_id:
        report = get_object_or_404(SavedReport, id=report_id)
        
        # Check if user has permission to edit this report
        if report.created_by != request.user:
            messages.error(request, "You don't have permission to edit this report.")
            return redirect('reports_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        report_type = request.POST.get('report_type')
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        
        # Process filters
        filters = {}
        for key, value in request.POST.items():
            if key.startswith('filters['):
                filter_key = key[8:-1]  # Extract the key between 'filters[' and ']'
                filters[filter_key] = value
        
        # Process chart types
        chart_types = []
        for key, value in request.POST.items():
            if key.startswith('charts[') and value == 'on':
                chart_type = key[7:-1]  # Extract the chart type between 'charts[' and ']'
                chart_types.append(chart_type)
        
        # Process display options
        show_summary = request.POST.get('display[summary]') == 'on'
        show_table = request.POST.get('display[table]') == 'on'
        
        # Create parameters object
        parameters = {
            'start_date': start_date,
            'end_date': end_date,
            'filters': filters,
            'chart_types': chart_types,
            'show_summary': show_summary,
            'show_table': show_table
        }
        
        # Generate report data based on parameters
        data = generate_report_data(report_type, parameters)
        
        if report:
            # Update existing report
            report.name = name
            report.report_type = report_type
            report.parameters = parameters
            report.data = data
            report.save()
            
            # Log the action
            AnalyticsLog.objects.create(
                user=request.user,
                action='update_report',
                details={'report_id': report.id}
            )
            
            messages.success(request, f'Report "{name}" has been updated successfully.')
        else:
            # Create new report
            report = SavedReport(
                name=name,
                report_type=report_type,
                created_by=request.user,
                parameters=parameters,
                data=data
            )
            report.save()
            
            # Log the action
            AnalyticsLog.objects.create(
                user=request.user,
                action='create_report',
                details={'report_id': report.id}
            )
            
            messages.success(request, f'Report "{name}" has been created successfully.')
        
        return redirect('report_view', report_id=report.id)
    
    # Prepare context for the form
    vessels = Vessel.objects.all()
    vessel_types = VesselType.objects.all()
    
    context = {
        'report': report,
        'vessels': vessels,
        'vessel_types': vessel_types
    }
    
    return render(request, 'ShipOps/reports/report_form.html', context)

@login_required
def report_delete(request, report_id):
    """View to delete a saved report"""
    report = get_object_or_404(SavedReport, id=report_id)
    
    # Check if user has permission to delete this report
    if report.created_by != request.user:
        messages.error(request, "You don't have permission to delete this report.")
        return redirect('reports_list')
    
    if request.method == 'POST':
        # Log the action
        AnalyticsLog.objects.create(
            user=request.user,
            action='delete_report',
            details={'report_id': report.id, 'report_name': report.name}
        )
        
        # Delete the report
        report_name = report.name
        report.delete()
        
        messages.success(request, f'Report "{report_name}" has been deleted successfully.')
    
    return redirect('reports_list')

@login_required
def report_refresh(request, report_id):
    """View to refresh the data of a saved report"""
    report = get_object_or_404(SavedReport, id=report_id)
    
    # Check if user has permission to refresh this report
    if report.created_by != request.user:
        messages.error(request, "You don't have permission to refresh this report.")
        return redirect('reports_list')
    
    # Generate fresh data based on the stored parameters
    report.data = generate_report_data(report.report_type, report.parameters)
    report.save()
    
    # Log the action
    AnalyticsLog.objects.create(
        user=request.user,
        action='refresh_report',
        details={'report_id': report.id}
    )
    
    messages.success(request, f'Report "{report.name}" has been refreshed successfully.')
    return redirect('report_view', report_id=report.id)

def generate_report_data(report_type, parameters):
    """Helper function to generate report data based on type and parameters"""
    data = {'items': [], 'summary': [], 'charts': {}}
    
    # Extract parameters
    start_date = parameters.get('start_date')
    end_date = parameters.get('end_date')
    filters = parameters.get('filters', {})
    
    if report_type == 'contract':
        # Get contracts
        queryset = Contract.objects.all()
        
        # Apply date filters if provided
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
        
        # Apply status filter if provided
        contract_status = filters.get('contract_status', [])
        if contract_status:
            queryset = queryset.filter(state__in=contract_status)
        
        # Apply vessel filter if provided
        vessel_ids = filters.get('vessel', [])
        if vessel_ids:
            queryset = queryset.filter(vessel_id__in=vessel_ids)
        
        # Prepare data
        contracts = list(queryset.values())
        data['items'] = contracts
        
        # Prepare summary
        total_contracts = len(contracts)
        total_amount = sum(c.get('price_usd', 0) for c in contracts)
        pending_contracts = sum(1 for c in contracts if c.get('state') == 'Pending')
        completed_contracts = sum(1 for c in contracts if c.get('state') == 'Completed')
        
        data['summary'] = [
            {'label': 'Total Contracts', 'value': total_contracts, 'icon': 'file-contract', 'color': 'primary'},
            {'label': 'Total Amount (USD)', 'value': f"${total_amount:,.2f}", 'icon': 'dollar-sign', 'color': 'success'},
            {'label': 'Pending Contracts', 'value': pending_contracts, 'icon': 'clock', 'color': 'warning'},
            {'label': 'Completed Contracts', 'value': completed_contracts, 'icon': 'check-circle', 'color': 'info'}
        ]
        
        # Prepare chart data
        chart_data = {}
        
        # Status distribution
        status_counts = {}
        for contract in contracts:
            state = contract.get('state', 'Unknown')
            status_counts[state] = status_counts.get(state, 0) + 1
        
        chart_data['status'] = {
            'type': 'pie',
            'data': {
                'labels': list(status_counts.keys()),
                'datasets': [{
                    'data': list(status_counts.values()),
                    'backgroundColor': [
                        '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'
                    ]
                }]
            }
        }
        
        # Monthly contracts
        monthly_counts = {}
        for contract in contracts:
            if 'created_at' in contract and contract['created_at']:
                month = contract['created_at'][:7]  # Get YYYY-MM format
                monthly_counts[month] = monthly_counts.get(month, 0) + 1
        
        # Sort months
        sorted_months = sorted(monthly_counts.keys())
        
        chart_data['monthly'] = {
            'type': 'bar',
            'data': {
                'labels': sorted_months,
                'datasets': [{
                    'label': 'Contracts',
                    'data': [monthly_counts[month] for month in sorted_months],
                    'backgroundColor': '#4e73df'
                }]
            }
        }
        
        data['charts'] = chart_data
    
    elif report_type == 'invoice':
        # Get invoices
        queryset = Invoice.objects.all()
        
        # Apply date filters if provided
        if start_date and end_date:
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
        
        # Apply status filter if provided
        payment_status = filters.get('payment_status', [])
        if payment_status:
            queryset = queryset.filter(status__in=payment_status)
        
        # Apply currency filter if provided
        currency = filters.get('currency')
        if currency:
            if currency == 'USD':
                queryset = queryset.filter(price_usd__gt=0)
            elif currency == 'AED':
                queryset = queryset.filter(aed_price__gt=0)
        
        # Prepare data
        invoices = list(queryset.values())
        data['items'] = invoices
        
        # Prepare summary
        total_invoices = len(invoices)
        total_amount_usd = sum(i.get('price_usd', 0) for i in invoices)
        total_amount_aed = sum(i.get('aed_price', 0) for i in invoices)
        paid_invoices = sum(1 for i in invoices if i.get('status') == 'Paid')
        
        data['summary'] = [
            {'label': 'Total Invoices', 'value': total_invoices, 'icon': 'file-invoice', 'color': 'primary'},
            {'label': 'Total USD', 'value': f"${total_amount_usd:,.2f}", 'icon': 'dollar-sign', 'color': 'success'},
            {'label': 'Total AED', 'value': f"AED {total_amount_aed:,.2f}", 'icon': 'money-bill-wave', 'color': 'info'},
            {'label': 'Paid Invoices', 'value': paid_invoices, 'icon': 'check-circle', 'color': 'success'}
        ]
        
        # Prepare chart data
        chart_data = {}
        
        # Status distribution
        status_counts = {}
        for invoice in invoices:
            status = invoice.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        chart_data['status'] = {
            'type': 'pie',
            'data': {
                'labels': list(status_counts.keys()),
                'datasets': [{
                    'data': list(status_counts.values()),
                    'backgroundColor': [
                        '#1cc88a', '#f6c23e', '#e74a3b', '#4e73df'
                    ]
                }]
            }
        }
        
        # Monthly invoices
        monthly_amounts = {'USD': {}, 'AED': {}}
        for invoice in invoices:
            if 'created_at' in invoice and invoice['created_at']:
                month = invoice['created_at'][:7]  # Get YYYY-MM format
                
                usd_amount = invoice.get('price_usd', 0)
                if usd_amount > 0:
                    if month not in monthly_amounts['USD']:
                        monthly_amounts['USD'][month] = 0
                    monthly_amounts['USD'][month] += usd_amount
                
                aed_amount = invoice.get('aed_price', 0)
                if aed_amount > 0:
                    if month not in monthly_amounts['AED']:
                        monthly_amounts['AED'][month] = 0
                    monthly_amounts['AED'][month] += aed_amount
        
        # Sort months
        all_months = set()
        for currency_data in monthly_amounts.values():
            all_months.update(currency_data.keys())
        sorted_months = sorted(all_months)
        
        datasets = []
        for currency, month_data in monthly_amounts.items():
            datasets.append({
                'label': currency,
                'data': [month_data.get(month, 0) for month in sorted_months],
                'backgroundColor': '#4e73df' if currency == 'USD' else '#1cc88a'
            })
        
        chart_data['monthly'] = {
            'type': 'bar',
            'data': {
                'labels': sorted_months,
                'datasets': datasets
            }
        }
        
        data['charts'] = chart_data
    
    elif report_type == 'vessel':
        # Get vessels
        queryset = Vessel.objects.all()
        
        # Apply status filter if provided
        vessel_status = filters.get('vessel_status', [])
        if vessel_status:
            queryset = queryset.filter(status__in=vessel_status)
        
        # Apply vessel type filter if provided
        vessel_type_ids = filters.get('vessel_type', [])
        if vessel_type_ids:
            queryset = queryset.filter(vessel_type_id__in=vessel_type_ids)
        
        # Prepare data
        vessels = list(queryset.values())
        data['items'] = vessels
        
        # Prepare summary
        total_vessels = len(vessels)
        active_vessels = sum(1 for v in vessels if v.get('status') == 'Active')
        maintenance_vessels = sum(1 for v in vessels if v.get('status') == 'In Maintenance')
        inactive_vessels = sum(1 for v in vessels if v.get('status') == 'Inactive')
        
        data['summary'] = [
            {'label': 'Total Vessels', 'value': total_vessels, 'icon': 'ship', 'color': 'primary'},
            {'label': 'Active Vessels', 'value': active_vessels, 'icon': 'check-circle', 'color': 'success'},
            {'label': 'In Maintenance', 'value': maintenance_vessels, 'icon': 'tools', 'color': 'warning'},
            {'label': 'Inactive Vessels', 'value': inactive_vessels, 'icon': 'pause-circle', 'color': 'danger'}
        ]
        
        # Prepare chart data
        chart_data = {}
        
        # Status distribution
        status_counts = {}
        for vessel in vessels:
            status = vessel.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        chart_data['status'] = {
            'type': 'pie',
            'data': {
                'labels': list(status_counts.keys()),
                'datasets': [{
                    'data': list(status_counts.values()),
                    'backgroundColor': [
                        '#1cc88a', '#f6c23e', '#e74a3b'
                    ]
                }]
            }
        }
        
        # Vessel types
        type_counts = {}
        for vessel in vessels:
            vessel_type = vessel.get('vessel_type', 'Unknown')
            type_counts[vessel_type] = type_counts.get(vessel_type, 0) + 1
        
        chart_data['types'] = {
            'type': 'bar',
            'data': {
                'labels': list(type_counts.keys()),
                'datasets': [{
                    'label': 'Vessels by Type',
                    'data': list(type_counts.values()),
                    'backgroundColor': '#4e73df'
                }]
            }
        }
        
        data['charts'] = chart_data
    
    return data
