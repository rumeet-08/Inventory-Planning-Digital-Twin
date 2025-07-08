
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector  #importing all libraries

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='(password)',  # Use MySQL password
    database='inventory_project'# connecting to MySQL using local connection
)

# Load demand data grouped by SKU and date, grouping data by sku and date, so that repeat orders dont take place
query = """
SELECT                            
    DATE(date_time) AS date,
    sku,
    SUM(quantity_demanded) AS total_demand
FROM demand_data
GROUP BY date, sku
ORDER BY date ASC              
"""
df = pd.read_sql(query, conn) #creating data frame, using sql where we can query using local conn

# Simulate inventory for each SKU
simulation_results = []
reorder_point = 100
order_quantity = 300
lead_time = 3

for sku in df['sku'].unique():  #creating for loop where unique values are returned
    sku_data = df[df['sku'] == sku].copy()
    sku_data['inventory'] = 500
    sku_data['reorder_triggered'] = 'No'
    sku_data['incoming_orders'] = 0
    on_order = []       # creating a df sku_data working copy where only true queries are returned with initial invenotry 500# this line keep list of replenishment

    for i in range(len(sku_data)):  #looping day by day, loops each rows in sku_data
        if i > 0:
            sku_data.iloc[i, sku_data.columns.get_loc('inventory')] = (
                sku_data.iloc[i - 1]['inventory'] #Previous row’s inventory
                - sku_data.iloc[i - 1]['total_demand']# Subtracts previous row’s total demand
                + sku_data.iloc[i - 1]['incoming_orders']#Adds previous row’s incoming orders
            )  #Accesses the cell at row i, column 'inventory' using index-based access,get_loc('inventory') gets the column number for 'inventory'.

        current_inventory = sku_data.iloc[i]['inventory']#returns current inventory

        if current_inventory <= reorder_point:
            sku_data.iloc[i, sku_data.columns.get_loc('reorder_triggered')] = 'Yes'
            on_order.append((i + lead_time, order_quantity))#If current inventory ≤ threshold, mark reorder and schedule an incoming order for (today + lead time).

        if i in [x[0] for x in on_order]: #on_order is a list of tuples like quantity, it checks if there any incoming order for this row i
            arrival_qty = sum([x[1] for x in on_order if x[0] == i]) #If yes, it sums all the quantities scheduled to arrive at this time step i.
            sku_data.iloc[i, sku_data.columns.get_loc('incoming_orders')] = arrival_qty #It writes that total arrival quantity into the 'incoming_orders' column at row i

    simulation_results.append(sku_data) #All the per-day, per-SKU data is collected into a list:

# Combine and plot
final_simulation = pd.concat(simulation_results) #Combines all SKU simulation results into one DataFrame.
example_sku = final_simulation[final_simulation['sku'] == final_simulation['sku'].unique()[0]] #Selects the first unique SKU from the simulation to visualize.

plt.figure(figsize=(10, 5))
plt.plot(example_sku['date'], example_sku['inventory'], marker='o')
plt.axhline(reorder_point, color='r', linestyle='--', label='Reorder Point')
plt.title(f"Inventory Level Over Time - {example_sku['sku'].iloc[0]}")#title of the plot to show which SKU's inventory is being visualized
plt.xlabel("Date")
plt.ylabel("Inventory Level")
plt.xticks(rotation=45)#rotates the x-axis labels 
plt.legend()
plt.tight_layout()# automatically adjusts the spacing between plot elements
plt.show() #A line chart showing how inventory changes over time for one SKU, helping visualize when to reorder stock.


# Insert final simulation results into MySQL
cursor = conn.cursor()#cursor object from the database connection 

insert_query = """   
INSERT INTO inventory_simulation (
    date, sku, total_demand, inventory, reorder_triggered, incoming_orders
) VALUES (%s, %s, %s, %s, %s, %s)  
"""   # Prepares the SQL insert query, the %s replaced by actual data for each row.

for row in final_simulation.itertuples(index=False): #Loops through each row in the final_simulation df, itertuples() returns each row as a named tuple 
    cursor.execute(insert_query, (
        row.date,
        row.sku,
        int(row.total_demand),
        int(row.inventory),
        row.reorder_triggered,
        int(row.incoming_orders)  # row’s values in a tuple that matches the SQL placeholders. 
    ))

conn.commit() #saves the changes permanently
cursor.close()
conn.close() #Closes the cursor and the database connection to free up resources
print("✅ Simulation results successfully saved to MySQL.") #Confirmation message
