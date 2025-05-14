from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from django.db.models import Q, Sum, Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import json
from .forms import ContractForm, InvoiceForm
from .models import (
    Contract,
    Invoice,
    Vessel,
    VesselDocument,
    VesselMaintenance,
)


@login_required
def contract_list(request):
    """
    View to display a list of all contracts.

    Retrieves all Contract objects from the database, with optional filtering 
    by state, and passes them to the 'contract_list.html' template.
    Also initializes a blank ContractForm for adding a new contract.

    :param request: The HTTP request object.
    :return: Rendered 'contract_list.html' template with contract data and form.
    """
    # Get state filter from query params
    state_filter = request.GET.get('state')
    
    # Get all contracts ordered by most recent first
    contracts = Contract.objects.all().order_by('-created_at')
    
    # Apply state filter if provided
    if state_filter and state_filter.isdigit():
        contracts = contracts.filter(state=int(state_filter))
    
    # Define contract states for the template
    contract_states = [
        (0, 'Pending'),
        (1, 'Finance'),
        (2, 'Billed')
    ]
    
    # Initialize an empty contract form
    form = ContractForm()
    
    # Prepare context dictionary for template rendering
    context = {
        'contracts': contracts,
        'form': form,
        'contract_states': contract_states,
        'current_state': state_filter,
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
        # Get the contract ID from the URL if present
        contract_id = request.GET.get('contract')
        initial_data = {}
        if contract_id:
            try:
                contract = Contract.objects.get(id=contract_id)
                initial_data['contract'] = contract
            except Contract.DoesNotExist:
                messages.warning(request, 'Selected contract not found')
        
        form = InvoiceForm(initial=initial_data)
    
    context = {
        'form': form,
        'page_title': 'Create New Invoice'
    }
    
    return render(request, 'ShipOps/invoice_edit.html', context)

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
    monthly_data = []
    
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
        
        # Append data with full date for sorting
        monthly_data.append({
            'month': month_name,
            'month_date': month_date.strftime('%Y-%m'),  # Add full date for sorting
            'contract_count': month_contracts,
            'invoice_count': month_invoices,
            'invoice_value': float(month_revenue)  # Ensure it's a float
        })
    
    # Sort monthly data by date
    monthly_data.sort(key=lambda x: x['month_date'])
    
    # Remove the sorting key before sending to template
    for item in monthly_data:
        del item['month_date']
    
    context = {
        'contract_count': contract_count,
        'invoice_count': invoice_count,
        'total_usd': total_usd,
        'total_aed': total_aed,
        'contract_status': contract_status,
        'status_percentages': status_percentages,
        'recent_contracts': recent_contracts,
        'monthly_data': monthly_data,
        'pending_contracts': contract_status['Pending'],
        'finance_contracts': contract_status['Finance'],
        'billed_contracts': contract_status['Billed']
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
        return redirect('vessel_list')


def contract_analytics_view(request):
    # Basic contract counts
    total_contracts = Contract.objects.count()
    total_invoices = Invoice.objects.count()

    # Status distribution
    status_distribution = Contract.objects.values('state').annotate(count=Count('id'))

    # Invoice status distribution
    invoice_status_distribution = Invoice.objects.values('status').annotate(count=Count('id'))
    
    # Get payment statistics from invoices
    total_invoiced_usd = Invoice.objects.aggregate(total=Sum('price_usd'))['total'] or 0
    total_invoiced_aed = Invoice.objects.aggregate(total=Sum('aed_price'))['total'] or 0
    avg_invoice_usd = Invoice.objects.aggregate(avg=Avg('price_usd'))['avg'] or 0
    
    # Contracts with and without invoices
    contracts_with_invoice = Contract.objects.filter(invoice_obj__isnull=False).count()
    contracts_without_invoice = Contract.objects.filter(invoice_obj__isnull=True).count()
    
    # Calculate invoice percentage
    invoice_percentage = 0
    if total_contracts > 0:
        invoice_percentage = (contracts_with_invoice / total_contracts) * 100

    # Expiring contracts (next 30 days)
    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    expiring_soon = Contract.objects.filter(contract_end__range=[today, thirty_days_later]).order_by('contract_end')

    # Overdue invoices
    overdue_invoices = Invoice.objects.filter(
        status=Invoice.STATUS_PENDING, 
        due_date__lt=today
    ).order_by('due_date')
    
    # If no overdue invoices found, check if invoices are being marked as overdue properly
    if not overdue_invoices.exists():
        # Try a broader search - just find invoices with past due dates regardless of status
        overdue_invoices = Invoice.objects.filter(
            due_date__lt=today
        ).order_by('due_date')
        
        # Also update any pending invoices that are past due to STATUS_OVERDUE
        pending_overdue = Invoice.objects.filter(
            status=Invoice.STATUS_PENDING,
            due_date__lt=today
        )
        for invoice in pending_overdue:
            invoice.status = Invoice.STATUS_OVERDUE
            invoice.save()
    else:
        # Update all pending invoices with past due dates to STATUS_OVERDUE
        for invoice in overdue_invoices:
            if invoice.status == Invoice.STATUS_PENDING:
                invoice.status = Invoice.STATUS_OVERDUE
                invoice.save()
    
    # Get all invoices that are past due regardless of status for the table display
    all_past_due_invoices = Invoice.objects.filter(due_date__lt=today).order_by('due_date')
    
    # Update the invoice status distribution after updating statuses
    invoice_status_distribution = Invoice.objects.values('status').annotate(count=Count('id'))

    # Contracts by vessel
    contracts_by_vessel = Contract.objects.values('vessel').annotate(count=Count('id'))

    # Monthly contract counts for the past 12 months
    last_12_months = timezone.now() - timedelta(days=365)
    monthly_contracts = Contract.objects.filter(
        contract_start__gte=last_12_months
    ).values('contract_start__year', 'contract_start__month').annotate(
        count=Count('id')
    ).order_by('contract_start__year', 'contract_start__month')

    # Monthly invoice data
    monthly_invoices = Invoice.objects.filter(
        created_at__gte=last_12_months
    ).values('created_at__year', 'created_at__month').annotate(
        count=Count('id'),
        total_usd=Sum('price_usd')
    ).order_by('created_at__year', 'created_at__month')

    # Convert to chart-friendly format
    months = []
    contract_counts = []
    invoice_counts = []
    invoice_amounts = []
    
    # Create month labels (last 12 months)
    for i in range(12):
        date = timezone.now() - timedelta(days=30 * (11 - i))
        month_name = f"{date.year}-{date.month}"
        months.append(month_name)
        contract_counts.append(0)  # Initialize with zeros
        invoice_counts.append(0)
        invoice_amounts.append(0)
    
    # Fill in actual contract counts
    for item in monthly_contracts:
        month_name = f"{item['contract_start__year']}-{item['contract_start__month']}"
        if month_name in months:
            idx = months.index(month_name)
            contract_counts[idx] = item['count']
    
    # Fill in actual invoice counts and amounts
    for item in monthly_invoices:
        month_name = f"{item['created_at__year']}-{item['created_at__month']}"
        if month_name in months:
            idx = months.index(month_name)
            invoice_counts[idx] = item['count']
            invoice_amounts[idx] = float(item['total_usd'] or 0)

    # For status distribution chart
    status_labels = [item['state'] for item in status_distribution]
    status_counts = [item['count'] for item in status_distribution]
    
    # For invoice status chart
    invoice_status_labels = [item['status'] for item in invoice_status_distribution]
    invoice_status_counts = [item['count'] for item in invoice_status_distribution]
    
    # Ensure we have some data for charts
    if not status_labels:
        status_labels = [0, 1, 2]
        status_counts = [0, 0, 0]
    
    # Convert to JSON safely
    def json_default(obj):
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        return str(obj)
    
    context = {
        'total_contracts': total_contracts,
        'total_invoices': total_invoices,
        'total_invoiced_usd': total_invoiced_usd,
        'total_invoiced_aed': total_invoiced_aed,
        'avg_invoice_usd': avg_invoice_usd,
        'invoice_percentage': round(invoice_percentage, 2),
        'contracts_with_invoice': contracts_with_invoice,
        'contracts_without_invoice': contracts_without_invoice,
        'expiring_soon': expiring_soon,
        'overdue_invoices': all_past_due_invoices,
        'status_distribution': status_distribution,
        'invoice_status_distribution': invoice_status_distribution,
        'contracts_by_vessel': contracts_by_vessel,
        'months_json': json.dumps(months, default=json_default),
        'contract_counts_json': json.dumps(contract_counts, default=json_default),
        'invoice_counts_json': json.dumps(invoice_counts, default=json_default),
        'invoice_amounts_json': json.dumps(invoice_amounts, default=json_default),
        'status_labels_json': json.dumps(status_labels, default=json_default),
        'status_counts_json': json.dumps(status_counts, default=json_default),
        'invoice_status_labels_json': json.dumps(invoice_status_labels, default=json_default),
        'invoice_status_counts_json': json.dumps(invoice_status_counts, default=json_default),
    }

    return render(request, 'ShipOps/contract_analytics.html', context)


@login_required
def invoice_reports_view(request):
    """View for comprehensive invoice reporting and analysis."""
    # Basic invoice metrics
    today = timezone.now().date()
    
    # Get invoice counts by status
    total_invoices = Invoice.objects.count()
    pending_invoices = Invoice.objects.filter(status=Invoice.STATUS_PENDING).count()
    paid_invoices = Invoice.objects.filter(status=Invoice.STATUS_PAID).count()
    overdue_invoices = Invoice.objects.filter(status=Invoice.STATUS_OVERDUE).count()
    cancelled_invoices = Invoice.objects.filter(status=Invoice.STATUS_CANCELLED).count()
    
    # Financial metrics
    total_invoiced_usd = Invoice.objects.aggregate(total=Sum('price_usd'))['total'] or 0
    total_invoiced_aed = Invoice.objects.aggregate(total=Sum('aed_price'))['total'] or 0
    
    # Paid vs Unpaid amounts
    paid_amount_usd = Invoice.objects.filter(status=Invoice.STATUS_PAID).aggregate(total=Sum('price_usd'))['total'] or 0
    unpaid_amount_usd = total_invoiced_usd - paid_amount_usd
    
    # Payment metrics
    avg_days_to_payment = 0
    paid_invoices_with_dates = Invoice.objects.filter(
        status=Invoice.STATUS_PAID, 
        due_date__isnull=False
    )
    
    # Calculate average days to payment for paid invoices
    if paid_invoices_with_dates.exists():
        total_days = 0
        count = 0
        for invoice in paid_invoices_with_dates:
            if invoice.due_date and invoice.created_at:
                # Assuming payment date is when status was changed to PAID
                # For simplicity, using updated_at as proxy for payment date
                payment_delay = (invoice.due_date - invoice.created_at.date()).days
                total_days += payment_delay
                count += 1
        
        if count > 0:
            avg_days_to_payment = total_days / count
    
    # Get all invoices for time-based analysis
    all_invoices = Invoice.objects.all().order_by('created_at')
    
    # Monthly invoice data (last 12 months)
    last_12_months = timezone.now() - timedelta(days=365)
    monthly_invoices = Invoice.objects.filter(
        created_at__gte=last_12_months
    ).values('created_at__year', 'created_at__month').annotate(
        count=Count('id'),
        total_usd=Sum('price_usd'),
        paid_count=Count('id', filter=models.Q(status=Invoice.STATUS_PAID)),
        paid_amount=Sum('price_usd', filter=models.Q(status=Invoice.STATUS_PAID))
    ).order_by('created_at__year', 'created_at__month')
    
    # Create month labels and initialize data arrays
    months = []
    invoice_counts = []
    invoice_amounts = []
    paid_counts = []
    paid_amounts = []
    
    # Create month labels (last 12 months)
    for i in range(12):
        date = timezone.now() - timedelta(days=30 * (11 - i))
        month_name = f"{date.year}-{date.month}"
        months.append(month_name)
        invoice_counts.append(0)
        invoice_amounts.append(0)
        paid_counts.append(0)
        paid_amounts.append(0)
    
    # Fill in actual invoice data
    for item in monthly_invoices:
        month_name = f"{item['created_at__year']}-{item['created_at__month']}"
        if month_name in months:
            idx = months.index(month_name)
            invoice_counts[idx] = item['count']
            invoice_amounts[idx] = float(item['total_usd'] or 0)
            paid_counts[idx] = item['paid_count'] or 0
            paid_amounts[idx] = float(item['paid_amount'] or 0)
    
    # Top contracts by invoice value
    top_invoices = Invoice.objects.order_by('-price_usd')[:10]
    
    # Payment efficiency by month (% of invoices paid)
    payment_efficiency = []
    for i in range(len(months)):
        if invoice_counts[i] > 0:
            efficiency = (paid_counts[i] / invoice_counts[i]) * 100
        else:
            efficiency = 0
        payment_efficiency.append(round(efficiency, 2))
    
    # Convert data to JSON for charts
    def json_default(obj):
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        return str(obj)
    
    context = {
        'total_invoices': total_invoices,
        'pending_invoices': pending_invoices,
        'paid_invoices': paid_invoices,
        'overdue_invoices': overdue_invoices,
        'cancelled_invoices': cancelled_invoices,
        'total_invoiced_usd': total_invoiced_usd,
        'total_invoiced_aed': total_invoiced_aed,
        'paid_amount_usd': paid_amount_usd,
        'unpaid_amount_usd': unpaid_amount_usd,
        'avg_days_to_payment': round(avg_days_to_payment, 1),
        'top_invoices': top_invoices,
        'months_json': json.dumps(months, default=json_default),
        'invoice_counts_json': json.dumps(invoice_counts, default=json_default),
        'invoice_amounts_json': json.dumps(invoice_amounts, default=json_default),
        'paid_counts_json': json.dumps(paid_counts, default=json_default),
        'paid_amounts_json': json.dumps(paid_amounts, default=json_default),
        'payment_efficiency_json': json.dumps(payment_efficiency, default=json_default),
    }
    
    return render(request, 'ShipOps/invoice_reports.html', context)


@login_required
def vessel_performance_view(request):
    """View for vessel performance metrics and analytics."""
    # Get all vessels
    vessels = Vessel.objects.all()
    total_vessels = vessels.count()
    
    # Get status counts
    operational_vessels = vessels.filter(status='operational').count()
    maintenance_vessels = vessels.filter(status='maintenance').count()
    repair_vessels = vessels.filter(status='repair').count()
    docked_vessels = vessels.filter(status='docked').count()
    unavailable_vessels = vessels.filter(status='unavailable').count()
    
    # Calculate fleet availability percentage
    fleet_availability = 0
    if total_vessels > 0:
        fleet_availability = (operational_vessels / total_vessels) * 100
    
    # Get vessel types distribution
    vessel_types = vessels.values('vessel_type').annotate(count=Count('id')).order_by('-count')
    
    # Get maintenance data
    today = timezone.now().date()
    maintenance_records = VesselMaintenance.objects.all()
    total_maintenance_count = maintenance_records.count()
    
    # Maintenance by status
    scheduled_maintenance = maintenance_records.filter(status='scheduled').count()
    in_progress_maintenance = maintenance_records.filter(status='in_progress').count()
    completed_maintenance = maintenance_records.filter(status='completed').count()
    delayed_maintenance = maintenance_records.filter(status='delayed').count()
    
    # Get upcoming maintenance in next 30 days
    thirty_days_later = today + timedelta(days=30)
    upcoming_maintenance = maintenance_records.filter(
        scheduled_date__range=[today, thirty_days_later]
    ).order_by('scheduled_date')
    
    # Calculate maintenance costs
    total_maintenance_cost = maintenance_records.aggregate(
        total=Sum('cost')
    )['total'] or 0
    
    avg_maintenance_cost = 0
    if total_maintenance_count > 0:
        avg_maintenance_cost = total_maintenance_cost / total_maintenance_count
    
    # Get maintenance costs by vessel
    vessel_maintenance_costs = VesselMaintenance.objects.values(
        'vessel__name'
    ).annotate(
        total_cost=Sum('cost'),
        maintenance_count=Count('id')
    ).order_by('-total_cost')[:10]
    
    # Get maintenance costs by month
    last_12_months = timezone.now() - timedelta(days=365)
    monthly_maintenance = VesselMaintenance.objects.filter(
        scheduled_date__gte=last_12_months
    ).values('scheduled_date__year', 'scheduled_date__month').annotate(
        count=Count('id'),
        total_cost=Sum('cost')
    ).order_by('scheduled_date__year', 'scheduled_date__month')
    
    # Create month labels and initialize data arrays
    months = []
    maintenance_counts = []
    maintenance_costs = []
    
    # Create month labels (last 12 months)
    for i in range(12):
        date = timezone.now() - timedelta(days=30 * (11 - i))
        month_name = f"{date.year}-{date.month}"
        months.append(month_name)
        maintenance_counts.append(0)
        maintenance_costs.append(0)
    
    # Fill in actual maintenance data
    for item in monthly_maintenance:
        month_name = f"{item['scheduled_date__year']}-{item['scheduled_date__month']}"
        if month_name in months:
            idx = months.index(month_name)
            maintenance_counts[idx] = item['count']
            maintenance_costs[idx] = float(item['total_cost'] or 0)
    
    # Get vessels with expired or expiring documents
    expiring_documents = VesselDocument.objects.filter(
        expiry_date__range=[today, thirty_days_later]
    ).order_by('expiry_date')
    
    # Get document compliance rate
    total_documents = VesselDocument.objects.count()
    expired_documents = VesselDocument.objects.filter(
        expiry_date__lt=today
    ).count()
    
    document_compliance_rate = 100
    if total_documents > 0:
        document_compliance_rate = ((total_documents - expired_documents) / total_documents) * 100
    
    # Get contract data by vessel
    contracts_by_vessel = Contract.objects.values('vessel').annotate(
        contract_count=Count('id')
    ).order_by('-contract_count')[:10]
    
    # Convert data to JSON for charts
    def json_default(obj):
        if isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        return str(obj)
    
    # Vessel status for pie chart
    status_labels = ['Operational', 'Maintenance', 'Repair', 'Docked', 'Unavailable']
    status_counts = [operational_vessels, maintenance_vessels, repair_vessels, docked_vessels, unavailable_vessels]
    
    # Vessel type data for charts
    vessel_type_labels = [item['vessel_type'] for item in vessel_types]
    vessel_type_counts = [item['count'] for item in vessel_types]
    
    # Maintenance status for charts
    maintenance_status_labels = ['Scheduled', 'In Progress', 'Completed', 'Delayed']
    maintenance_status_counts = [scheduled_maintenance, in_progress_maintenance, completed_maintenance, delayed_maintenance]
    
    # Vessel maintenance cost data
    maintenance_vessel_names = [item['vessel__name'] for item in vessel_maintenance_costs]
    maintenance_vessel_costs = [float(item['total_cost']) for item in vessel_maintenance_costs]
    
    context = {
        'total_vessels': total_vessels,
        'operational_vessels': operational_vessels,
        'maintenance_vessels': maintenance_vessels,
        'repair_vessels': repair_vessels,
        'docked_vessels': docked_vessels,
        'unavailable_vessels': unavailable_vessels,
        'fleet_availability': round(fleet_availability, 2),
        'vessel_types': vessel_types,
        'total_maintenance_count': total_maintenance_count,
        'scheduled_maintenance': scheduled_maintenance,
        'in_progress_maintenance': in_progress_maintenance,
        'completed_maintenance': completed_maintenance,
        'delayed_maintenance': delayed_maintenance,
        'upcoming_maintenance': upcoming_maintenance,
        'total_maintenance_cost': total_maintenance_cost,
        'avg_maintenance_cost': round(avg_maintenance_cost, 2),
        'vessel_maintenance_costs': vessel_maintenance_costs,
        'expiring_documents': expiring_documents,
        'document_compliance_rate': round(document_compliance_rate, 2),
        'contracts_by_vessel': contracts_by_vessel,
        
        # JSON data for charts
        'months_json': json.dumps(months, default=json_default),
        'maintenance_counts_json': json.dumps(maintenance_counts, default=json_default),
        'maintenance_costs_json': json.dumps(maintenance_costs, default=json_default),
        'status_labels_json': json.dumps(status_labels, default=json_default),
        'status_counts_json': json.dumps(status_counts, default=json_default),
        'vessel_type_labels_json': json.dumps(vessel_type_labels, default=json_default),
        'vessel_type_counts_json': json.dumps(vessel_type_counts, default=json_default),
        'maintenance_status_labels_json': json.dumps(maintenance_status_labels, default=json_default),
        'maintenance_status_counts_json': json.dumps(maintenance_status_counts, default=json_default),
        'maintenance_vessel_names_json': json.dumps(maintenance_vessel_names, default=json_default),
        'maintenance_vessel_costs_json': json.dumps(maintenance_vessel_costs, default=json_default),
    }
    
    return render(request, 'ShipOps/vessel_performance.html', context)

@login_required
def maintenance_report_view(request):
    """
    View function for vessel maintenance reports
    """
    # Get maintenance data
    vessels = Vessel.objects.all()
    maintenance_records = VesselMaintenance.objects.all().order_by('-scheduled_date')
    
    # Calculate maintenance statistics
    overdue_tasks = maintenance_records.filter(
        status='delayed',
        scheduled_date__lt=timezone.now().date()
    )
    
    scheduled_tasks = maintenance_records.filter(
        status='scheduled'
    )
    
    completed_tasks = maintenance_records.filter(
        status='completed',
        completion_date__gte=timezone.now().date() - timezone.timedelta(days=30)
    )
    
    pending_tasks = maintenance_records.filter(
        status='in_progress'
    )
    
    # Get upcoming maintenance tasks
    upcoming_maintenance = maintenance_records.filter(
        status__in=['scheduled', 'in_progress'],
        scheduled_date__gte=timezone.now().date()
    ).order_by('scheduled_date')[:10]
    
    # Prepare context for the template
    context = {
        'overdue_tasks_count': overdue_tasks.count(),
        'scheduled_tasks_count': scheduled_tasks.count(),
        'completed_tasks_count': completed_tasks.count(),
        'pending_tasks_count': pending_tasks.count(),
        'due_this_week_count': scheduled_tasks.filter(
            scheduled_date__lte=timezone.now().date() + timezone.timedelta(days=7)
        ).count(),
        'total_scheduled_count': maintenance_records.filter(status='scheduled').count(),
        'maintenance_tasks': upcoming_maintenance,
    }
    
    return render(request, 'ShipOps/reports/report_types/maintenance_report.html', context)
