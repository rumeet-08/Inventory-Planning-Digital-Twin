import pandas as pd
import mysql.connector

# === Step 1: Load the CSV ===
csv_file = r'C:\Users\rvagh\Downloads\demand_data.csv'  # update path if needed
df = pd.read_csv(csv_file)

# === Step 2: Convert date column ===
df['date_time'] = pd.to_datetime(df['date_time'], format='%m/%d/%Y')

# === Step 3: Connect to MySQL ===
conn = mysql.connector.connect(
    host='localhost',
    user='root',              # or your username
    password='DhyanV@09876', # replace with your MySQL password
    database='inventory_project'  # replace if your DB name is different
)
cursor = conn.cursor()

# === Step 4: Create the table (optional - only if not done already) ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS demand_data (
    date_time DATE,
    sku VARCHAR(20),
    quantity_demanded INT,
    customer_id VARCHAR(50),
    order_type VARCHAR(20),
    price DECIMAL(10,2),
    demand_source VARCHAR(50),
    lead_time_days INT
)
""")

# === Step 5: Insert data row by row ===
insert_query = """
INSERT INTO demand_data (
    date_time, sku, quantity_demanded, customer_id, order_type,
    price, demand_source, lead_time_days
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

for row in df.itertuples(index=False):
    cursor.execute(insert_query, (
        row.date_time.date(), row.sku, row.quantity_demanded, row.customer_id,
        row.order_type, float(row.price), row.demand_source, row.lead_time_days
    ))

conn.commit()
print("✅ CSV data loaded successfully into MySQL!")

# === Step 6: Close connection ===
cursor.close()
conn.close()