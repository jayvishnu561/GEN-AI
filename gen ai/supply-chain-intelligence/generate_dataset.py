import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Parameters
num_records = 2500
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 8, 31)

# Lists for categorical data
suppliers = ['SupplierA', 'SupplierB', 'SupplierC', 'SupplierD', 'SupplierE', 
             'SupplierF', 'SupplierG', 'SupplierH', 'SupplierI', 'SupplierJ']
warehouses = ['WarehouseNY', 'WarehouseLA', 'WarehouseChicago', 'WarehouseTX', 'WarehouseSeattle']
destinations = ['NYC', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
                'San Antonio', 'San Diego', 'Dallas', 'San Jose']
products = ['Product_' + str(i) for i in range(1, 51)]
transport_modes = ['Ground', 'Air', 'Ocean', 'Rail']
weather_conditions = ['Clear', 'Rainy', 'Snowy', 'Stormy', 'Foggy']
statuses = ['Delivered', 'In Transit', 'Pending']

# Distance mapping for reference
distance_map = {
    ('WarehouseNY', 'NYC'): 50,
    ('WarehouseLA', 'Los Angeles'): 30,
    ('WarehouseChicago', 'Chicago'): 40,
    ('WarehouseTX', 'Houston'): 100,
    ('WarehouseSeattle', 'Seattle'): 50,
}

# Generate dataset
data = []
for i in range(num_records):
    shipment_id = f"S{str(i+1).zfill(5)}"
    order_id = f"O{str(random.randint(1, num_records//2)).zfill(5)}"
    product_id = random.choice(products)
    supplier = random.choice(suppliers)
    warehouse = random.choice(warehouses)
    destination = random.choice(destinations)
    
    # Dates
    order_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    ship_date = order_date + timedelta(days=random.randint(1, 5))
    
    # Transport mode affects expected delivery
    transport_mode = random.choice(transport_modes)
    base_days = {'Ground': 15, 'Air': 5, 'Ocean': 30, 'Rail': 10}
    expected_delivery_days = base_days[transport_mode] + random.randint(-2, 2)
    expected_delivery = ship_date + timedelta(days=expected_delivery_days)
    
    # Status determines actual delivery
    status = random.choices(statuses, weights=[60, 35, 5])[0]
    
    if status == 'Delivered':
        # 70% on-time, 20% delayed (1-10 days), 10% severely delayed (>10 days)
        rand_val = random.random()
        if rand_val < 0.70:
            actual_delivery = expected_delivery + timedelta(days=random.randint(0, 1))
        elif rand_val < 0.90:
            actual_delivery = expected_delivery + timedelta(days=random.randint(2, 10))
        else:
            actual_delivery = expected_delivery + timedelta(days=random.randint(11, 30))
    elif status == 'In Transit':
        actual_delivery = None
    else:  # Pending
        actual_delivery = None
    
    # Quantities and inventory
    quantity = random.randint(10, 500)
    inventory_level = random.randint(50, 1000)
    reorder_point = random.randint(100, 300)
    safety_stock = random.randint(50, 150)
    
    # Supplier lead time and actual lead time
    supplier_lead_time = random.randint(5, 20)
    if actual_delivery:
        actual_lead_time = (actual_delivery - order_date).days
    else:
        actual_lead_time = (datetime.now() - order_date).days
    
    # Transportation
    key = (warehouse, destination)
    distance_km = distance_map.get(key, random.randint(500, 3000))
    
    base_cost = distance_km * random.uniform(0.5, 1.5)
    if transport_mode == 'Air':
        base_cost *= 3
    elif transport_mode == 'Ocean':
        base_cost *= 0.5
    
    shipping_cost = round(base_cost + random.gauss(0, base_cost * 0.15), 2)
    
    weather_condition = random.choice(weather_conditions)
    
    # Create row
    row = {
        'shipment_id': shipment_id,
        'order_id': order_id,
        'product_id': product_id,
        'supplier': supplier,
        'warehouse': warehouse,
        'destination': destination,
        'order_date': order_date,
        'ship_date': ship_date,
        'expected_delivery': expected_delivery,
        'actual_delivery': actual_delivery,
        'quantity': quantity,
        'inventory_level': inventory_level,
        'reorder_point': reorder_point,
        'safety_stock': safety_stock,
        'supplier_lead_time': supplier_lead_time,
        'actual_lead_time': actual_lead_time,
        'transport_mode': transport_mode,
        'shipping_cost': shipping_cost,
        'distance_km': distance_km,
        'weather_condition': weather_condition,
        'status': status
    }
    data.append(row)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('supply_chain_data.csv', index=False)
print(f"Dataset created: {len(df)} records")
print(f"Columns: {list(df.columns)}")
print(f"\nDataset Info:")
print(df.info())
print(f"\nFirst few records:")
print(df.head())
