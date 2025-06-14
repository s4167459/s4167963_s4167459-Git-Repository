import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def is_number(val):
    try:
        float(val)
        return True
    except (TypeError, ValueError):
        return False

def get_filtered_climate_data(form_data):
    try:
        start_date = form_data.get("start_date")
        end_date = form_data.get("end_date")
        climate_type = form_data.get("climate_type")
        start_station = int(form_data.get("start_station"))
        end_station = int(form_data.get("end_station"))

        if not (start_date and end_date and climate_type):
            return json.dumps({"error": "Missing required form fields."})

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        if end_dt <= start_dt:
            return json.dumps({"error": "End date must be later than start date."})

        conn = sqlite3.connect("climate.db")
        c = conn.cursor()

        query = f"""
            SELECT dmy, location, {climate_type}
            FROM weather_data
            WHERE location BETWEEN ? AND ?
              AND dmy BETWEEN ? AND ?
              AND {climate_type} IS NOT NULL
            ORDER BY dmy
        """
        c.execute(query, (start_station, end_station, start_date, end_date))
        rows = c.fetchall()

        values_by_date = defaultdict(list)
        for dmy, location, value in rows:
            if is_number(value):
                values_by_date[dmy].append(float(value))

        timeseries = [
            {"date": date, "value": round(sum(vals) / len(vals), 2)}
            for date, vals in sorted(values_by_date.items()) if vals
        ]

        summary_query = f"""
            SELECT ws.state, AVG(CAST(wd.{climate_type} AS FLOAT))
            FROM weather_data wd
            JOIN weather_station ws ON wd.location = ws.site_id
            WHERE wd.dmy BETWEEN ? AND ?
              AND wd.{climate_type} IS NOT NULL
            GROUP BY ws.state
            ORDER BY ws.state
        """
        c.execute(summary_query, (start_date, end_date))
        summary_rows = c.fetchall()

        bar_totals = [{"state": state, "total": round(avg_val, 2)} for state, avg_val in summary_rows]

        conn.close()

        return json.dumps({
            "timeseries": timeseries,
            "bar_totals": bar_totals
        })

    except Exception as e:
        return json.dumps({"error": str(e)})
