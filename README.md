💳 Django Digital Wallet App
A secure, feature-rich digital wallet system built with Django, allowing users to manage balances, transfer funds, and view transaction histories. Admins can manage wallets, monitor activity, and add funds directly to user accounts.

🔧 Features
✅ User registration with email and phone verification

✅ Secure login/logout with custom validations

✅ Dashboard showing wallet balance and recent transactions

✅ Add, withdraw, and transfer funds between users

✅ Admin-only controls for adding funds to any user

✅ Transaction logging with types and timestamps

✅ Clean Bootstrap-based responsive UI

📦 Tech Stack
Python 3.11

Django 4+

Bootstrap 5

SQLite (default)

HTML, CSS, JavaScript

🚀 Setup Instructions
Clone the repo
git clone https://github.com/yourusername/django-wallet.git

Install dependencies
pip install -r requirements.txt

Run migrations
python manage.py migrate

Create a superuser
python manage.py createsuperuser

Start the development server
python manage.py runserver

📸 Screenshots
(Optional: Add screenshots of the dashboard, login screen, and admin features)

🛡️ Security & Notes
Sensitive actions like adding funds are restricted to admin users.

Transactions are recorded with status, notes, and timestamps.

Includes basic protections against invalid inputs.

📃 License
This project is open-source and available under the MIT License.