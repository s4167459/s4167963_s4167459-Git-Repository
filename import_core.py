import sqlite3
import csv
import os

# ====================================================================
# 🧠 SCRIPT - DO NOT MODIFY BELOW THIS LINE (UNLESS FEELING BRAVE 💪)
# ====================================================================

def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def create_table(conn, create_table_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as e:
        print(f"❌ Error creating table: {e}")

def build_lookup_tables(csv_file, conn, lookup_config):
    inserted_ids = {}
    with open(csv_file, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for field, cfg in lookup_config.items():
        table = cfg["table_name"]
        create_sql = cfg["create_sql"]
        column = cfg["target_column"]

        create_table(conn, create_sql)

        values = sorted(set(row[column].strip() for row in rows if row.get(column)))
        cursor = conn.cursor()

        for value in values:
            try:
                cursor.execute(f"INSERT OR IGNORE INTO {table} (name) VALUES (?)", (value,))
            except sqlite3.Error as e:
                print(f"❌ Insert error in '{table}': {e}")
        conn.commit()

        cursor.execute(f"SELECT id, name FROM {table}")
        inserted_ids[field] = {name: id for id, name in cursor.fetchall()}

    return inserted_ids, rows

def import_csv_to_table(csv_file, table_name, csv_columns, column_map, conn,
                        use_lookups=False, lookup_config=None):
    print(f"\n📄 Processing: {csv_file}")

    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return

    lookup_values = {}
    all_rows = []

    if use_lookups and lookup_config:
        lookup_values, all_rows = build_lookup_tables(csv_file, conn, lookup_config)
    else:
        with open(csv_file, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            all_rows = list(reader)

    db_columns = []
    for col in csv_columns:
        if use_lookups and lookup_config and col in lookup_config:
            db_columns.append(lookup_config[col]["lookup_column"])
        else:
            db_columns.append(column_map.get(col, col))

    columns = ", ".join(db_columns)
    placeholders = ", ".join(['?'] * len(db_columns))
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    rows_to_insert = []
    for row in all_rows:
        row_data = []
        for col in csv_columns:
            val = row.get(col, None)
            if use_lookups and lookup_config and col in lookup_values:
                if val is not None:
                    val = lookup_values[col].get(val.strip(), None)
                else:
                    val = None
            row_data.append(val)
        rows_to_insert.append(row_data)

    if not rows_to_insert:
        print("⚠️ No data rows found.")
        return

    print(f"📥 SQL to execute: {insert_sql}")
    print(f"🔍 First 3 parsed rows: {rows_to_insert[:3]}")

    try:
        cursor = conn.cursor()
        cursor.executemany(insert_sql, rows_to_insert)
        conn.commit()
        print(f"✅ Inserted {len(rows_to_insert)} records into '{table_name}'.")
    except sqlite3.Error as e:
        print(f"❌ Error during insertion: {e}")
        return

    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        result = cursor.fetchall()
        print(f"🔎 Sample data from '{table_name}': {result}")
    except Exception as e:
        print(f"⚠️ Could not query table for sample output: {e}")

