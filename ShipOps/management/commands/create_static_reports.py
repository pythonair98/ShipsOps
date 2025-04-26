from django.core.management.base import BaseCommand
from ShipOps.models import StaticReport

class Command(BaseCommand):
    help = 'Creates predefined static reports'
    
    def handle(self, *args, **options):
        # Define the predefined reports
        reports = [
            # Contract Reports
            {
                'name': 'Contract Status Overview',
                'slug': 'contract-status',
                'description': 'Overview of contracts by status with charts and statistics',
                'report_type': 'contract',
                'generator_function': 'generate_contract_report',
                'chart_type': 'pie',
                'default_filters': {}
            },
            {
                'name': 'Monthly Contract Analysis',
                'slug': 'monthly-contracts',
                'description': 'Analysis of contracts created per month',
                'report_type': 'contract',
                'generator_function': 'generate_contract_report',
                'chart_type': 'bar',
                'default_filters': {'grouping': 'month'}
            },
            {
                'name': 'Contracts by Charterer',
                'slug': 'charterer-contracts',
                'description': 'Breakdown of contracts by charterer',
                'report_type': 'contract',
                'generator_function': 'generate_contract_report',
                'chart_type': 'bar',
                'default_filters': {'grouping': 'charterer'}
            },
            
            # Invoice Reports
            {
                'name': 'Invoice Payment Status',
                'slug': 'invoice-status',
                'description': 'Overview of invoices by payment status',
                'report_type': 'invoice',
                'generator_function': 'generate_invoice_report',
                'chart_type': 'pie',
                'default_filters': {}
            },
            {
                'name': 'USD Invoices',
                'slug': 'usd-invoices',
                'description': 'Analysis of invoices in USD currency',
                'report_type': 'invoice',
                'generator_function': 'generate_invoice_report',
                'chart_type': 'bar',
                'default_filters': {'currency': 'USD'}
            },
            {
                'name': 'AED Invoices',
                'slug': 'aed-invoices',
                'description': 'Analysis of invoices in AED currency',
                'report_type': 'invoice',
                'generator_function': 'generate_invoice_report',
                'chart_type': 'bar',
                'default_filters': {'currency': 'AED'}
            },
            
            # Vessel Reports
            {
                'name': 'Vessel Fleet Overview',
                'slug': 'fleet-overview',
                'description': 'Overview of all vessels in the fleet',
                'report_type': 'vessel',
                'generator_function': 'generate_vessel_report',
                'chart_type': 'pie',
                'default_filters': {}
            },
            {
                'name': 'Vessels by Type',
                'slug': 'vessel-types',
                'description': 'Breakdown of vessels by type',
                'report_type': 'vessel',
                'generator_function': 'generate_vessel_report',
                'chart_type': 'pie',
                'default_filters': {'grouping': 'type'}
            },
            {
                'name': 'Active Vessels',
                'slug': 'active-vessels',
                'description': 'List of all active vessels',
                'report_type': 'vessel',
                'generator_function': 'generate_vessel_report',
                'chart_type': 'bar',
                'default_filters': {'status': 'active'}
            },
            
            # Financial Reports
            {
                'name': 'Monthly Financial Summary',
                'slug': 'monthly-finance',
                'description': 'Monthly summary of financial performance',
                'report_type': 'financial',
                'generator_function': 'generate_financial_report',
                'chart_type': 'bar',
                'default_filters': {'grouping': 'month'}
            },
            {
                'name': 'USD Revenue Analysis',
                'slug': 'usd-revenue',
                'description': 'Analysis of USD revenue over time',
                'report_type': 'financial',
                'generator_function': 'generate_financial_report',
                'chart_type': 'line',
                'default_filters': {'currency': 'USD', 'grouping': 'month'}
            },
            
            # Status Reports
            {
                'name': 'System Status Dashboard',
                'slug': 'system-status',
                'description': 'Overall system status dashboard with contracts, invoices, and vessels',
                'report_type': 'status',
                'generator_function': 'generate_status_report',
                'chart_type': 'doughnut',
                'default_filters': {}
            }
        ]
        
        # Create or update each report
        created_count = 0
        updated_count = 0
        
        for report_data in reports:
            report, created = StaticReport.objects.update_or_create(
                slug=report_data['slug'],
                defaults={
                    'name': report_data['name'],
                    'description': report_data['description'],
                    'report_type': report_data['report_type'],
                    'generator_function': report_data['generator_function'],
                    'chart_type': report_data['chart_type'],
                    'default_filters': report_data['default_filters'],
                    'show_chart': True
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} reports and updated {updated_count} reports.')) 