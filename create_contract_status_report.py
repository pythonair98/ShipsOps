import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShipsManagment.settings')
django.setup()

# Import necessary models
from django.contrib.auth.models import User
from ShipOps.models import ReportTemplate

def create_contract_status_distribution_report():
    """
    Creates a Contract Status Distribution report template
    """
    # Get an admin user (use the first admin user found)
    try:
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            print("No admin user found. Please create an admin user first.")
            return
    except Exception as e:
        print(f"Error finding admin user: {e}")
        return
    
    # Define the report template configuration
    report_config = {
        'name': 'Contract Status Distribution',
        'description': 'Shows distribution of contracts by state (Pending, Finance, Billed). Visualized using pie charts and summary metrics. Helps track contract pipeline and identify bottlenecks.',
        'report_type': 'contract',
        'created_by': admin_user,
        'is_public': True,
        'configuration': {
            'fields': ['id', 'charterer', 'vessel', 'state', 'created_at'],
            'filters': {
                'date_range': True,
                'state': True,
                'charterer': True,
                'vessel': True
            },
            'grouping': 'state',
            'charts': ['status_pie', 'status_bar'],
            'display_options': {
                'show_summary': True,
                'show_charts': True,
                'show_details': True
            }
        }
    }
    
    # Check if report already exists
    existing_report = ReportTemplate.objects.filter(
        name=report_config['name'], 
        report_type=report_config['report_type']
    ).first()
    
    if existing_report:
        print(f"Report template '{report_config['name']}' already exists. Updating configuration...")
        # Update existing template
        existing_report.description = report_config['description']
        existing_report.is_public = report_config['is_public']
        existing_report.configuration = report_config['configuration']
        existing_report.save()
        print(f"Report template updated successfully (ID: {existing_report.id})")
        return existing_report
    else:
        # Create new template
        template = ReportTemplate(
            name=report_config['name'],
            description=report_config['description'],
            report_type=report_config['report_type'],
            created_by=report_config['created_by'],
            is_public=report_config['is_public'],
            configuration=report_config['configuration']
        )
        template.save()
        print(f"Report template created successfully (ID: {template.id})")
        return template

if __name__ == "__main__":
    create_contract_status_distribution_report() 