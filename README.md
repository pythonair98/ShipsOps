# Ships Management System

A comprehensive Django-based system for managing ship contracts, invoices, and contacts with support for both Arabic and English languages.

## Features

- **Contract Management**
  - Create and manage ship reservation contracts
  - Track charter party details
  - Monitor contract states and dates
  - Handle vessel and cargo information
  - Manage payment terms and commission details

- **Invoice System**
  - Generate invoices linked to contracts
  - Support for both USD and AED currencies
  - Price representation in words and numbers
  - Automatic invoice tracking and management

- **Contact Management**
  - Bilingual contact information (Arabic/English)
  - Store and manage contact details
  - Track contact creation dates
  - Support for phone numbers and email addresses

- **Authentication System**
  - Secure user authentication
  - Role-based access control
  - User management interface

## Project Structure

```
ShipsManagment/
├── ShipOps/              # Main operations app
│   ├── models.py         # Data models for contracts, invoices, contacts
│   ├── views.py          # View logic
│   ├── forms.py          # Form definitions
│   ├── admin.py         # Admin interface customization
│   └── urls.py          # URL routing
├── ShipsAuth/           # Authentication app
│   ├── models.py        # User and authentication models
│   └── forms.py         # Authentication forms
├── templates/          # HTML templates
├── static/            # Static files (CSS, JS, images)
└── manage.py         # Django management script
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
```

2. Activate the virtual environment:
- Windows:
```bash
.venv\Scripts\activate
```
- Unix/MacOS:
```bash
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install django
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Models

### Contract
- Manages ship reservation contracts
- Tracks charter party details, vessel information, and cargo details
- Handles payment terms and commission information
- Maintains contract states and important dates

### Invoice
- Links to contracts (one-to-one relationship)
- Supports dual currency (USD/AED)
- Stores prices in both numerical and word formats
- Tracks creation timestamps

### Contact
- Bilingual contact information storage
- Supports both Arabic and English names
- Manages contact details (phone, email)
- Tracks contact creation dates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is proprietary and confidential. All rights reserved. 