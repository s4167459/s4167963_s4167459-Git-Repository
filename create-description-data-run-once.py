import sqlite3
import csv

# Path to your files
db_path = "climate.db"
csv_path = "description.csv"

# Connect to database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create the new table
cur.execute("""
    CREATE TABLE IF NOT EXISTS WeatherDescription (
        Field TEXT PRIMARY KEY,
        Description TEXT
    );
""")

# Read the CSV and insert into table
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT OR REPLACE INTO WeatherDescription (Field, Description)
            VALUES (?, ?);
        """, (row['Field'].strip(), row['Description'].strip()))

# Commit and close
conn.commit()
conn.close()

print("WeatherDescription table successfully created and populated.")