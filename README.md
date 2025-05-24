💳 Django Digital Wallet
This is a web-based digital wallet application built using Django and styled with Bootstrap. It allows users to register, manage their account balances, transfer funds, and track transaction history. Admin users can add funds to any user's wallet.

🔍 Features
User Registration & Login
Secure authentication with email and phone number verification.

Admin Fund Management
Admins can add funds to any user’s wallet directly from the dashboard.

Fund Transfers Between Users
Users can transfer money securely to other registered users.

Transaction History
Each user has access to a detailed view of recent transactions:

📤 Sent Transfers

📥 Received Transfers

💸 Withdrawals

➕ Admin-added Funds

Role-Based Access
Only admins can add funds; normal users can only withdraw or transfer.

🛠️ Technologies Used
Backend: Django (Python)

Frontend: HTML, CSS, Bootstrap 5

Database: SQLite (for development)

Authentication: Django built-in AbstractUser with email and phone fields

Session Management: Django Auth System

🚀 Getting Started
Prerequisites
Python 3.8+

pip

Virtualenv (recommended)

Installation
Clone the repository

bash

git clone https://github.com/your-username/django-digital-wallet.git
cd django-digital-wallet
Set up the virtual environment

bash

python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
Install dependencies

bash

pip install -r requirements.txt
Run migrations

bash

python manage.py migrate
Create a superuser

bash

python manage.py createsuperuser
Start the development server

bash

python manage.py runserver
📸 Screenshots
Below is a preview of the dashboard interface:
![Dashboard Screenshot] (screenshots/dashboard.png)
