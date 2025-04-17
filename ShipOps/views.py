from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Contract, Invoice
from .forms import ContractForm, InvoiceForm
from django.db import models
from django.utils import timezone
from django.contrib.auth.decorators import login_required


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
    
    return render(request, 'contract_list.html', context)


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
    
    return render(request, 'invoice_list.html', context)


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
    
    return render(request, 'contract_edit.html', context)


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
    
    return render(request, 'invoice_edit.html', context)

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
    
    return render(request, 'contract_list.html', context)


@login_required
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
    
    return render(request, 'contract_edit.html', context)


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
    
    return render(request, 'contract_detail.html', context)

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
    
    return render(request, 'invoice_list.html', context)


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
    
    return render(request, 'invoice_edit.html', context)


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
    
    return render(request, 'invoice_detail.html', context)


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
    
    if state == 'finance':
        # Set state to indicate sent to finance (assuming state=1 means sent to finance)
        contract.state = 1
        contract.save()
        messages.success(request, f"Contract #{contract.id} for {contract.vessel} sent to Finance Department")
    else:
        # Generic state change handling could be added here
        pass
    
    return redirect("contract_list")


@login_required
def dashboard_home(request):
    """
    Dashboard home page with analytics and overview of the system.
    
    Displays summary statistics, recent contracts, pending invoices,
    and visualizations of key metrics.
    
    :param request: The HTTP request object.
    :return: Rendered 'dashboard.html' template with dashboard data.
    """
    # Get counts for various models
    contract_count = Contract.objects.count()
    invoice_count = Invoice.objects.count()
    
    # Get recent contracts (last 5)
    recent_contracts = Contract.objects.all().order_by('-created_at')[:5]
    
    # Get pending/unbilled contracts
    pending_contracts = Contract.objects.filter(state=0).count()
    finance_contracts = Contract.objects.filter(state=1).count()
    billed_contracts = Contract.objects.filter(state=2).count()
    
    # Calculate total invoice values
    total_usd = Invoice.objects.aggregate(total=models.Sum('price_usd'))['total'] or 0
    total_aed = Invoice.objects.aggregate(total=models.Sum('aed_price'))['total'] or 0
    
    # Get monthly contract counts for the past 6 months
    today = timezone.now()
    six_months_ago = today - timezone.timedelta(days=180)
    # Count all contracts and invoices
    monthly_data = []
    
    for i in range(6):
        month_start = (today - timezone.timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0)
        if i > 0:
            next_month = (today - timezone.timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0)
        else:
            next_month = today + timezone.timedelta(days=31)
            next_month = next_month.replace(day=1, hour=0, minute=0, second=0)
            
        # Get count of contracts for this month
        contract_count = Contract.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        # Get count of invoices for this month
        invoice_count = Invoice.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        # Get sum of invoice values for this month
        invoice_value = Invoice.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month
        ).aggregate(total=models.Sum('price_usd'))['total'] or 0
        
        month_name = month_start.strftime('%b %Y')
        
        monthly_data.append({
            'month': month_name,
            'contract_count': contract_count,
            'invoice_count': invoice_count,
            'invoice_value': invoice_value
        })
    
    # Reverse to show oldest to newest
    monthly_data.reverse()
    
    # Get top charterers by contract count
    top_charterers = Contract.objects.values('charterer').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    # Get top vessels by contract count
    top_vessels = Contract.objects.values('vessel').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    all_contracts = Contract.objects.all().count()
    all_invoices = Invoice.objects.all().count()

    context = {
        'page_title': 'Dashboard',
        'today': today,
        'contract_count': contract_count,
        'invoice_count': invoice_count,
        'recent_contracts': recent_contracts,
        'pending_contracts': pending_contracts,
        'finance_contracts': finance_contracts,
        'billed_contracts': billed_contracts,
        'total_usd': total_usd,
        'total_aed': total_aed,
        'monthly_data': monthly_data,
        'top_charterers': top_charterers,
        'top_vessels': top_vessels,
        "all_contracts":all_contracts,
        "all_invoices":all_invoices
    }
    
    return render(request, 'dashboard.html', context)
