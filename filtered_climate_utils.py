import sqlite3
import json
from datetime import datetime
import io
import csv

def get_filtered_climate_data(form_data):
    start_date = form_data.get('start_date')
    end_date = form_data.get('end_date')
    climate_type = form_data.get('climate_type')
    start_station = int(form_data.get('start_station'))
    end_station = int(form_data.get('end_station'))

    if not (start_date and end_date and climate_type):
        return json.dumps({"error": "Missing parameters"})

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if end <= start:
            return json.dumps({"error": "End date must be later than start date."})
        if start.year < 1970 or end.year > 2020:
            return json.dumps({"error": "Date out of range (1970–2020)."})
    except ValueError:
        return json.dumps({"error": "Invalid date format."})

    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()

    # Line graph: station-level data
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

    # Summary chart: average per state
    bar_query = f"""
        SELECT ws.state, AVG(wd.{climate_type})
        FROM weather_data wd
        JOIN weather_station ws ON wd.location = ws.site_id
        WHERE wd.DMY BETWEEN ? AND ?
          AND wd.{climate_type} IS NOT NULL
        GROUP BY ws.state;
    """
    cur.execute(bar_query, (start_date, end_date))
    state_averages = cur.fetchall()

    bar_data = [{"state": state, "total": round(avg, 2)} for state, avg in state_averages]

    conn.close()

    return json.dumps({
        "timeseries": timeseries_data,
        "bar_totals": bar_data
    })


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

    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()

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
        day, month, year = dmy.split('/')
        iso_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        writer.writerow([iso_date, value])

    csv_content = output.getvalue()
    output.close()

    return csv_content, None
