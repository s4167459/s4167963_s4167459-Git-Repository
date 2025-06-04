# ==========================================================
# 🦁 IMPORT SCRIPT CONFIGURATION (Run this file directly)
# ==========================================================
# This script allows you to import data from a CSV file into a SQLite
# database. You can use it to load data into one table at a time.
# You can run this file with: python create-weather-data-run-once.py OR python3 create-weather-data-run-once.py
#
# ***IMPORTANT***
# If using this to populate a single table with data from more than one 
# CSV file you will need to run the file once for each file.
#
# 📝 How to use:
# - Edit the CONFIGURATION section below.
# - Modify the CREATE TABLE SQL depending on the table you are creating.
# - Run this script in the same folder as your CSV file.
# - It will automatically create the database and load the data.
# 
# ✅ NOTE:
# This is a starter script to help you learn and structure your project.
# You will need to modify it to suit your own database design.
# REMEMBER: YOUR ERD should determine the tables in your database.
# After running the script, always inspect the data manually to verify.
#
# 🔒 The core logic is in a separate file (import_core.py) and should not
# need to be changed. If your design is more advanced, you may modify it —
# but test thoroughly to ensure data is handled correctly.
# ==========================================================

from import_core import create_connection, create_table, import_csv_to_table

DATABASE_NAME = "climate.db" # What name do you want for your database.
CSV_FILE = "Location.csv" # Which CSV file contains the data you want to copy.
TABLE_NAME = "weather_station"  # What name do you want for the table in your database.
CSV_COLUMNS = ["Site", "Name", "Lat", "Long", "State", "Region"] # Which columns in your csv file are you copying to the table.

# ----------------------------------------------------------------------
# NORMALIZED TABLE (uses lookup tables for State and Region)
# ----------------------------------------------------------------------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_station (
    site_id INTEGER PRIMARY KEY,
    name TEXT,
    latitude REAL,
    longitude REAL,
    state TEXT,
    region TEXT
);
"""

COLUMN_MAP = {
    "Site": "site_id",
    "Name": "name",
    "Lat": "latitude",
    "Long": "longitude",
    "State": "state",
    "Region": "region"
}

# ----------------------------------------------------------------------
# 🔍 LOOKUP_CONFIG EXPLAINED
# ----------------------------------------------------------------------
# Use this section if you want to normalize columns (e.g., State, Region)
# into separate lookup tables. For each column:
#
# - The **key** (e.g., "State") should match the column name in your CSV.
# - `table_name`: the name of the new lookup table you want to create.
# - `create_sql`: the SQL that defines the lookup table (usually has 'id' and 'name').
# - `lookup_column`: the name of the column that will go into your main table.
#                    This is what your main table will store as a foreign key.
#                    This must match what you have used in the SQL for your main table above.
# - `target_column`: the name of the column in the CSV that contains the original text value.
#                    This is what gets looked up in the lookup table.
#
# Example:
# If your CSV has a column called "State" with values like "WA" or "NSW",
# this config will:
# - Create a separate table called "state" with all unique state names
# - Replace the value "WA" with its ID from the state table (e.g., state_id = 1)
# - Store that ID in the weather_station table as the foreign key "state_id"

# ==========================================================
# 🚦 MAIN EXECUTION 
# Run this file with: python config.py or python3 config.py
# ==========================================================

if __name__ == '__main__':
    print("🚀 Starting import...")
    print(f"📁 Database: {DATABASE_NAME}")
    print(f"📄 CSV File: {CSV_FILE}")

    conn = create_connection(DATABASE_NAME)

    if conn:

        create_table(conn, CREATE_TABLE_SQL)

        import_csv_to_table(
            CSV_FILE,
            TABLE_NAME,
            CSV_COLUMNS,
            COLUMN_MAP,
            conn
        )

        conn.close()
        print("\n✅ Import complete!")
