import random
import os
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from ShipOps.models import (
    Contract, Invoice, Vessel, VesselDocument, VesselMaintenance,
    ReportTemplate, SavedReport, Dashboard, AnalyticsLog, Contact
)
from ShipsAuth.models import (
    UserProfile, UserRole, Occupation, Profile, SystemPages, Permission
)

class Command(BaseCommand):
    help = 'Generates comprehensive dummy data for the Ships Management System'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to generate')
        parser.add_argument('--contracts', type=int, default=20, help='Number of contracts to generate')
        parser.add_argument('--vessels', type=int, default=15, help='Number of vessels to generate')
        parser.add_argument('--reports', type=int, default=10, help='Number of reports to generate')
        parser.add_argument('--dashboards', type=int, default=5, help='Number of dashboards to generate')
        
    def handle(self, *args, **options):
        self.stdout.write('Starting comprehensive dummy data generation...')
        
        # Initialize Faker
        self.fake = Faker()
        
        # Get parameters
        num_users = options['users']
        num_contracts = options['contracts']
        num_vessels = options['vessels']
        num_reports = options['reports']
        num_dashboards = options['dashboards']
        
        with transaction.atomic():
            # Create system models first
            self.create_roles()
            self.create_occupations()
            self.create_system_pages()
            
            # Create users and their profiles
            users = self.create_users(num_users)
            
            # Create vessels and their related records
            vessels = self.create_vessels(num_vessels)
            self.create_vessel_documents(vessels)
            self.create_vessel_maintenance(vessels)
            
            # Create contracts and invoices
            contracts = self.create_contracts(num_contracts, vessels, users)
            invoices = self.create_invoices(contracts)
            
            # Create reporting and analytics
            report_templates = self.create_report_templates(num_reports // 2, users)
            saved_reports = self.create_saved_reports(num_reports, report_templates, users)
            dashboards = self.create_dashboards(num_dashboards, users)
            analytics_logs = self.create_analytics_logs(users, saved_reports, dashboards)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated comprehensive dummy data!'))
        self.stdout.write(f'Created {num_users} users')
        self.stdout.write(f'Created {num_vessels} vessels with documents and maintenance records')
        self.stdout.write(f'Created {num_contracts} contracts with invoices')
        self.stdout.write(f'Created {len(report_templates)} report templates and {len(saved_reports)} saved reports')
        self.stdout.write(f'Created {len(dashboards)} dashboards')
        self.stdout.write(f'Created {len(analytics_logs)} analytics log entries')

    def create_roles(self):
        """Create user roles for ShipOps"""
        roles = [
            ('admin', 'Administrator with full system access'),
            ('finance', 'Finance department with invoice management capabilities'),
            ('manager', 'Management staff with oversight permissions'),
            ('operations', 'Operations staff with contract management capabilities'),
            ('viewer', 'Read-only access to system data'),
        ]
        
        created_roles = []
        for role_name, role_desc in roles:
            role, created = UserRole.objects.get_or_create(
                name=role_name,
                defaults={'description': role_desc}
            )
            created_roles.append(role)
        
        self.stdout.write(f'Created {len(created_roles)} user roles')
        return created_roles

    def create_occupations(self):
        """Create occupations for ShipsAuth"""
        occupations = [
            ('مدير النظام', 'System Administrator', 1),
            ('مدير مالي', 'Financial Manager', 2),
            ('مدير العمليات', 'Operations Manager', 3),
            ('موظف مالي', 'Financial Staff', 4),
            ('موظف عمليات', 'Operations Staff', 5),
            ('مستخدم', 'Regular User', 6),
            ('ضيف', 'Guest User', 7),
        ]
        
        created_occupations = []
        for ar_name, en_name, power in occupations:
            # Check if occupation with this power already exists
            existing = Occupation.objects.filter(power=power).first()
            if existing:
                self.stdout.write(f"Occupation with power {power} already exists: {existing.en_name}")
                created_occupations.append(existing)
                continue
                
            # Check if occupation with this name already exists
            existing_ar = Occupation.objects.filter(ar_name=ar_name).first()
            existing_en = Occupation.objects.filter(en_name=en_name).first()
            
            if existing_ar or existing_en:
                self.stdout.write(f"Occupation with name {en_name} already exists")
                created_occupations.append(existing_ar or existing_en)
                continue
            
            # Create new occupation
            try:
                occupation = Occupation.objects.create(
                    ar_name=ar_name,
                    en_name=en_name,
                    power=power
                )
                created_occupations.append(occupation)
                self.stdout.write(f"Created occupation: {en_name} (Power: {power})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating occupation {en_name}: {e}"))
        
        self.stdout.write(f'Created/found {len(created_occupations)} occupations')
        return created_occupations

    def create_system_pages(self):
        """Create system pages and permissions for ShipsAuth"""
        pages = [
            ('dashboard', 'Dashboard', True, None),
            ('contracts', 'Contracts', True, None),
            ('invoices', 'Invoices', True, None),
            ('vessels', 'Vessels', True, None),
            ('reports', 'Reports', True, None),
            ('users', 'User Management', True, None),
            ('settings', 'Settings', True, None),
            
            # Subpages
            ('contract_new', 'New Contract', False, 'contracts'),
            ('contract_edit', 'Edit Contract', False, 'contracts'),
            ('invoice_new', 'New Invoice', False, 'invoices'),
            ('invoice_edit', 'Edit Invoice', False, 'invoices'),
            ('vessel_new', 'New Vessel', False, 'vessels'),
            ('vessel_edit', 'Edit Vessel', False, 'vessels'),
            ('report_new', 'Create Report', False, 'reports'),
            ('report_view', 'View Reports', False, 'reports'),
        ]
        
        # Create or get pages
        page_objects = {}
        
        # First create all top-level pages
        for endpoint, name, is_nav, parent in pages:
            if parent is None:
                try:
                    page = SystemPages.objects.filter(endpoint=endpoint).first()
                    if page:
                        self.stdout.write(f"Page {endpoint} already exists")
                    else:
                        page = SystemPages.objects.create(
                            endpoint=endpoint,
                            rendered_name=name,
                            is_nav_item=is_nav,
                            has_submenu=False
                        )
                        self.stdout.write(f"Created page: {name} (endpoint: {endpoint})")
                    
                    page_objects[endpoint] = page
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating page {endpoint}: {e}"))
        
        # Then create subpages with correct parent references
        for endpoint, name, is_nav, parent in pages:
            if parent is not None and parent in page_objects:
                try:
                    page = SystemPages.objects.filter(endpoint=endpoint).first()
                    if page:
                        self.stdout.write(f"Subpage {endpoint} already exists")
                    else:
                        page = SystemPages.objects.create(
                            endpoint=endpoint,
                            rendered_name=name,
                            is_nav_item=is_nav,
                            has_submenu=False,
                            parent=page_objects[parent]
                        )
                        self.stdout.write(f"Created subpage: {name} (endpoint: {endpoint})")
                    
                    # Update parent to show it has submenus
                    parent_page = page_objects[parent]
                    if parent_page and not parent_page.has_submenu:
                        parent_page.has_submenu = True
                        parent_page.save()
                        self.stdout.write(f"Updated parent page {parent_page.endpoint} to show it has submenus")
                    
                    page_objects[endpoint] = page
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating subpage {endpoint}: {e}"))
        
        # Assign permissions based on occupation power
        permission_count = 0
        try:
            occupations = Occupation.objects.all().order_by('power')
            for occupation in occupations:
                for endpoint, page in page_objects.items():
                    if page is None:
                        continue
                        
                    # Check if permission already exists
                    if Permission.objects.filter(occupation=occupation, page=page).exists():
                        continue
                        
                    # Admin gets all permissions
                    if occupation.power == 1:
                        Permission.objects.create(
                            occupation=occupation,
                            page=page
                        )
                        permission_count += 1
                    # Financial staff get dashboard, contracts, invoices
                    elif occupation.power in [2, 4] and endpoint in ['dashboard', 'contracts', 'invoices', 'reports', 'contract_view', 'invoice_new', 'invoice_edit']:
                        Permission.objects.create(
                            occupation=occupation,
                            page=page
                        )
                        permission_count += 1
                    # Operations staff get dashboard, contracts, vessels
                    elif occupation.power in [3, 5] and endpoint in ['dashboard', 'contracts', 'vessels', 'reports', 'contract_new', 'contract_edit', 'vessel_view']:
                        Permission.objects.create(
                            occupation=occupation,
                            page=page
                        )
                        permission_count += 1
                    # Regular users get dashboard and view-only access
                    elif occupation.power == 6 and endpoint in ['dashboard', 'contracts', 'vessels', 'reports', 'report_view']:
                        Permission.objects.create(
                            occupation=occupation,
                            page=page
                        )
                        permission_count += 1
                    # Guests get only dashboard
                    elif occupation.power == 7 and endpoint in ['dashboard']:
                        Permission.objects.create(
                            occupation=occupation,
                            page=page
                        )
                        permission_count += 1
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating permissions: {e}"))
        
        self.stdout.write(f'Created {len(page_objects)} system pages with {permission_count} permissions')
        return page_objects

    def create_users(self, count):
        """Create users with both ShipsAuth and ShipOps profiles"""
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
            
            # Create ShipsAuth profile for superuser
            admin_occupation = Occupation.objects.filter(power=1).first()
            if admin_occupation:
                Profile.objects.create(
                    user_obj=superuser,
                    occupation=admin_occupation,
                    token='admin_token',
                    profile_image='admin.jpg'
                )
            
            # Create ShipOps profile for superuser
            admin_role = UserRole.objects.get(name='admin')
            UserProfile.objects.create(
                user=superuser,
                role=admin_role,
                department='Management',
                can_view_contracts=True,
                can_edit_contracts=True,
                can_view_invoices=True,
                can_edit_invoices=True
            )
            
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
            count -= 1  # Reduce count since we created a user
        
        # Create regular users
        roles = list(UserRole.objects.all())
        occupations = list(Occupation.objects.all())
        departments = ['Finance', 'Operations', 'Management', 'IT', 'HR', 'Sales', 'Support']
        
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
            
            # Create ShipsAuth profile
            occupation = random.choice(occupations)
            Profile.objects.create(
                user_obj=user,
                occupation=occupation,
                token=f'token_{username}',
                profile_image=f'profile_{i+1}.jpg' if random.random() < 0.7 else None
            )
            
            # Match role to occupation
            if occupation.power == 1:
                role = next((r for r in roles if r.name == 'admin'), roles[0])
            elif occupation.power in [2, 4]:
                role = next((r for r in roles if r.name == 'finance'), roles[0])
            elif occupation.power in [3, 5]:
                role = next((r for r in roles if r.name == 'operations'), roles[0])
            elif occupation.power == 6:
                role = next((r for r in roles if r.name == 'viewer'), roles[0])
            else:
                role = random.choice(roles)
            
            # Assign appropriate department
            if occupation.power in [2, 4]:
                department = 'Finance'
            elif occupation.power in [3, 5]:
                department = 'Operations'
            elif occupation.power == 1:
                department = 'Management'
            else:
                department = random.choice(departments)
            
            # Create ShipOps profile with permissions based on role
            UserProfile.objects.create(
                user=user,
                role=role,
                department=department,
                can_view_contracts=role.name in ['admin', 'manager', 'finance', 'operations', 'viewer'],
                can_edit_contracts=role.name in ['admin', 'manager', 'operations'],
                can_view_invoices=role.name in ['admin', 'manager', 'finance', 'operations'],
                can_edit_invoices=role.name in ['admin', 'manager', 'finance']
            )
            
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

    def create_report_templates(self, count, users):
        """Create report templates for reporting system"""
        templates = []
        
        report_types = ['contract', 'invoice', 'vessel', 'maintenance', 'financial', 'custom']
        
        # Sample configurations for different report types
        template_configs = {
            'contract': {
                'fields': ['id', 'vessel', 'charterer', 'owner', 'cargo', 'load_port', 'discharge_port', 'contract_start', 'contract_end', 'state'],
                'filters': ['vessel', 'charterer', 'date_range', 'state'],
                'charts': ['vessel_distribution', 'monthly_contracts', 'cargo_distribution'],
                'groupBy': ['charterer', 'vessel', 'month'],
                'sortBy': 'contract_start'
            },
            'invoice': {
                'fields': ['id', 'contract', 'price_usd', 'aed_price', 'status', 'due_date', 'created_at'],
                'filters': ['status', 'date_range', 'price_range'],
                'charts': ['status_distribution', 'monthly_revenue', 'currency_comparison'],
                'groupBy': ['status', 'month', 'contract'],
                'sortBy': 'due_date'
            },
            'vessel': {
                'fields': ['name', 'imo_number', 'vessel_type', 'flag', 'status', 'owner', 'gross_tonnage'],
                'filters': ['vessel_type', 'status', 'flag'],
                'charts': ['status_distribution', 'type_distribution', 'age_distribution'],
                'groupBy': ['vessel_type', 'status', 'flag'],
                'sortBy': 'name'
            },
            'maintenance': {
                'fields': ['vessel', 'maintenance_type', 'scheduled_date', 'completion_date', 'status', 'cost', 'vendor'],
                'filters': ['vessel', 'status', 'date_range'],
                'charts': ['status_distribution', 'cost_by_vessel', 'maintenance_timeline'],
                'groupBy': ['vessel', 'maintenance_type', 'status'],
                'sortBy': 'scheduled_date'
            },
            'financial': {
                'fields': ['invoice_id', 'contract_id', 'price_usd', 'aed_price', 'status', 'due_date', 'charterer', 'owner'],
                'filters': ['date_range', 'charterer', 'status'],
                'charts': ['monthly_revenue', 'status_distribution', 'charterer_distribution'],
                'groupBy': ['month', 'charterer', 'status'],
                'sortBy': 'price_usd'
            },
            'custom': {
                'fields': ['contract_id', 'vessel', 'charterer', 'invoice_id', 'price_usd', 'aed_price', 'status'],
                'filters': ['vessel', 'charterer', 'date_range', 'status'],
                'charts': ['charterer_revenue', 'vessel_revenue', 'monthly_trend'],
                'groupBy': ['vessel', 'charterer', 'month', 'status'],
                'sortBy': 'price_usd'
            }
        }
        
        # Create templates
        for i in range(count):
            # Choose a report type and user
            report_type = random.choice(report_types)
            created_by = random.choice(users)
            
            # Create a template with appropriate configuration
            template = ReportTemplate.objects.create(
                name=f"{report_type.capitalize()} Analysis Report" if i == 0 else f"{self.fake.word().capitalize()} {report_type.capitalize()} Report",
                description=self.fake.paragraph() if random.random() < 0.7 else "",  # 70% chance of having a description
                report_type=report_type,
                created_by=created_by,
                is_public=random.random() < 0.6,  # 60% chance of being public
                created_at=timezone.now() - timedelta(days=random.randint(1, 180)),  # created within the last 6 months
                configuration=template_configs[report_type]
            )
            templates.append(template)
            
            self.stdout.write(f'Created report template: {template.name} (Type: {report_type})')
        
        self.stdout.write(f'Created a total of {len(templates)} report templates')
        return templates
    
    def create_saved_reports(self, count, templates, users):
        """Create saved reports based on templates"""
        reports = []
        
        # Ensure we have templates; if not, create one
        if not templates:
            templates = self.create_report_templates(1, users)
        
        # Sample report data structures for different report types
        sample_data = {
            'contract': {
                'summary': {
                    'total_contracts': random.randint(10, 100),
                    'active_contracts': random.randint(5, 50),
                    'completed_contracts': random.randint(5, 50),
                    'average_duration': random.randint(30, 120)
                },
                'chart_data': {
                    'vessel_distribution': [
                        {'name': 'Vessel 1', 'count': random.randint(1, 10)},
                        {'name': 'Vessel 2', 'count': random.randint(1, 10)},
                        {'name': 'Vessel 3', 'count': random.randint(1, 10)}
                    ],
                    'monthly_contracts': [
                        {'month': 'Jan', 'count': random.randint(1, 20)},
                        {'month': 'Feb', 'count': random.randint(1, 20)},
                        {'month': 'Mar', 'count': random.randint(1, 20)}
                    ]
                },
                'results': [
                    {'id': 1, 'vessel': 'Vessel 1', 'charterer': 'Company A', 'cargo': 'Crude Oil', 'state': 'Completed'},
                    {'id': 2, 'vessel': 'Vessel 2', 'charterer': 'Company B', 'cargo': 'LNG', 'state': 'Active'}
                ]
            },
            'invoice': {
                'summary': {
                    'total_invoices': random.randint(10, 100),
                    'paid_invoices': random.randint(5, 50),
                    'pending_invoices': random.randint(5, 50),
                    'total_revenue': random.randint(500000, 5000000)
                },
                'chart_data': {
                    'status_distribution': [
                        {'status': 'Paid', 'count': random.randint(5, 50)},
                        {'status': 'Pending', 'count': random.randint(5, 50)},
                        {'status': 'Overdue', 'count': random.randint(1, 10)}
                    ],
                    'monthly_revenue': [
                        {'month': 'Jan', 'revenue': random.randint(100000, 1000000)},
                        {'month': 'Feb', 'revenue': random.randint(100000, 1000000)},
                        {'month': 'Mar', 'revenue': random.randint(100000, 1000000)}
                    ]
                },
                'results': [
                    {'id': 1, 'contract': 1, 'price_usd': 250000, 'status': 'Paid', 'due_date': '2023-01-15'},
                    {'id': 2, 'contract': 2, 'price_usd': 325000, 'status': 'Pending', 'due_date': '2023-02-20'}
                ]
            }
        }
        
        # Add similar structures for vessel, maintenance, financial, custom report types
        for report_type in ['vessel', 'maintenance', 'financial', 'custom']:
            if report_type not in sample_data:
                sample_data[report_type] = {
                    'summary': {
                        'total_items': random.randint(10, 100),
                        'active_items': random.randint(5, 50),
                        'average_value': random.randint(10000, 100000)
                    },
                    'chart_data': {
                        'distribution': [
                            {'category': 'Type A', 'count': random.randint(5, 20)},
                            {'category': 'Type B', 'count': random.randint(5, 20)},
                            {'category': 'Type C', 'count': random.randint(5, 20)}
                        ],
                        'timeline': [
                            {'month': 'Jan', 'value': random.randint(5, 20)},
                            {'month': 'Feb', 'value': random.randint(5, 20)},
                            {'month': 'Mar', 'value': random.randint(5, 20)}
                        ]
                    },
                    'results': [
                        {'id': 1, 'name': 'Item 1', 'type': 'Type A', 'status': 'Active'},
                        {'id': 2, 'name': 'Item 2', 'type': 'Type B', 'status': 'Inactive'}
                    ]
                }
        
        for i in range(count):
            # Choose a template and user
            template = random.choice(templates)
            created_by = random.choice(users)
            
            # Generate parameters based on template type
            parameters = {
                'date_range': f"{(timezone.now() - timedelta(days=90)).strftime('%Y-%m-%d')} to {timezone.now().strftime('%Y-%m-%d')}",
                'filters': {}
            }
            
            if template.report_type == 'contract':
                parameters['filters']['state'] = random.choice(['All', 'Pending', 'Finance', 'Billed'])
            elif template.report_type == 'invoice':
                parameters['filters']['status'] = random.choice(['All', 'Pending', 'Paid', 'Overdue'])
            elif template.report_type == 'vessel':
                parameters['filters']['status'] = random.choice(['All', 'operational', 'maintenance'])
            
            # Create the report
            report = SavedReport.objects.create(
                name=f"Report: {template.name}",
                template=template,
                description=f"Generated report based on {template.name}",
                report_type=template.report_type,
                created_by=created_by,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),  # created within the last 2 months
                parameters=parameters,
                data=sample_data.get(template.report_type, sample_data['contract']),
                file=f"report_{template.report_type}_{i+1}.pdf" if random.random() < 0.5 else None  # 50% chance of having a file
            )
            reports.append(report)
            
            self.stdout.write(f'Created saved report: {report.name} (Type: {report.report_type})')
        
        self.stdout.write(f'Created a total of {len(reports)} saved reports')
        return reports
    
    def create_dashboards(self, count, users):
        """Create dashboards for analytics"""
        dashboards = []
        
        # Sample dashboard configurations
        dashboard_configs = [
            {
                'layout': '2-col',
                'widgets': [
                    {'type': 'contract_summary', 'title': 'Contract Overview', 'position': 1},
                    {'type': 'invoice_status', 'title': 'Invoice Status', 'position': 2},
                    {'type': 'revenue_chart', 'title': 'Monthly Revenue', 'position': 3},
                    {'type': 'vessel_status', 'title': 'Vessel Status', 'position': 4}
                ]
            },
            {
                'layout': '3-col',
                'widgets': [
                    {'type': 'contract_list', 'title': 'Recent Contracts', 'position': 1},
                    {'type': 'financial_summary', 'title': 'Financial Summary', 'position': 2},
                    {'type': 'maintenance_alerts', 'title': 'Maintenance Alerts', 'position': 3},
                    {'type': 'expiring_documents', 'title': 'Expiring Documents', 'position': 4},
                    {'type': 'charterer_analysis', 'title': 'Top Charterers', 'position': 5}
                ]
            },
            {
                'layout': 'custom',
                'widgets': [
                    {'type': 'kpi_cards', 'title': 'Key Performance Indicators', 'position': 1},
                    {'type': 'interactive_chart', 'title': 'Business Performance', 'position': 2},
                    {'type': 'geo_map', 'title': 'Global Operations', 'position': 3},
                    {'type': 'invoice_aging', 'title': 'Invoice Aging Analysis', 'position': 4}
                ]
            }
        ]
        
        for i in range(count):
            # Choose a user and configuration
            created_by = random.choice(users)
            config = random.choice(dashboard_configs)
            
            # Customize the configuration slightly
            custom_config = config.copy()
            custom_config['refresh_rate'] = random.choice([0, 5, 15, 30, 60])  # minutes (0 = manual refresh)
            custom_config['theme'] = random.choice(['light', 'dark', 'auto'])
            
            # Create the dashboard
            dashboard = Dashboard.objects.create(
                name=f"{self.fake.word().capitalize()} Dashboard" if i > 0 else "Operations Overview",
                description=self.fake.paragraph() if random.random() < 0.7 else "",  # 70% chance of having a description
                created_by=created_by,
                is_public=random.random() < 0.5,  # 50% chance of being public
                created_at=timezone.now() - timedelta(days=random.randint(1, 90)),  # created within the last 3 months
                configuration=custom_config
            )
            dashboards.append(dashboard)
            
            self.stdout.write(f'Created dashboard: {dashboard.name}')
        
        self.stdout.write(f'Created a total of {len(dashboards)} dashboards')
        return dashboards
    
    def create_analytics_logs(self, users, reports, dashboards):
        """Create analytics logs to track system usage"""
        logs = []
        
        # Define possible actions
        actions = [
            'view_report', 'generate_report', 'save_report',
            'view_dashboard', 'create_dashboard', 'update_dashboard'
        ]
        
        # Generate ~5 logs per user on average
        num_logs = len(users) * 5
        
        for i in range(num_logs):
            # Choose a user and action
            user = random.choice(users)
            action = random.choice(actions)
            
            # Generate timestamp within the last 30 days
            timestamp = timezone.now() - timedelta(days=random.randint(0, 30), 
                                                 hours=random.randint(0, 23), 
                                                 minutes=random.randint(0, 59))
            
            # Generate details based on action
            details = {}
            
            if 'report' in action:
                if reports:
                    report = random.choice(reports)
                    details = {
                        'report_id': report.id,
                        'report_name': report.name,
                        'report_type': report.report_type
                    }
                else:
                    details = {
                        'report_type': random.choice(['contract', 'invoice', 'vessel', 'maintenance', 'financial', 'custom']),
                        'filters_applied': random.choice([True, False])
                    }
            
            elif 'dashboard' in action:
                if dashboards:
                    dashboard = random.choice(dashboards)
                    details = {
                        'dashboard_id': dashboard.id,
                        'dashboard_name': dashboard.name
                    }
                else:
                    details = {
                        'dashboard_type': random.choice(['operations', 'financial', 'vessel', 'custom']),
                        'widgets_count': random.randint(3, 8)
                    }
            
            # Add common details
            details['ip_address'] = f"192.168.1.{random.randint(1, 254)}"
            details['user_agent'] = random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X)',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)'
            ])
            
            # Create the log entry
            log = AnalyticsLog.objects.create(
                user=user,
                action=action,
                timestamp=timestamp,
                details=details
            )
            logs.append(log)
        
        self.stdout.write(f'Created a total of {len(logs)} analytics logs')
        return logs 