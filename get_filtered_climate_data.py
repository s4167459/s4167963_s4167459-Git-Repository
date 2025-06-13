import sqlite3
import json
from datetime import datetime

def get_filtered_climate_data(form_data):
    start_date = form_data.get('start_date')
    end_date = form_data.get('end_date')
    climate_type = form_data.get('climate_type')
    start_station = int(form_data.get('start_station'))
    end_station = int(form_data.get('end_station'))

    if not (start_date and end_date and climate_type):
        return json.dumps({"error": "Missing parameters"})

    try:
        # Validate date format
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end <= start:
            return json.dumps({"error": "End date must be later than start date."})
        if start.year < 1970 or end.year > 2020:
            return json.dumps({"error": "Date out of range (1970–2020)."})
    except ValueError:
        return json.dumps({"error": "Invalid date format."})

    # Open connection
    conn = sqlite3.connect("database/climate_data.db")
    cur = conn.cursor()

    # Query 1: Line graph (date vs metric)
    line_query = f"""
        SELECT DMY, location, {climate_type}
        FROM weather_data
        WHERE location BETWEEN ? AND ?
          AND DMY BETWEEN ? AND ?
          AND {climate_type} IS NOT NULL
        ORDER BY DMY ASC;
    """
    cur.execute(line_query, (start_station, end_station, start_date, end_date))
    raw_results = cur.fetchall()

    timeseries_data = []
    for date, site, value in raw_results:
        timeseries_data.append({"date": date, "value": value})

    # Query 2: Summary table — sum per state
    bar_query = f"""
        SELECT ws.state, SUM(wd.{climate_type})
        FROM weather_data wd
        JOIN weather_station ws ON wd.location = ws.site_id
        WHERE wd.location BETWEEN ? AND ?
          AND wd.DMY BETWEEN ? AND ?
          AND wd.{climate_type} IS NOT NULL
        GROUP BY ws.state;
    """
    cur.execute(bar_query, (start_station, end_station, start_date, end_date))
    state_totals = cur.fetchall()
    bar_data = [{"state": state, "total": round(total, 2)} for state, total in state_totals]

    conn.close()

    return json.dumps({
        "timeseries": timeseries_data,
        "bar_totals": bar_data
    })

import io
import csv

def get_filtered_climate_data_csv(form_data):
    start_date = form_data.get('start_date')
    end_date = form_data.get('end_date')
    climate_type = form_data.get('climate_type')
    start_station = int(form_data.get('start_station'))
    end_station = int(form_data.get('end_station'))

    if not (start_date and end_date and climate_type):
        return None, "Missing parameters"

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end <= start:
            return None, "End date must be later than start date."
        if start.year < 1970 or end.year > 2020:
            return None, "Date out of range (1970–2020)."
    except ValueError:
        return None, "Invalid date format."

    conn = sqlite3.connect("database/climate_data.db")
    cur = conn.cursor()

    # Query timeseries data for CSV export
    query = f"""
        SELECT DMY, {climate_type}
        FROM weather_data
        WHERE location BETWEEN ? AND ?
          AND DMY BETWEEN ? AND ?
          AND {climate_type} IS NOT NULL
        ORDER BY DMY ASC;
    """

    cur.execute(query, (start_station, end_station, start_date, end_date))
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['date', climate_type])

    for dmy, value in rows:
        # Convert dd/mm/yyyy to yyyy-mm-dd
        day, month, year = dmy.split('/')
        iso_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        writer.writerow([iso_date, value])

    csv_content = output.getvalue()
    output.close()

    return csv_content, None
