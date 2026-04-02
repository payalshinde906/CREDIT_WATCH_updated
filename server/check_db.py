import sqlite3
import os

db_path = 'app.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path} (CWD: {os.getcwd()})")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Schema of purchase_orders table:")
cursor.execute("PRAGMA table_info(purchase_orders);")
columns = cursor.fetchall()
for col in columns:
    print(col)

print("\nNumber of POs in database:")
cursor.execute("SELECT COUNT(*) FROM purchase_orders;")
count = cursor.fetchone()[0]
print(f"Total POs: {count}")

print("\nSample PO data (first 5):")
cursor.execute("SELECT id, po_number, vendor, status, archived FROM purchase_orders LIMIT 5;")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
