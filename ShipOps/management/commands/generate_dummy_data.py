import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from ShipOps.models import Contract, Invoice, UserRole, UserProfile, Contact
from ShipsAuth.models import Occupation, Profile, SystemPages, Permission

class Command(BaseCommand):
    help = 'Generates dummy data for the Ships Management System'

    def add_arguments(self, parser):
        parser.add_argument('--contracts', type=int, default=20, help='Number of contracts to generate')
        parser.add_argument('--users', type=int, default=5, help='Number of users to generate')
        parser.add_argument('--contacts', type=int, default=10, help='Number of contacts to generate')

    def handle(self, *args, **options):
        self.stdout.write('Starting dummy data generation...')
        
        num_contracts = options['contracts']
        num_users = options['users']
        num_contacts = options['contacts']
        
        with transaction.atomic():
            # Create roles first
            self.create_roles()
            
            # Create occupations
            self.create_occupations()
            
            # Create system pages and permissions
            self.create_system_pages()
            
            # Create users with profiles
            users = self.create_users(num_users)
            
            # Create contacts
            contacts = self.create_contacts(num_contacts)
            
            # Create contracts
            contracts = self.create_contracts(num_contracts)
            
            # Create invoices (for some contracts)
            self.create_invoices(contracts)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully generated dummy data!'))
        self.stdout.write(f'Created {num_users} users')
        self.stdout.write(f'Created {num_contacts} contacts')
        self.stdout.write(f'Created {num_contracts} contracts')
        self.stdout.write(f'Created invoices for {num_contracts // 2} contracts')

    def create_roles(self):
        """Create user roles"""
        roles = [
            ('admin', 'Administrator'),
            ('finance', 'Finance Department'),
            ('manager', 'Head Manager'),
            ('operations', 'Operations Staff'),
            ('viewer', 'Read-only User'),
        ]
        
        for role_name, role_desc in roles:
            UserRole.objects.get_or_create(
                name=role_name,
                defaults={'description': f'Users with {role_desc} privileges'}
            )
        
        self.stdout.write('Created user roles')

    def create_occupations(self):
        """Create occupations for ShipsAuth"""
        occupations = [
            ('مدير', 'Manager', 1),
            ('محاسب', 'Accountant', 2),
            ('مشغل', 'Operator', 3),
            ('مستخدم', 'User', 4),
            ('ضيف', 'Guest', 5),
        ]
        
        for ar_name, en_name, power in occupations:
            Occupation.objects.get_or_create(
                ar_name=ar_name, 
                en_name=en_name,
                defaults={'power': power}
            )
        
        self.stdout.write('Created occupations')

    def create_system_pages(self):
        """Create system pages and permissions"""
        pages = [
            ('dashboard', 'Dashboard', True),
            ('contracts', 'Contracts', True),
            ('invoices', 'Invoices', True),
            ('users', 'Users', True),
            ('settings', 'Settings', True),
        ]
        
        # Create pages
        created_pages = []
        for endpoint, name, is_nav in pages:
            page, created = SystemPages.objects.get_or_create(
                endpoint=endpoint,
                defaults={
                    'rendered_name': name,
                    'is_nav_item': is_nav,
                    'has_submenu': False
                }
            )
            created_pages.append(page)
        
        # Create permissions
        occupations = Occupation.objects.all()
        for page in created_pages:
            for occupation in occupations:
                # Manager and admin get access to everything
                if occupation.power <= 2:
                    Permission.objects.get_or_create(
                        page=page,
                        occupation=occupation
                    )
                # Others get access to dashboard and contracts only
                elif page.endpoint in ['dashboard', 'contracts']:
                    Permission.objects.get_or_create(
                        page=page,
                        occupation=occupation
                    )
        
        self.stdout.write('Created system pages and permissions')

    def create_users(self, count):
        """Create users with both types of profiles"""
        users = []
        
        # Create a superuser if one doesn't exist
        if not User.objects.filter(is_superuser=True).exists():
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            users.append(superuser)
            
            # Create profiles for superuser
            occupation = Occupation.objects.filter(power=1).first()
            Profile.objects.create(
                user_obj=superuser,
                occupation=occupation,
                token='admintoken',
                profile_image='admin.jpg'
            )
            
            role = UserRole.objects.get(name='admin')
            UserProfile.objects.create(
                user=superuser,
                role=role,
                department='Management',
                can_view_contracts=True,
                can_edit_contracts=True,
                can_view_invoices=True,
                can_edit_invoices=True
            )
            
            count -= 1  # Reduce count since we created one user
        
        # Create regular users
        roles = list(UserRole.objects.all())
        occupations = list(Occupation.objects.all())
        departments = ['Operations', 'Finance', 'Management', 'Sales', 'IT']
        
        for i in range(count):
            username = f'user{i+1}'
            
            # Skip if user already exists
            if User.objects.filter(username=username).exists():
                continue
                
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password=f'password{i+1}',
                first_name=f'First{i+1}',
                last_name=f'Last{i+1}'
            )
            users.append(user)
            
            # Create ShipsAuth profile
            occupation = random.choice(occupations)
            Profile.objects.create(
                user_obj=user,
                occupation=occupation,
                token=f'token{i+1}',
                profile_image=f'profile{i+1}.jpg'
            )
            
            # Create ShipOps profile
            role = random.choice(roles)
            department = random.choice(departments)
            can_edit = role.name in ['admin', 'manager']
            
            UserProfile.objects.create(
                user=user,
                role=role,
                department=department,
                can_view_contracts=True,
                can_edit_contracts=can_edit,
                can_view_invoices=role.name != 'viewer',
                can_edit_invoices=role.name in ['admin', 'finance']
            )
        
        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_contacts(self, count):
        """Create contact records"""
        contacts = []
        
        ar_first_names = ['أحمد', 'محمد', 'علي', 'خالد', 'عمر', 'سعيد', 'فهد', 'ناصر', 'سلطان', 'عبدالله']
        ar_last_names = ['الشمري', 'العتيبي', 'القحطاني', 'السبيعي', 'الدوسري', 'المطيري', 'الحربي', 'الغامدي', 'الزهراني', 'البقمي']
        en_first_names = ['Ahmed', 'Mohammed', 'Ali', 'Khaled', 'Omar', 'Saeed', 'Fahad', 'Nasser', 'Sultan', 'Abdullah']
        en_last_names = ['Al-Shammari', 'Al-Otaibi', 'Al-Qahtani', 'Al-Subaie', 'Al-Dosari', 'Al-Mutairi', 'Al-Harbi', 'Al-Ghamdi', 'Al-Zahrani', 'Al-Buqami']
        
        for i in range(count):
            ar_fname_idx = random.randint(0, len(ar_first_names) - 1)
            ar_lname_idx = random.randint(0, len(ar_last_names) - 1)
            
            ar_fname = ar_first_names[ar_fname_idx]
            ar_lname = ar_last_names[ar_lname_idx]
            en_fname = en_first_names[ar_fname_idx]  # Use same index for corresponding names
            en_lname = en_last_names[ar_lname_idx]
            
            ar_name = f"{ar_fname} {ar_lname}"
            en_name = f"{en_fname} {en_lname}"
            
            contact = Contact(
                ar_name=ar_name,
                en_name=en_name,
                ar_fname=ar_fname,
                ar_lname=ar_lname,
                en_fname=en_fname,
                en_lname=en_lname,
                phone_number=f"+966 5{random.randint(10000000, 99999999)}",
                email=f"{en_fname.lower()}.{en_lname.lower()}@example.com"
            )
            contact.save()
            contacts.append(contact)
        
        self.stdout.write(f'Created {len(contacts)} contacts')
        return contacts

    def create_contracts(self, count):
        """Create contract records"""
        contracts = []
        
        vessels = ['Arabian Star', 'Gulf Pride', 'Sea Knight', 'Desert Voyager', 'Red Sea Explorer', 
                  'Falcon Mariner', 'Al Manhal', 'Saqr Al Khaleej', 'Al Jawhara', 'Al Dana']
        
        charterers = ['Saudi Aramco', 'ADNOC', 'Qatar Gas', 'Kuwait Oil Company', 'PDO Oman',
                     'Bahrain Petroleum', 'Emirates National Oil', 'Dragon Oil', 'BP Middle East', 'Shell GCC']
        
        owners = ['National Shipping Co.', 'Gulf Marine Services', 'Arabian Maritime Ltd.', 'Middle East Shipping',
                 'Red Sea Navigation', 'Peninsula Maritime', 'Ocean Gulf Carriers', 'Arabian Shipping Lines']
        
        charter_forms = ['BIMCO Standard', 'ASBA', 'Shelltime 4', 'Baltime', 'NYPE 93', 'SUPPLYTIME 2017']
        
        cargoes = ['Crude Oil', 'LNG', 'Petrochemicals', 'Container Goods', 'Dry Bulk', 'Vehicles', 
                  'Construction Materials', 'General Merchandise', 'Refrigerated Goods']
        
        ports = ['Jeddah', 'Dammam', 'Jubail', 'Dubai', 'Abu Dhabi', 'Doha', 'Kuwait', 'Muscat', 
                'Salalah', 'Manama', 'Fujairah', 'Ras Tanura', 'Yanbu']
        
        now = timezone.now()
        
        for i in range(count):
            # Generate dates
            start_date = now - timedelta(days=random.randint(0, 365))
            end_date = start_date + timedelta(days=random.randint(30, 180))
            
            # Random state (0=pending, 1=finance, 2=billed)
            state = random.randint(0, 2)
            
            contract = Contract(
                charter_party_dated=start_date - timedelta(days=random.randint(1, 30)),
                charterer=random.choice(charterers),
                owner=random.choice(owners),
                charter_party_form=random.choice(charter_forms),
                vessel=random.choice(vessels),
                charter_party_speed=f"{random.randint(10, 20)} knots",
                last_three_cargoes=", ".join(random.sample(cargoes, 3)),
                cargo=random.choice(cargoes),
                quantity=f"{random.randint(10000, 100000)} MT",
                heating=f"{random.randint(20, 40)}°C" if random.choice([True, False]) else "N/A",
                load_port=random.choice(ports),
                laycan=f"{random.randint(1, 28)}-{random.randint(1, 28)} {start_date.strftime('%b %Y')}",
                discharge_port=random.choice(ports),
                freight=f"USD {random.randint(200000, 2000000)}",
                demurrage=f"USD {random.randint(10000, 50000)}/day",
                laytime=f"{random.randint(24, 96)} hours",
                payment_terms="30 days from completion",
                payment_to=random.choice(owners),
                brokers="Middle East Maritime Brokers",
                commission=f"{random.randint(1, 5)}%",
                state=state,
                contract_start=start_date,
                contract_end=end_date
            )
            contract.save()
            contracts.append(contract)
        
        self.stdout.write(f'Created {len(contracts)} contracts')
        return contracts

    def create_invoices(self, contracts):
        """Create invoice records for about half the contracts"""
        invoices = []
        
        # Create invoices for contracts with state > 0
        for contract in contracts:
            if contract.state > 0:  # Only create invoices for contracts sent to finance or billed
                price_usd = float(contract.freight.replace('USD ', '').replace(',', ''))
                
                # Convert to AED with random exchange rate between 3.65-3.68
                exchange_rate = random.uniform(3.65, 3.68)
                price_aed = price_usd * exchange_rate
                
                # Function to convert number to words
                def num_to_words(num):
                    # Simplified version for demonstration
                    return f"{num:,.2f} (approximately)"
                
                invoice = Invoice(
                    price_usd=price_usd,
                    price_usd_in_word=num_to_words(price_usd),
                    aed_price=price_aed,
                    aed_price_in_word=num_to_words(price_aed),
                    created_at=contract.contract_start + timedelta(days=random.randint(1, 30)),
                    contract=contract
                )
                invoice.save()
                invoices.append(invoice)
        
        self.stdout.write(f'Created {len(invoices)} invoices')
        return invoices 