import random
import os
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from ShipOps.models import (
    Contract, Invoice, Vessel, VesselDocument, VesselMaintenance
)

class Command(BaseCommand):
    help = 'Generates comprehensive dummy data for the Ships Management System'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to generate')
        parser.add_argument('--contracts', type=int, default=20, help='Number of contracts to generate')
        parser.add_argument('--vessels', type=int, default=15, help='Number of vessels to generate')
        
    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive dummy data generation...')
        
        # Initialize Faker
        self.fake = Faker()
        
        # Get parameters
        num_users = options['users']
        num_contracts = options['contracts']
        num_vessels = options['vessels']
        
        with transaction.atomic():
            # Create users
            users = self.create_users(num_users)
            
            # Create vessels and their related records
            vessels = self.create_vessels(num_vessels)
            self.create_vessel_documents(vessels)
            self.create_vessel_maintenance(vessels)
            
            # Create contracts and invoices
            contracts = self.create_contracts(num_contracts, vessels, users)
            invoices = self.create_invoices(contracts)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated comprehensive dummy data!'))
        self.stdout.write(f'Created {num_users} users')
        self.stdout.write(f'Created {num_vessels} vessels with documents and maintenance records')
        self.stdout.write(f'Created {num_contracts} contracts with invoices')

    def create_users(self, count):
        """Create users with basic Django user accounts"""
        users = []
        
        # Always create a superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword',
                first_name='Admin',
                last_name='User'
            )
            users.append(superuser)
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
            count -= 1  # Reduce count since we created a user
        
        # Create regular users
        for i in range(count):
            # Generate user data
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Skip if user already exists
            if User.objects.filter(username=username).exists():
                username = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
                
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password=f'password123',
                first_name=first_name,
                last_name=last_name,
                is_staff=random.random() < 0.3,  # 30% chance of being staff
                date_joined=timezone.now() - timedelta(days=random.randint(1, 365))
            )
            users.append(user)
            
            self.stdout.write(f'Created user: {username}')
        
        self.stdout.write(f'Created a total of {len(users)} users')
        return users

    def create_vessels(self, count):
        """Create vessels with realistic data"""
        vessels = []
        
        vessel_types = ['Cargo Ship', 'Oil Tanker', 'Container Ship', 'Bulk Carrier', 'Chemical Tanker', 
                         'LNG Carrier', 'Fishing Vessel', 'Passenger Ship', 'Ro-Ro Ship', 'Tug Boat']
        
        flags = ['United Arab Emirates', 'Saudi Arabia', 'Panama', 'Marshall Islands', 'Liberia', 
                 'Bahamas', 'Singapore', 'Malta', 'Greece', 'Cyprus', 'China', 'Japan']
        
        statuses = ['operational', 'maintenance', 'repair', 'docked', 'unavailable']
        status_weights = [0.6, 0.15, 0.1, 0.1, 0.05]  # 60% operational, etc.
        
        # Company name generator
        def get_company_name():
            company_types = ['Marine', 'Shipping', 'Maritime', 'Logistics', 'Transport', 'Carriers']
            return f"{self.fake.company()} {random.choice(company_types)}"
        
        for i in range(count):
            # Generate a unique IMO number (format: 7 digits)
            imo_number = f"IMO{random.randint(1000000, 9999999)}"
            while Vessel.objects.filter(imo_number=imo_number).exists():
                imo_number = f"IMO{random.randint(1000000, 9999999)}"
            
            # Generate vessel data
            vessel_type = random.choice(vessel_types)
            status = random.choices(statuses, weights=status_weights, k=1)[0]
            
            # Create vessel with randomly generated specifications
            vessel = Vessel.objects.create(
                name=f"{self.fake.word().capitalize()} {self.fake.word().capitalize()}",
                imo_number=imo_number,
                vessel_type=vessel_type,
                built_year=random.randint(1990, 2022),
                flag=random.choice(flags),
                gross_tonnage=random.uniform(5000, 150000),
                net_tonnage=random.uniform(3000, 100000),
                length_overall=random.uniform(50, 300),
                breadth=random.uniform(10, 50),
                draft=random.uniform(5, 20),
                status=status,
                owner=get_company_name(),
                operator=get_company_name() if random.random() < 0.3 else "",  # 30% chance of different operator
                created_at=timezone.now() - timedelta(days=random.randint(30, 730))  # between 1 month and 2 years old
            )
            vessels.append(vessel)
            
            self.stdout.write(f'Created vessel: {vessel.name} (IMO: {vessel.imo_number})')
        
        self.stdout.write(f'Created a total of {len(vessels)} vessels')
        return vessels

    def create_vessel_documents(self, vessels):
        """Create documents for vessels"""
        documents = []
        
        document_types = [
            'registration', 'insurance', 'classification', 'safety', 'inspection', 'other'
        ]
        
        document_titles = {
            'registration': ['Registration Certificate', 'Certificate of Registry', 'Flag State Registration'],
            'insurance': ['Hull Insurance', 'P&I Insurance', 'Cargo Insurance', 'War Risk Insurance'],
            'classification': ['Class Certificate', 'Classification Society Certificate', 'Tonnage Certificate'],
            'safety': ['Safety Management Certificate', 'Safety Construction Certificate', 'Safety Equipment Certificate'],
            'inspection': ['Port State Inspection', 'Annual Survey Report', 'Condition Survey Report'],
            'other': ['Crew List', 'Minimum Safe Manning Document', 'Ship Security Certificate', 'Load Line Certificate']
        }
        
        for vessel in vessels:
            # Each vessel will have 2-5 documents
            num_docs = random.randint(2, 5)
            used_types = set()
            
            for _ in range(num_docs):
                # Choose a document type, preferring unused types first
                available_types = [t for t in document_types if t not in used_types]
                if not available_types:
                    available_types = document_types
                    
                doc_type = random.choice(available_types)
                used_types.add(doc_type)
                
                # Choose a title based on the document type
                title = random.choice(document_titles[doc_type])
                
                # For documents normally requiring renewal, set an expiry date
                needs_renewal = doc_type in ['registration', 'insurance', 'classification', 'safety']
                
                # Set issue date between vessel creation and now
                days_since_vessel_creation = (timezone.now() - vessel.created_at).days
                issue_date = vessel.created_at.date() + timedelta(days=random.randint(1, max(1, days_since_vessel_creation)))
                
                # Set expiry date for documents that need renewal
                if needs_renewal:
                    # Documents typically valid for 1-5 years
                    expiry_date = issue_date + timedelta(days=random.randint(365, 365 * 5))
                else:
                    expiry_date = None
                
                # Create the document
                doc = VesselDocument.objects.create(
                    vessel=vessel,
                    document_type=doc_type,
                    title=title,
                    file=f"dummy_vessel_doc_{vessel.id}_{doc_type}.pdf",  # dummy filename
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    notes=self.fake.paragraph() if random.random() < 0.3 else "",  # 30% chance of having notes
                    uploaded_at=timezone.now() - timedelta(days=random.randint(1, 180))  # uploaded within the last 6 months
                )
                documents.append(doc)
        
        self.stdout.write(f'Created {len(documents)} vessel documents')
        return documents

    def create_vessel_maintenance(self, vessels):
        """Create maintenance records for vessels"""
        maintenance_records = []
        
        maintenance_types = [
            'Engine Overhaul', 'Hull Inspection', 'Propeller Maintenance', 
            'Electrical System Check', 'Navigation Equipment Calibration',
            'Safety Equipment Inspection', 'Ballast Tank Cleaning',
            'Dry Docking', 'Annual Survey', 'Emergency Repair'
        ]
        
        statuses = ['scheduled', 'in_progress', 'completed', 'delayed', 'cancelled']
        status_weights = [0.3, 0.2, 0.3, 0.15, 0.05]  # 30% scheduled, 20% in progress, etc.
        
        vendors = [
            'Maritime Services Ltd.', 'Ocean Tech Systems', 'ShipFix Engineering',
            'Nautical Repairs Co.', 'MarineWorks International', 'SeaWorthy Solutions',
            'AquaFix Marine', 'Offshore Maintenance Group', 'Harbor Technical Services'
        ]
        
        for vessel in vessels:
            # Each vessel will have 1-3 maintenance records
            num_records = random.randint(1, 3)
            
            for _ in range(num_records):
                maintenance_type = random.choice(maintenance_types)
                status = random.choices(statuses, weights=status_weights, k=1)[0]
                
                # Set dates based on status
                now = timezone.now().date()
                
                # Scheduled date can be in the past for completed/in progress/delayed,
                # or in the future for scheduled
                if status in ['completed', 'in_progress', 'delayed']:
                    scheduled_date = now - timedelta(days=random.randint(1, 180))
                else:
                    scheduled_date = now + timedelta(days=random.randint(1, 180))
                
                # Set completion date only for completed maintenance
                if status == 'completed':
                    completion_date = scheduled_date + timedelta(days=random.randint(1, 30))
                else:
                    completion_date = None
                
                # Set cost (higher for completed maintenance)
                if status == 'completed':
                    cost = random.uniform(5000, 100000)
                else:
                    cost = random.uniform(1000, 80000) if random.random() < 0.7 else None  # 30% chance of no cost estimate yet
                
                # Create the maintenance record
                maintenance = VesselMaintenance.objects.create(
                    vessel=vessel,
                    maintenance_type=maintenance_type,
                    description=self.fake.paragraph(),
                    scheduled_date=scheduled_date,
                    completion_date=completion_date,
                    status=status,
                    cost=cost,
                    vendor=random.choice(vendors) if random.random() < 0.8 else "",  # 80% chance of having a vendor
                    notes=self.fake.paragraph() if random.random() < 0.4 else "",  # 40% chance of having notes
                    created_at=timezone.now() - timedelta(days=random.randint(1, 365))  # created within the last year
                )
                maintenance_records.append(maintenance)
                
                # If the vessel has active maintenance, update its status accordingly
                if status in ['in_progress', 'scheduled'] and vessel.status != 'maintenance':
                    vessel.status = 'maintenance'
                    vessel.save()
        
        self.stdout.write(f'Created {len(maintenance_records)} vessel maintenance records')
        return maintenance_records

    def create_contracts(self, count, vessels, users):
        """Create shipping contracts with realistic data"""
        contracts = []
        
        charterers = [
            'Global Shipping Corp.', 'OceanTrade International', 'EastWest Logistics',
            'Pacific Cargo Lines', 'Continental Freight', 'SeaWay Transport',
            'UAE Maritime Solutions', 'Gulf Carriers Ltd.', 'Middle East Shipping Co.',
            'Arabian Logistics Group', 'Al Khalij Transport', 'Al Bahar Shipping'
        ]
        
        owners = [
            'Vessel Holdings LLC', 'Maritime Assets Group', 'Ocean Fleet Management',
            'Gulf Maritime Partners', 'Nautical Ownership Co.', 'SeaFleet Capital',
            'Al Manakh Marine', 'Emirates Vessel Solutions', 'Abu Dhabi Maritime Asset Corp.',
            'Sharjah Ships LLC', 'Dubai Maritime Group', 'Al Ain Maritime Holdings'
        ]
        
        charter_party_forms = [
            'BIMCO Standard', 'NYPE 93', 'ASBATIME', 'BALTIME', 'SHELLTIME',
            'GENCON', 'ASBATANKVOY', 'INTERTANKVOY', 'BPTime', 'ShellVoy'
        ]
        
        cargoes = [
            'Crude Oil', 'Petroleum Products', 'Chemical Products', 'LNG',
            'Bulk Grain', 'Coal', 'Iron Ore', 'Containers', 'General Cargo',
            'Automobiles', 'Livestock', 'Steel Products', 'Timber'
        ]
        
        ports = [
            'Jebel Ali, UAE', 'Khalifa Port, UAE', 'Fujairah Port, UAE',
            'Dammam, Saudi Arabia', 'Jeddah Islamic Port, Saudi Arabia',
            'Doha Port, Qatar', 'Kuwait Port, Kuwait', 'Salalah, Oman',
            'Singapore', 'Rotterdam, Netherlands', 'Shanghai, China', 'Antwerp, Belgium',
            'Hamburg, Germany', 'Busan, South Korea', 'New York, USA'
        ]
        
        # Contract states: 0 = Pending, 1 = Finance, 2 = Billed
        states = [0, 1, 2]
        state_weights = [0.3, 0.4, 0.3]  # 30% Pending, 40% Finance, 30% Billed
        
        for i in range(count):
            # Select a random vessel
            vessel = random.choice(vessels)
            
            # Generate contract dates
            now = timezone.now()
            created_at = now - timedelta(days=random.randint(1, 365))  # within the last year
            contract_start = created_at + timedelta(days=random.randint(7, 30))  # starting 1-4 weeks after creation
            contract_duration = random.randint(30, 180)  # 1-6 months duration
            contract_end = contract_start + timedelta(days=contract_duration)
            
            # Generate laytime (usually 24-72 hours)
            laytime_hours = random.choice([24, 36, 48, 72, 96])
            
            # Generate demurrage rate (cost per day for delays)
            demurrage_rate = random.randint(5000, 20000)
            
            # Determine contract state
            state = random.choices(states, weights=state_weights, k=1)[0]
            
            # Create the contract
            contract = Contract.objects.create(
                charter_party_dated=created_at,
                charterer=random.choice(charterers),
                owner=random.choice(owners),
                charter_party_form=random.choice(charter_party_forms),
                vessel=vessel.name,
                charter_party_speed=f"{random.randint(10, 20)} knots",
                last_three_cargoes=", ".join(random.sample(cargoes, 3)),
                cargo=random.choice(cargoes),
                quantity=f"{random.randint(10000, 100000)} MT",
                heating=f"{random.randint(40, 60)}°C" if random.random() < 0.4 else "N/A",
                load_port=random.choice(ports),
                laycan=f"{contract_start.strftime('%d %b %Y')} - {(contract_start + timedelta(days=5)).strftime('%d %b %Y')}",
                discharge_port=random.choice(ports),
                freight=f"USD {random.randint(200000, 2000000)}",
                demurrage=f"USD {demurrage_rate} per day",
                laytime=f"{laytime_hours} hours SHINC",
                payment_terms=f"{random.choice(['100', '90', '80'])}% upon completion, {random.choice(['0', '10', '20'])}% after discharge",
                payment_to=f"Bank Account: {random.randint(10000000, 99999999)}",
                brokers=f"{self.fake.company()} Brokers",
                commission=f"{random.randint(1, 5)}%",
                state=state,
                contract_start=contract_start,
                contract_end=contract_end,
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(1, 30))  # last updated 1-30 days after creation
            )
            contracts.append(contract)
            
            self.stdout.write(f'Created contract #{contract.id} for vessel {contract.vessel} (State: {state})')
        
        self.stdout.write(f'Created a total of {len(contracts)} contracts')
        return contracts
    
    def create_invoices(self, contracts):
        """Create invoices for contracts"""
        invoices = []
        
        # Only contracts in Finance (1) or Billed (2) state should have invoices
        eligible_contracts = [contract for contract in contracts if contract.state in [1, 2]]
        
        # Helper function to convert number to words (simplified)
        def num_to_words(num):
            # This is a simplified version for demonstration
            units = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
            teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
            tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
            thousands = ['', 'Thousand', 'Million', 'Billion']
            
            if num < 10:
                return units[num]
            elif num < 20:
                return teens[num - 10]
            elif num < 100:
                return tens[num // 10] + (' ' + units[num % 10] if num % 10 != 0 else '')
            elif num < 1000:
                return units[num // 100] + ' Hundred' + (' ' + num_to_words(num % 100) if num % 100 != 0 else '')
            
            for i in range(3, 0, -1):
                if num >= 10**(i*3):
                    return num_to_words(num // 10**(i*3)) + ' ' + thousands[i] + (' ' + num_to_words(num % 10**(i*3)) if num % 10**(i*3) != 0 else '')
            
            return num_to_words(num)
            
        for contract in eligible_contracts:
            # Extract the freight amount from the contract
            try:
                freight_str = contract.freight.replace('USD', '').replace(',', '').strip()
                price_usd = float(freight_str) if freight_str.isdigit() else random.randint(200000, 2000000)
            except (ValueError, AttributeError):
                price_usd = random.randint(200000, 2000000)
            
            # Convert USD to AED (assuming 1 USD = 3.67 AED)
            aed_price = price_usd * 3.67
            
            # Set due date based on contract dates
            if contract.contract_end:
                due_date = contract.contract_end.date() + timedelta(days=random.randint(7, 30))  # due 1-4 weeks after contract end
            else:
                due_date = timezone.now().date() + timedelta(days=random.randint(7, 30))
            
            # Set status based on contract state and due date
            if contract.state == 2:  # Billed
                status = Invoice.STATUS_PAID
            elif due_date < timezone.now().date():
                status = Invoice.STATUS_OVERDUE
            else:
                status = Invoice.STATUS_PENDING
            
            # Create the invoice
            invoice = Invoice.objects.create(
                contract=contract,
                price_usd=price_usd,
                price_usd_in_word=f"{num_to_words(int(price_usd))} US Dollars",
                aed_price=aed_price,
                aed_price_in_word=f"{num_to_words(int(aed_price))} UAE Dirhams",
                status=status,
                due_date=due_date,
                notes=self.fake.paragraph() if random.random() < 0.3 else "",  # 30% chance of having notes
                created_at=contract.created_at + timedelta(days=random.randint(1, 5))  # created 1-5 days after contract
            )
            invoices.append(invoice)
            
            self.stdout.write(f'Created invoice #{invoice.id} for contract #{contract.id} (Status: {invoice.get_status_display()})')
        
        self.stdout.write(f'Created a total of {len(invoices)} invoices')
        return invoices 