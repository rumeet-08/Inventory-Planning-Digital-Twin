import pandas as pd
import numpy as np
from datetime import datetime, timedelta #for handling dates

np.random.seed(42) #get the same random results each time 

days = 180
skus = [f'SKU_{i}' for i in range(1, 11)]
customers = [f'Cust_{i}' for i in range(1, 21)]  # 20 customers/locations
order_types = ['Online', 'Retail', 'Wholesale']
demand_sources = ['Website', 'Mobile App', 'Store', 'Distributor'] #Simulates 10 SKUs, 20 customers, 3 order types, and 4 demand sources over 180 days

base_demands = np.linspace(60, 10, num=10)  # SKU_1 high demand to SKU_10 low

start_date = datetime(2024, 1, 1)  # Starting date

data = []   #empty list to store 

for sku_idx, sku in enumerate(skus): #Loops through each SKU
    base_demand_val = base_demands[sku_idx] #Assigns the base demand value
    
    for day_offset in range(days):  #Loops through each day
        current_date = start_date + timedelta(days=day_offset) #Calculates the actual calendar date 
        weekday = current_date.weekday()
        
        # Seasonality: Weekdays higher demand, weekends 60%
        if weekday < 5:
            base_demand = base_demand_val
        else:
            base_demand = base_demand_val * 0.6
        
        # Number of orders per day for this SKU (random small number of orders)
        orders_per_day = np.random.randint(1, 5)
        
        for _ in range(orders_per_day):   #Loop through each individual order for that day.
            demand_qty = max(1, int(np.random.normal(base_demand / orders_per_day, base_demand * 0.1))) # normal distribution (bell curve)(mean,dev) centered around average per-order demand.
            customer = np.random.choice(customers)
            order_type = np.random.choice(order_types)
            price = round(np.random.uniform(10, 100), 2)  # Random price between $10 and $100, round off to 2 
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
            }) #Appends a dictionary representing a single order to the data list

df = pd.DataFrame(data) #converts that list into a pandas DataFrame, a tabular structure with rows and columns.

df.to_csv('detailed_demand_dataset_10skus_180days.csv', index=False) 

print("Sample of detailed demand data:")
print(df.head(20)) #Just to overview the dataset
