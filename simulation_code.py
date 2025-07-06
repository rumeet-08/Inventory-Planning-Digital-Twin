
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

# --- Step 1: Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='DhyanV@09876',  # 🔁 Replace with your actual password
    database='inventory_project'
)

# --- Step 2: Load demand data grouped by SKU and date
query = """
SELECT 
    DATE(date_time) AS date,
    sku,
    SUM(quantity_demanded) AS total_demand
FROM demand_data
GROUP BY date, sku
ORDER BY date ASC
"""
df = pd.read_sql(query, conn)

# --- Step 3: Simulate inventory for each SKU
simulation_results = []
reorder_point = 100
order_quantity = 300
lead_time = 3

for sku in df['sku'].unique():
    sku_data = df[df['sku'] == sku].copy()
    sku_data['inventory'] = 500
    sku_data['reorder_triggered'] = 'No'
    sku_data['incoming_orders'] = 0
    on_order = []

    for i in range(len(sku_data)):
        if i > 0:
            sku_data.iloc[i, sku_data.columns.get_loc('inventory')] = (
                sku_data.iloc[i - 1]['inventory']
                - sku_data.iloc[i - 1]['total_demand']
                + sku_data.iloc[i - 1]['incoming_orders']
            )

        current_inventory = sku_data.iloc[i]['inventory']

        if current_inventory <= reorder_point:
            sku_data.iloc[i, sku_data.columns.get_loc('reorder_triggered')] = 'Yes'
            on_order.append((i + lead_time, order_quantity))

        if i in [x[0] for x in on_order]:
            arrival_qty = sum([x[1] for x in on_order if x[0] == i])
            sku_data.iloc[i, sku_data.columns.get_loc('incoming_orders')] = arrival_qty

    simulation_results.append(sku_data)

# --- Step 4: Combine and plot
final_simulation = pd.concat(simulation_results)
example_sku = final_simulation[final_simulation['sku'] == final_simulation['sku'].unique()[0]]

plt.figure(figsize=(10, 5))
plt.plot(example_sku['date'], example_sku['inventory'], marker='o')
plt.axhline(reorder_point, color='r', linestyle='--', label='Reorder Point')
plt.title(f"Inventory Level Over Time - {example_sku['sku'].iloc[0]}")
plt.xlabel("Date")
plt.ylabel("Inventory Level")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()


# Insert final simulation results into MySQL
cursor = conn.cursor()

insert_query = """
INSERT INTO inventory_simulation (
    date, sku, total_demand, inventory, reorder_triggered, incoming_orders
) VALUES (%s, %s, %s, %s, %s, %s)
"""

for row in final_simulation.itertuples(index=False):
    cursor.execute(insert_query, (
        row.date,
        row.sku,
        int(row.total_demand),
        int(row.inventory),
        row.reorder_triggered,
        int(row.incoming_orders)
    ))

conn.commit()
cursor.close()
conn.close()
print("✅ Simulation results successfully saved to MySQL.")
