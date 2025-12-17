# KijijiGas — LPG Supply Management & Customer Locator System

kijijiGas is a complete digital platform that connects LPG suppliers with nearby customers while helping suppliers manage their daily operations. It includes stock management, multi-substation support, employee accounts, sales and delivery tracking, and integrated M-Pesa STK Push payments. Customers can locate the nearest gas supplier using their device location, compare prices, and order instantly.

---

## 🚀 Key Features

### 🔸 Customer Features
- Search and locate the nearest verified gas supplier  
- View available gas sizes and prices  
- Make orders for delivery or pick-up  
- Track order progress  
- Pay using **M-Pesa STK Push**  
- View supplier profiles & ratings (future)

### 🔸 Supplier Features
- Create a business account and get verified  
- Add multiple substations / branches  
- Track **filled vs empty cylinders**  
- Add employees with assigned roles (Admin, Manager, Agent)  
- Record sales, deliveries, and prepaid orders  
- Receive M-Pesa payments directly  
- Get smart reports (profit, sales trends, stock alerts)

### 🔸 Admin/Business Owner Features
- Approve or reject supplier applications  
- Manage employees  
- Adjust stock levels with history records  
- View performance dashboards  
- Track all stock movements:  
  - stock_in  
  - stock_out  
  - returns  
  - sales  
  - prepaid collections  

---

## 🧱 System Architecture

**Backend:** Python Django
**Database:** PostgreSQL  
**Frontend:** HTML + modern responsive UI (Bootstrap / Tailwind)  
**Payments:** M-Pesa Daraja STK Push  
**Maps:** Google Maps API / Mapbox  
**Hosting:** Render / DigitalOcean / AWS (recommended)

---

## 🗄️ Database Overview (simplified)

🏁 KijijiGas – Django Setup Guide
1. Clone the project
git clone https://github.com/<your-username>/kijijigas.git
cd kijijigas

2. Create a virtual environment
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Configure environment variables

Copy .env.example → .env and fill in:

DATABASE_URL → Your PostgreSQL or other database URL

SECRET_KEY → Your Django secret key

MPESA_CONSUMER_KEY → Safaricom API consumer key

MPESA_CONSUMER_SECRET → Safaricom API consumer secret

MPESA_SHORTCODE → Your business shortcode

MPESA_PASSKEY → Your Safaricom passkey

MAPS_API_KEY → Google Maps API key

Tip: Use python-decouple
 or django-environ
 to read .env variables in settings.py.

Example snippet for settings.py using django-environ:

import environ

env = environ.Env()
environ.Env.read_env()  # reads .env

DATABASES = {
    'default': env.db('DATABASE_URL')
}

SECRET_KEY = env('SECRET_KEY')
MPESA_CONSUMER_KEY = env('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = env('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = env('MPESA_SHORTCODE')
MPESA_PASSKEY = env('MPESA_PASSKEY')
MAPS_API_KEY = env('MAPS_API_KEY')

5. Apply database migrations
python manage.py migrate

6. Create a superuser (admin account)
python manage.py createsuperuser

7. Start the development server
python manage.py runserver

8. Access the app

Open your browser at:

http://127.0.0.1:8000/

9. MPESA Integration Tips

Install the official Safaricom SDK or use requests to call the API.

For STK Push:

Generate access token using consumer key/secret.

Use MPESA_SHORTCODE and MPESA_PASSKEY for payments.

Always test in sandbox mode before going live.

10. Maps Integration Tips

Use MAPS_API_KEY in your Django templates or JavaScript for:

Displaying gas delivery locations

Calculating routes and distances

Keep the key secure in .env and never push it to GitHub.

## 📡 API Examples

- Find nearby suppliers  
  ```
  GET /api/suppliers/nearby?lat=...&lng=...
  ```

- Create a sale  
  ```
  POST /api/sales
  ```

- Trigger M-Pesa STK Push  
  ```
  POST /api/payments/mpesa
  ```

- Get dashboard data  
  ```
  GET /api/dashboard
  ```

---

## 🛣️ Roadmap

### MVP
- Supplier signup & verification  
- Employee accounts  
- Stock tracking (filled/empty)  
- Sales logging  
- Customer nearby search  
- Basic delivery assignment  

### Phase 2
- Full M-Pesa integration  
- Prepaid order module  
- Detailed reports  

### Phase 3
- Ratings & reviews  
- Route optimisation  
- Supplier marketplace  
- Mobile App  

---

## 📜 License
MIT License — free to use, modify and improve.

---

## 👤 Author
**Nabiswa James**  
📧 Email: nabiswaj8@gmail.com  
🌐 GitHub: https://github.com/<nabiswa-cmd>/

test it out for free on https://kijijigas-production.up.railway.app/
---

