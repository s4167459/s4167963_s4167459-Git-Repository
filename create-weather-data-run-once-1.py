# ==========================================================
# 🦁 IMPORT SCRIPT CONFIGURATION (Run this file directly)
# ==========================================================
# This script allows you to import data from a CSV file into a SQLite
# database. You can use it to load data into one table at a time.
# You can run this file with: python config.py or python3 config.py
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
CSV_FILE = "WA.csv" #Which CSV file contains the data you want to copy.
TABLE_NAME = "weather_data"  # What name do you want for the table in your database.
CSV_COLUMNS = ["Location","DMY","Precipitation","PrecipQual","RainDaysNum","RainDaysMeasure","Evaporation","EvapQual","EvapDaysNum","MaxTemp","MaxTempQual","MaxTempDaysNum","MinTemp","MinTempQual","MinTempDays","Humid00","Humid00Qual","Humid03","Humid03QUal","Humid06","Humid06Qual","Humid09","Humid09Qual","Humid12","Humid12Qual","Humid15","Humid15Qual","Humid18","Humid18Qual","Humid21","Humid21Qual","Sunshine","SunshineQual","Okta00","Okta00Qual","Okta03","Okta03Qual","Okta06","Okta06Qual","Okta09","Okta09Qual","Okta12","Okta12Qual","Okta15","Okta15Qual","Okta18","Okta18Qual","Okta21","Okta21Qual"]

# ----------------------------------------------------------------------------
# ✅ FLAT TABLE (no lookup tables)
# ----------------------------------------------------------------------------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_data(
    location INTEGER,
    DMY TEXT,
    Precipitation REAL,
    PrecipQual TEXT,
    RainDaysNum INTEGER,
    RainDaysMeasure INTEGER,
    Evaporation REAL,
    EvapQual TEXT,
    EvapDaysNum INTEGER,
    MaxTemp REAL,
    MaxTempQual TEXT,
    MaxTempDaysNum INTEGER,
    MinTemp REAL,
    MinTempQual TEXT,
    MinTempDays INTEGER,
    Humid00 REAL,
    Humid00Qual TEXT,
    Humid03 REAL,
    Humid03QUal TEXT,
    Humid06 REAL,
    Humid06QUal TEXT,
    Humid09 REAL,
    Humid09QUal TEXT,
    Humid12 REAL,
    Humid12Qual TEXT,
    Humid15 REAL,
    Humid15Qual TEXT,
    Humid18 REAL,
    Humid18Qual TEXT,
    Humid21 REAL,
    Humid21Qual TEXT,
    Sunshine REAL,
    SunshineQual TEXT,
    Okta00 REAL,
    Okta00Qual TEXT,
    Okta03 REAL,
    Okta03Qual TEXT,
    Okta06 REAL,
    Okta06Qual TEXT,
    Okta09 REAL,
    Okta09Qual TEXT,
    Okta12 REAL,
    Okta12Qual TEXT,
    Okta15 REAL,
    Okta15Qual TEXT,
    Okta18 REAL,
    Okta18Qual TEXT,
    Okta21 REAL,
    Okta21Qual TEXT,
    PRIMARY KEY (location, DMY),
    FOREIGN KEY (location) REFERENCES weather_station(site_id)
);
"""

COLUMN_MAP = {
    "location": "location",
    "DMY": "dmy",
    "Precipitation": "precipitation",
    "PrecipQual": "precipqual",
    "RainDaysNum": "raindaysnum",
    "RainDaysMeasure": "raindaysmeasure",
    "Evaporation": "Evaporation",
    "EvapQual": "evapqual",
    "EvapDaysNum": "evapdaysnum",
    "MaxTemp": "maxtemp",
    "MaxTempQual": "maxtempqual",
    "MaxTempDaysNum": "maxtempdaysnum",
    "MinTemp": "mintemp",
    "MinTempQual": "mintempqual",
    "MinTempDays": "mintempdays",
    "Humid00": "humid00",
    "Humid00Qual": "humid00qual",
    "Humid03": "humid03",
    "Humid03Qual":"Humid03Qual",
    "Humid06": "Humid06",
    "Humid06Qual": "Humid06Qual",
    "Humid09": "Humid09",
    "Humid09Qual": "Humid09Qual",
    "Humid12": "Humid12",
    "Humid12Qual": "Humid12Qual",
    "Humid15": "Humid12",
    "Humid15Qual": "Humid12Qual",
    "Humid18": "Humid18",
    "Humid18Qual": "Humid18Qual",
    "Humid21": "Humid21",
    "Humid21Qual": "Humid21Qual",
    "Sunshine": "Sunshine",
    "SunshineQual": "SunshineQual",
    "Okta00": "Okta00",
    "Okta00Qual": "Okta00Qual",
    "Okta03": "Okta03",
    "Okta03Qual": "Okta03Qual",
    "Okta06": "Okta06",
    "Okta06Qual": "Okta06Qual",
    "Okta09": "Okta09",
    "Okta09Qual": "Okta09Qual",
    "Okta12": "Okta12",
    "Okta12Qual": "Okta12Qual",
    "Okta15": "Okta12",
    "Okta15Qual": "Okta12Qual",
    "Okta18": "Okta18",
    "Okta18Qual": "Okta18Qual",
    "Okta21": "Okta21",
    "Okta21Qual": "Okta21Qual"
}

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
            conn,
        )

        conn.close()
        print("\n✅ Import complete!")
