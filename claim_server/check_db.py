import sqlite3

# Check audit.db
print("Checking audit.db:")
conn = sqlite3.connect('audit.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', tables)
conn.close()

# Check app.db
print("\nChecking app.db:")
conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:', tables)
conn.close()