import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

days = 180
skus = [f'SKU_{i}' for i in range(1, 11)]
customers = [f'Cust_{i}' for i in range(1, 21)]  # 20 customers/locations
order_types = ['Online', 'Retail', 'Wholesale']
demand_sources = ['Website', 'Mobile App', 'Store', 'Distributor']

base_demands = np.linspace(60, 10, num=10)  # SKU_1 high demand to SKU_10 low

start_date = datetime(2024, 1, 1)  # Starting date

data = []

for sku_idx, sku in enumerate(skus):
    base_demand_val = base_demands[sku_idx]
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        weekday = current_date.weekday()
        
        # Seasonality: Weekdays higher demand, weekends 60%
        if weekday < 5:
            base_demand = base_demand_val
        else:
            base_demand = base_demand_val * 0.6
        
        # Number of orders per day for this SKU (random small number of orders)
        orders_per_day = np.random.randint(1, 5)
        
        for _ in range(orders_per_day):
            demand_qty = max(1, int(np.random.normal(base_demand / orders_per_day, base_demand * 0.1)))
            customer = np.random.choice(customers)
            order_type = np.random.choice(order_types)
            price = round(np.random.uniform(10, 100), 2)  # Random price between $10 and $100
            demand_source = np.random.choice(demand_sources)
            lead_time = np.random.randint(2, 6)  # 2-5 days
            
            data.append({
                'date_time': current_date.strftime('%Y-%m-%d'),
                'sku': sku,
                'quantity_demanded': demand_qty,
                'customer_id': customer,
                'order_type': order_type,
                'price': price,
                'demand_source': demand_source,
                'lead_time_days': lead_time
            })

df = pd.DataFrame(data)

df.to_csv('detailed_demand_dataset_10skus_180days.csv', index=False)

print("Sample of detailed demand data:")
print(df.head(20))