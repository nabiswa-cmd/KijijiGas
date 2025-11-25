# ReliableGas — LPG Supply Management & Customer Locator System

ReliableGas is a complete digital platform that connects LPG suppliers with nearby customers while helping suppliers manage their daily operations. It includes stock management, multi-substation support, employee accounts, sales and delivery tracking, and integrated M-Pesa STK Push payments. Customers can locate the nearest gas supplier using their device location, compare prices, and order instantly.

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

**Backend:** Python Flask  
**Database:** PostgreSQL  
**Frontend:** HTML + modern responsive UI (Bootstrap / Tailwind)  
**Payments:** M-Pesa Daraja STK Push  
**Maps:** Google Maps API / Mapbox  
**Hosting:** Render / DigitalOcean / AWS (recommended)

---

## 🗄️ Database Overview (simplified)

- suppliers  
- substations  
- employees  
- gases  
- sales  
- payments  
- prepaid_customers  
- stock_movements  
- deliveries  

Each table includes timestamps and relational mapping for accurate record-keeping.

---

## 🏁 Getting Started (Development Setup)

1. Clone the project:
   ```bash
   git clone https://github.com/<your-username>/reliablegas.git
   cd reliablegas
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:  
   Copy `.env.example` → `.env` and fill in:
   - DATABASE_URL  
   - SECRET_KEY  
   - MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET  
   - MPESA_SHORTCODE  
   - MPESA_PASSKEY  
   - MAPS_API_KEY  

5. Run database migrations:
   ```bash
   flask db upgrade
   ```

6. Start server:
   ```bash
   flask run
   ```

---

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

---
