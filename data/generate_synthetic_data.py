#!/usr/bin/env python3
import csv
import json
import uuid
import random
from datetime import datetime, timedelta

print("🚀 Starting synthetic data generation for NovaBazaar...")

# Seed random numbers for reproducibility
random.seed(42)

# File Paths
olist_dir = "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/data/olist"
synth_dir = "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/data/synthetic"
cdc_dir = "/Users/rhitambhaduri/.gemini/antigravity/scratch/novabazaar-lakehouse/data/cdc"

# Date range based on Olist orders
MIN_DATE = datetime(2016, 9, 1)
MAX_DATE = datetime(2018, 10, 31)

# Helper: Generate date list
def get_date_range(start_date, end_date):
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

# ──────────────────────────────────────────────────────────
# 1. EXCHANGE RATES GENERATION (exchange_rates.csv)
# ──────────────────────────────────────────────────────────
print("📊 Generating exchange rates...")
dates = get_date_range(MIN_DATE, MAX_DATE)
ex_rates = []

for d in dates:
    # Simulate a random walk for BRL to USD and EUR
    # In 2016-2018 BRL to USD was around 3.10 to 4.20
    # BRL to EUR was around 3.50 to 4.90
    day_num = (d - MIN_DATE).days
    usd_rate = 3.15 + (day_num * 0.001) + (random.uniform(-0.05, 0.05))
    eur_rate = 3.50 + (day_num * 0.0012) + (random.uniform(-0.06, 0.06))
    
    ex_rates.append({
        "date": d.strftime("%Y-%m-%d"),
        "currency": "USD",
        "rate_to_brl": round(1 / usd_rate, 6) # Rate to convert BRL -> USD
    })
    ex_rates.append({
        "date": d.strftime("%Y-%m-%d"),
        "currency": "EUR",
        "rate_to_brl": round(1 / eur_rate, 6) # Rate to convert BRL -> EUR
    })

with open(f"{synth_dir}/exchange_rates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "currency", "rate_to_brl"])
    writer.writeheader()
    writer.writerows(ex_rates)
print(f"   Saved {len(ex_rates)} exchange rate entries.")

# ──────────────────────────────────────────────────────────
# 2. EMPLOYEES & CDC UPDATES (employees.csv & employees_day2.csv)
# ──────────────────────────────────────────────────────────
print("👥 Generating employees and CDC updates...")
first_names = ["Gabriel", "Lucas", "Matheus", "Pedro", "Enzo", "Joao", "Sophia", "Alice", "Julia", "Isabella", "Manuela", "Laura", "Carlos", "Roberto", "Ana", "Maria", "Juliana", "Fernando", "Beatriz", "Camila"]
last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Pinto", "Mendes", "Rocha", "Vieira", "Barbosa"]
positions = ["Sales Associate", "Store Manager", "Assistant Manager", "Cashier", "Inventory Specialist", "HR Specialist", "Customer Service Agent"]
departments = ["Sales", "Operations", "Operations", "Sales", "Supply Chain", "HR", "Customer Service"]

employees = []
# Create 30 initial employees on Day 1
for i in range(1, 31):
    emp_id = f"EMP{i:03d}"
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    pos_idx = random.randint(0, len(positions)-1)
    pos = positions[pos_idx]
    dept = departments[pos_idx]
    salary = round(random.uniform(2500, 9500), 2)
    hire_date = (MIN_DATE + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
    manager_id = "EMP001" if emp_id != "EMP001" else ""
    
    employees.append({
        "employee_id": emp_id,
        "first_name": fn,
        "last_name": ln,
        "email": f"{fn.lower()}.{ln.lower()}@novabazaar.com.br",
        "position": pos,
        "department": dept,
        "salary": salary,
        "hire_date": hire_date,
        "manager_id": manager_id,
        "is_active": "true",
        "modified_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Save Day 1
with open(f"{synth_dir}/employees.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(employees[0].keys()))
    writer.writeheader()
    writer.writerows(employees)

# Create Day 2 updates for employees (SCD Type 2 test)
# EMP005 gets promoted and salary raise, EMP008 leaves (soft delete)
employees_day2 = []
for emp in employees:
    emp_copy = emp.copy()
    if emp_copy["employee_id"] == "EMP005":
        emp_copy["position"] = "Store Manager"
        emp_copy["department"] = "Operations"
        emp_copy["salary"] = round(emp_copy["salary"] * 1.25, 2)
        emp_copy["modified_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        employees_day2.append(emp_copy)
    elif emp_copy["employee_id"] == "EMP008":
        emp_copy["is_active"] = "false"
        emp_copy["modified_date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        employees_day2.append(emp_copy)

# Add 2 new hires on Day 2
for i in range(31, 33):
    emp_id = f"EMP{i:03d}"
    fn = random.choice(first_names)
    ln = random.choice(last_names)
    pos_idx = random.randint(0, len(positions)-1)
    pos = positions[pos_idx]
    dept = departments[pos_idx]
    salary = round(random.uniform(2500, 9500), 2)
    hire_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    employees_day2.append({
        "employee_id": emp_id,
        "first_name": fn,
        "last_name": ln,
        "email": f"{fn.lower()}.{ln.lower()}@novabazaar.com.br",
        "position": pos,
        "department": dept,
        "salary": salary,
        "hire_date": hire_date,
        "manager_id": "EMP001",
        "is_active": "true",
        "modified_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    })

with open(f"{cdc_dir}/employees_day2.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(employees[0].keys()))
    writer.writeheader()
    writer.writerows(employees_day2)
print("   Saved employees.csv and cdc/employees_day2.csv")

# ──────────────────────────────────────────────────────────
# 3. PROMOTIONS & CDC (promotions.csv & promotions_day2.csv)
# ──────────────────────────────────────────────────────────
print("🏷️  Generating promotions...")
promos = [
    {"promotion_id": "PRM001", "promo_name": "Welcome Discount 10%", "discount_pct": 0.10, "start_date": "2016-09-01", "end_date": "2018-12-31", "is_active": "true", "modified_date": "2016-09-01 00:00:00"},
    {"promotion_id": "PRM002", "promo_name": "Black Friday 2016", "discount_pct": 0.25, "start_date": "2016-11-20", "end_date": "2016-11-30", "is_active": "false", "modified_date": "2016-11-30 23:59:59"},
    {"promotion_id": "PRM003", "promo_name": "Summer Special 15%", "discount_pct": 0.15, "start_date": "2017-06-01", "end_date": "2017-08-31", "is_active": "false", "modified_date": "2017-08-31 23:59:59"},
    {"promotion_id": "PRM004", "promo_name": "Black Friday 2017", "discount_pct": 0.30, "start_date": "2017-11-20", "end_date": "2017-11-30", "is_active": "false", "modified_date": "2017-11-30 23:59:59"},
    {"promotion_id": "PRM005", "promo_name": "New Year Kickoff 20%", "discount_pct": 0.20, "start_date": "2018-01-01", "end_date": "2018-01-15", "is_active": "false", "modified_date": "2018-01-15 23:59:59"},
    {"promotion_id": "PRM006", "promo_name": "Free Shipping Special", "discount_pct": 0.05, "start_date": "2018-05-01", "end_date": "2018-10-31", "is_active": "true", "modified_date": "2018-05-01 00:00:00"},
]

with open(f"{synth_dir}/promotions.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(promos[0].keys()))
    writer.writeheader()
    writer.writerows(promos)

# Day 2 promotions - update PRM006 to be deactivated, add a new Black Friday 2018 promo
promos_day2 = []
for p in promos:
    p_copy = p.copy()
    if p_copy["promotion_id"] == "PRM006":
        p_copy["is_active"] = "false"
        p_copy["modified_date"] = "2018-11-01 00:00:00"
        promos_day2.append(p_copy)

promos_day2.append(
    {"promotion_id": "PRM007", "promo_name": "Black Friday 2018", "discount_pct": 0.35, "start_date": "2018-11-20", "end_date": "2018-11-30", "is_active": "true", "modified_date": "2018-11-01 00:00:00"}
)

with open(f"{cdc_dir}/promotions_day2.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(promos[0].keys()))
    writer.writeheader()
    writer.writerows(promos_day2)
print("   Saved promotions.csv and cdc/promotions_day2.csv")

# ──────────────────────────────────────────────────────────
# 4. MARKETING CAMPAIGNS (marketing_campaigns.json)
# ──────────────────────────────────────────────────────────
print("📣 Generating marketing campaigns...")
campaigns = [
    {"campaign_id": "CMP001", "campaign_name": "Google Ads - Electronics", "channel": "Paid Search", "start_date": "2017-01-01", "end_date": "2017-06-30", "budget": 15000.00},
    {"campaign_id": "CMP002", "campaign_name": "Facebook Retargeting Q3", "channel": "Social Media", "start_date": "2017-07-01", "end_date": "2017-09-30", "budget": 8500.00},
    {"campaign_id": "CMP003", "campaign_name": "Email Newsletter Blast", "channel": "Email", "start_date": "2018-02-01", "end_date": "2018-02-07", "budget": 1200.00},
    {"campaign_id": "CMP004", "campaign_name": "Instagram Influencer Push", "channel": "Influencer", "start_date": "2018-05-01", "end_date": "2018-08-31", "budget": 24000.00},
]

with open(f"{synth_dir}/marketing_campaigns.json", "w") as f:
    json.dump(campaigns, f, indent=2)
print("   Saved marketing_campaigns.json")

# ──────────────────────────────────────────────────────────
# 5. INVENTORY SNAPSHOTS (inventory_snapshots.json)
# ──────────────────────────────────────────────────────────
print("📦 Generating inventory snapshots...")
# Read Olist products to maintain referential integrity
product_ids = []
try:
    with open(f"{olist_dir}/olist_products_dataset.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_ids.append(row["product_id"])
except FileNotFoundError:
    print("   ⚠️ olist_products_dataset.csv not found, generating mock product_ids instead!")
    product_ids = [f"prod_{i:04d}" for i in range(1, 101)]

# Limit to 500 products to keep file size reasonable
sample_product_ids = product_ids[:500]
inventory_snapshots = []

# Generate daily snapshots for the last 15 days of the dataset (2018-08-15 to 2018-08-30)
snapshot_dates = get_date_range(datetime(2018, 8, 15), datetime(2018, 8, 30))

for sd in snapshot_dates:
    for pid in sample_product_ids:
        # Base inventory calculations on random seeds per product
        # Ensure we have reorders and stockouts occasionally
        on_hand = random.choices([random.randint(10, 150), 0, random.randint(1, 9)], weights=[0.85, 0.05, 0.10])[0]
        reorder_pt = random.choice([5, 10, 15])
        on_order = 0 if on_hand > reorder_pt else random.choice([0, 50])
        
        inventory_snapshots.append({
            "product_id": pid,
            "snapshot_date": sd.strftime("%Y-%m-%d"),
            "quantity_on_hand": on_hand,
            "quantity_on_order": on_order,
            "reorder_point": reorder_pt,
            "reorder_qty": 50
        })

with open(f"{synth_dir}/inventory_snapshots.json", "w") as f:
    json.dump(inventory_snapshots, f, indent=2)
print(f"   Saved {len(inventory_snapshots)} inventory snapshot entries.")

# ──────────────────────────────────────────────────────────
# 6. GENERAL LEDGER (general_ledger.csv)
# ──────────────────────────────────────────────────────────
print("🧾 Generating general ledger entries linked to Olist payments...")

# Read Olist payments to build matching GL entries for reconciliation!
gl_entries = []
payment_rows = []

try:
    with open(f"{olist_dir}/olist_order_payments_dataset.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payment_rows.append(row)
except FileNotFoundError:
    print("   ⚠️ olist_order_payments_dataset.csv not found, generating mock ledger instead!")
    # Mock data if Olist payments not downloaded yet
    for i in range(1, 1001):
        payment_rows.append({
            "order_id": str(uuid.uuid4())[:8],
            "payment_value": str(round(random.uniform(20.0, 500.0), 2))
        })

# Let's take a large slice or all rows to make it look realistic.
# Let's use the first 20,000 rows to prevent the ledger file from growing too large (>10MB).
sampled_payments = payment_rows[:20000]

entry_num = 1
for row in sampled_payments:
    order_id = row["order_id"]
    val = float(row["payment_value"])
    if val <= 0:
        continue
        
    posting_date = (MIN_DATE + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d")
    
    # Entry 1: Credit to Revenue (Account 40010)
    gl_entries.append({
        "entry_id": f"GL{entry_num:06d}",
        "order_id": order_id,
        "posting_date": posting_date,
        "account_code": "40010", # Sales Revenue
        "debit_amount": 0.0,
        "credit_amount": round(val, 2),
        "cost_center": "CC_ECOM"
    })
    entry_num += 1
    
    # Entry 2: Debit to Accounts Receivable (Account 10020)
    gl_entries.append({
        "entry_id": f"GL{entry_num:06d}",
        "order_id": order_id,
        "posting_date": posting_date,
        "account_code": "10020", # Accounts Receivable
        "debit_amount": round(val, 2),
        "credit_amount": 0.0,
        "cost_center": "CC_FINANCE"
    })
    entry_num += 1

with open(f"{synth_dir}/general_ledger.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["entry_id", "order_id", "posting_date", "account_code", "debit_amount", "credit_amount", "cost_center"])
    writer.writeheader()
    writer.writerows(gl_entries)
print(f"   Saved {len(gl_entries)} General Ledger entries.")

# ──────────────────────────────────────────────────────────
# 7. CUSTOMERS CDC UPDATES (customers_day2.csv & customers_day3.csv)
# ──────────────────────────────────────────────────────────
print("👤 Generating customer CDC update files...")
# Read Olist customers
olist_customers = []
try:
    with open(f"{olist_dir}/olist_customers_dataset.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            olist_customers.append(row)
except FileNotFoundError:
    print("   ⚠️ olist_customers_dataset.csv not found, cannot generate customer CDC!")

if olist_customers:
    # Day 2: Take 1% of customers and update their address details (SCD Type 2 test)
    cdc_sample_size = len(olist_customers) // 100
    day2_customers = []
    
    # Select random customers to update
    updated_indices = random.sample(range(len(olist_customers)), cdc_sample_size)
    for idx in updated_indices:
        cust = olist_customers[idx].copy()
        # Change state and city
        cust["customer_state"] = random.choice(["SP", "RJ", "MG", "RS", "PR"])
        cust["customer_city"] = f"{cust['customer_city']}_UPDATED"
        day2_customers.append(cust)
        
    with open(f"{cdc_dir}/customers_day2.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(olist_customers[0].keys()))
        writer.writeheader()
        writer.writerows(day2_customers)
    print(f"   Saved {len(day2_customers)} updates in cdc/customers_day2.csv")

    # Day 3: Take another set of updates plus some new registrations
    day3_customers = []
    
    # 500 updates
    more_updates = random.sample(range(len(olist_customers)), 500)
    for idx in more_updates:
        if idx not in updated_indices:
            cust = olist_customers[idx].copy()
            cust["customer_state"] = "SP"
            cust["customer_city"] = "Sao Paulo"
            day3_customers.append(cust)
            
    # 100 brand new customer profiles
    for i in range(100):
        new_id = f"new_cust_id_{i:04d}"
        new_uniq = f"new_uniq_id_{i:04d}"
        day3_customers.append({
            "customer_id": new_id,
            "customer_unique_id": new_uniq,
            "customer_zip_code_prefix": "1001",
            "customer_city": "Sao Paulo",
            "customer_state": "SP"
        })
        
    with open(f"{cdc_dir}/customers_day3.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(olist_customers[0].keys()))
        writer.writeheader()
        writer.writerows(day3_customers)
    print(f"   Saved {len(day3_customers)} entries in cdc/customers_day3.csv")

# ──────────────────────────────────────────────────────────
# 8. PRODUCTS CDC UPDATES (products_day2.csv)
# ──────────────────────────────────────────────────────────
print("🏷️  Generating product CDC updates...")
olist_products = []
try:
    with open(f"{olist_dir}/olist_products_dataset.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            olist_products.append(row)
except FileNotFoundError:
    pass

if olist_products:
    # Day 2: Take 100 products and modify their weights or categories
    # And add 5 brand new products
    day2_products = []
    prod_updates = random.sample(olist_products, 100)
    for p in prod_updates:
        p_copy = p.copy()
        # Update weight by +10%
        w = p_copy["product_weight_g"]
        if w:
            p_copy["product_weight_g"] = str(int(float(w) * 1.1))
        p_copy["product_category_name"] = "eletrodomesticos"
        day2_products.append(p_copy)
        
    # Add 5 brand new products
    for i in range(5):
        new_id = f"new_prod_id_{i:04d}"
        day2_products.append({
            "product_id": new_id,
            "product_category_name": "informatica_acessorios",
            "product_name_lenght": "30",
            "product_description_lenght": "250",
            "product_photos_qty": "2",
            "product_weight_g": "500",
            "product_length_cm": "20",
            "product_height_cm": "10",
            "product_width_cm": "15"
        })
        
    with open(f"{cdc_dir}/products_day2.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(olist_products[0].keys()))
        writer.writeheader()
        writer.writerows(day2_products)
    print(f"   Saved {len(day2_products)} entries in cdc/products_day2.csv")

print("\n🎉 All synthetic data and CDC files generated successfully!")
