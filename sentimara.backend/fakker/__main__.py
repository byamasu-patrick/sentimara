import csv
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Generate Clients Data
clients_data = []
south_african_first_names = [
    "Thabo", "Nomsa", "Sipho", "Zanele", "Mandla", "Precious", "Kagiso", "Thandiwe", 
    "Bongani", "Ntombi", "Lesego", "Palesa", "Tshepo", "Nomthandazo", "Sello", "Dineo",
    "Neo", "Kgomotso", "Lerato", "Mpho", "Tebogo", "Refilwe", "Gift", "Beauty",
    "Lucky", "Happy", "Innocent", "Blessing", "Faith", "Hope", "Grace", "Joy",
    "John", "Mary", "David", "Sarah", "Michael", "Elizabeth", "James", "Susan",
    "Robert", "Linda", "William", "Patricia", "Richard", "Jennifer", "Charles", "Lisa",
    "Pieter", "Marietjie", "Johan", "Annelie", "Francois", "Elmarie", "Hennie", "Suzette"
]

south_african_last_names = [
    "Mthembu", "Nkomo", "Dlamini", "Ndlovu", "Khumalo", "Mahlangu", "Mokoena", "Molefe",
    "Maseko", "Sibeko", "Zungu", "Mnguni", "Radebe", "Sithole", "Cele", "Zulu",
    "Xhosa", "Tswana", "Sotho", "Venda", "Tsonga", "Swati", "Motaung", "Mahlaba",
    "Van der Merwe", "Smith", "Botha", "Van Wyk", "Pretorius", "Du Toit", "Nel", "Meyer",
    "Steyn", "Fourie", "Le Roux", "Jansen", "Van Zyl", "Coetzee", "Marais", "Viljoen",
    "Patel", "Singh", "Reddy", "Naidoo", "Pillay", "Maharaj", "Moodley", "Ramjee"
]

south_african_cities = [
    "Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein",
    "East London", "Pietermaritzburg", "Witbank", "Welkom", "Kimberley", "Rustenburg",
    "Polokwane", "Nelspruit", "George", "Upington", "Klerksdorp", "Potchefstroom"
]

provinces = [
    "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape", "Free State",
    "Limpopo", "Mpumalanga", "North West", "Northern Cape"
]

id_types = ["South African ID", "Passport", "Asylum Document", "Permit"]

transaction_types = [
    "Deposit", "Withdrawal", "Transfer In", "Transfer Out", "Payment", 
    "Salary", "Investment", "Loan Payment", "Insurance", "Utility Payment"
]

for i in range(200):
    client_id = str(uuid.uuid4())
    client_number = f"CL{str(i+1).zfill(6)}"
    
    # Random dates for creation (last 6 months) with time
    random_days = random.randint(30, 180)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    created_date = datetime.now() - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
    
    # Birth date (18-80 years old)
    birth_date = datetime.now() - timedelta(days=random.randint(18*365, 80*365))
    
    first_name = random.choice(south_african_first_names)
    last_name = random.choice(south_african_last_names)
    
    client = {
        "id": client_id,
        "client_number": client_number,
        "created_at": created_date.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": created_date.strftime("%Y-%m-%d %H:%M:%S"),
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": birth_date.strftime("%Y-%m-%d %H:%M:%S"),
        "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
        "phone": f"0{random.randint(60, 89)}{random.randint(1000000, 9999999)}",
        "id_type": random.choice(id_types),
        "id_number": f"{random.randint(1000000000000, 9999999999999)}",
        "street_address": f"{random.randint(1, 999)} {random.choice(['Main', 'Church', 'Market', 'King', 'Queen'])} Street",
        "city": random.choice(south_african_cities),
        "state": random.choice(provinces),
        "postal_code": f"{random.randint(1000, 9999)}",
        "country": "South Africa",
        "annual_income": f"{random.randint(120000, 2000000)}.00",
        "income_currency": "ZAR",
        "nationality": random.choice(["South African", "Zimbabwean", "Nigerian", "Ghanaian", "Indian", "British"])
    }
    clients_data.append(client)

# Generate timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Write clients CSV
with open(f'clients_{timestamp}.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        'id', 'client_number', 'created_at', 'updated_at', 'first_name', 'last_name',
        'date_of_birth', 'email', 'phone', 'id_type', 'id_number', 'street_address',
        'city', 'state', 'postal_code', 'country', 'annual_income', 'income_currency', 'nationality'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(clients_data)

print(f"Generated {len(clients_data)} clients in clients_{timestamp}.csv")

# Generate Transactions Data
transactions_data = []
transaction_counter = 1

# Define the 3-month period
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

for client in clients_data:
    client_number = client['client_number']
    
    # Generate 5-15 transactions per client per month (so 15-45 total over 3 months)
    total_transactions = random.randint(15, 45)
    
    for _ in range(total_transactions):
        transaction_id = str(uuid.uuid4())
        transaction_number = f"TXN{str(transaction_counter).zfill(8)}"
        transaction_counter += 1
        
        # Random date within the 3-month period with time
        random_days = random.randint(0, 90)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)
        transaction_date = start_date + timedelta(days=random_days, hours=random_hours, minutes=random_minutes, seconds=random_seconds)
        
        # Transaction type and corresponding amount logic
        trans_type = random.choice(transaction_types)
        
        if trans_type in ["Deposit", "Transfer In", "Salary", "Investment"]:
            # Positive amounts (money coming in)
            amount = random.randint(500, 50000)
        elif trans_type in ["Withdrawal", "Transfer Out", "Payment", "Loan Payment", "Insurance", "Utility Payment"]:
            # Negative amounts (money going out) - but stored as positive in DB
            amount = random.randint(100, 25000)
        else:
            amount = random.randint(100, 30000)
        
        # Add some cents for realism
        amount_decimal = amount + (random.randint(0, 99) / 100)
        
        transaction = {
            "id": transaction_id,
            "transaction_number": transaction_number,
            "client_number": client_number,
            "transaction_type": trans_type,
            "amount": f"{amount_decimal:.2f}",
            "currency": "ZAR",
            "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        transactions_data.append(transaction)

# Write transactions CSV
with open(f'transactions_{timestamp}.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        'id', 'transaction_number', 'client_number', 'transaction_type', 
        'amount', 'currency', 'transaction_date', 'created_at', 'updated_at'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(transactions_data)

print(f"Generated {len(transactions_data)} transactions in transactions_{timestamp}.csv")
print(f"Average transactions per client: {len(transactions_data)/len(clients_data):.1f}")

# Generate some statistics
print("\n--- Data Summary ---")
print(f"Clients: {len(clients_data)}")
print(f"Transactions: {len(transactions_data)}")
print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Currency: ZAR (South African Rand)")

# Transaction type distribution
type_counts = {}
for trans in transactions_data:
    trans_type = trans['transaction_type']
    type_counts[trans_type] = type_counts.get(trans_type, 0) + 1

print("\nTransaction Types:")
for trans_type, count in sorted(type_counts.items()):
    print(f"  {trans_type}: {count}")

print(f"\nFiles created: clients_{timestamp}.csv and transactions_{timestamp}.csv")