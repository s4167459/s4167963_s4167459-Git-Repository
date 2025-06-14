import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def get_similarity_data(form_data):
    start_date = form_data.get("start_date")
    end_date = form_data.get("end_date")
    reference_metric = form_data.get("reference_metric")
    selected_others = form_data.get("other_metrics")

    if not (start_date and end_date and reference_metric):
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

    if isinstance(selected_others, str):
        selected_others = [selected_others]
    elif not selected_others:
        selected_others = []

    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()

    results_by_metric = {}

    def parse_date(dmy):
        try:
            if '/' in dmy:
                day, month, year = map(int, dmy.split('/'))
                return f"{year:04d}-{month:02d}-{day:02d}"
            else:
                datetime.strptime(dmy, "%Y-%m-%d")  # validate
                return dmy
        except Exception:
            return None

    def fetch_averaged_series(metric):
        cur.execute(f"""
            SELECT DMY, {metric}
            FROM weather_data
            WHERE DMY BETWEEN ? AND ? AND {metric} IS NOT NULL
        """, (start_date, end_date))
        rows = cur.fetchall()

        value_by_date = defaultdict(list)
        for dmy, val in rows:
            iso_date = parse_date(dmy)
            if iso_date and val is not None:
                try:
                    value_by_date[iso_date].append(float(val))
                except ValueError:
                    continue

        averaged = []
        for date, vals in sorted(value_by_date.items()):
            avg = sum(vals) / len(vals)
            averaged.append({"date": date, "value": round(avg, 2)})
        return averaged

    # Fetch reference metric
    ref_series = fetch_averaged_series(reference_metric)

    # Fetch other metrics
    for metric in selected_others:
        results_by_metric[metric] = fetch_averaged_series(metric)

    conn.close()

    return json.dumps({
        "reference": reference_metric,
        "reference_series": ref_series,
        "other_series": results_by_metric
    })
