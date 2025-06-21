import sqlite3
import json
from datetime import datetime
from collections import defaultdict

def debug(msg):
    print(f"DEBUG: {msg}")

def determine_granularity(start_date, end_date):
    delta = (end_date - start_date).days
    debug(f"Determining granularity for delta days: {delta}")
    if delta <= 90:
        return 'daily'
    elif delta <= 730:
        return 'monthly'
    else:
        return 'yearly'

def parse_dmy_to_date(dmy_str):
    try:
        date_obj = datetime.strptime(dmy_str, "%Y-%m-%d")
        return date_obj
    except Exception:
        return None

def aggregate_by_granularity(data, granularity):
    grouped = defaultdict(list)
    debug(f"Aggregating {len(data)} rows by granularity '{granularity}'")
    for dmy, value in data:
        date_obj = parse_dmy_to_date(dmy)
        if not date_obj or value is None:
            continue
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            continue

        if granularity == 'daily':
            key = date_obj.strftime("%Y-%m-%d")
        elif granularity == 'monthly':
            key = date_obj.strftime("%Y-%m")
        else:
            key = date_obj.strftime("%Y")
        grouped[key].append(numeric_value)
    aggregated = {str(k): sum(v) / len(v) for k, v in grouped.items() if v}
    debug(f"Aggregated into {len(aggregated)} groups")
    return aggregated

def get_similar_climate_metrics(form_data):
    debug(f"Received form_data with keys: {list(form_data.keys())}")

    try:
        start_date = datetime.strptime(form_data["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(form_data["end_date"], "%Y-%m-%d")
    except Exception as e:
        return json.dumps({"error": f"Invalid date format: {e}"})

    reference_metric = form_data.get("reference_metric", "")
    selected_metrics = form_data.get("other_metrics", [])

    # Make sure selected_metrics is always a list
    if isinstance(selected_metrics, str):
        selected_metrics = [selected_metrics]
    elif not isinstance(selected_metrics, list):
        selected_metrics = list(selected_metrics)

    debug(f"Reference metric: '{reference_metric}'")
    debug(f"Selected other metrics: {selected_metrics}")

    if not reference_metric:
        return json.dumps({"error": "Reference metric not specified."})

    # Make sure no duplicate of reference_metric in other_metrics
    selected_metrics = [m for m in selected_metrics if m != reference_metric]

    all_metrics = [reference_metric] + selected_metrics
    debug(f"All metrics to process: {all_metrics}")

    granularity = determine_granularity(start_date, end_date)
    debug(f"Using granularity: {granularity}")

    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()

    metric_series = {}

    for metric in all_metrics:
        query = f"""
            SELECT DMY, {metric}
            FROM weather_data
            WHERE {metric} IS NOT NULL
              AND DMY != ''
              AND DMY BETWEEN ? AND ?
        """
        cur.execute(query, (form_data["start_date"], form_data["end_date"]))
        rows = cur.fetchall()
        debug(f"Metric '{metric}' fetched {len(rows)} rows")

        aggregated = aggregate_by_granularity(rows, granularity)
        debug(f"Metric '{metric}' aggregated into {len(aggregated)} groups")

        if not aggregated:
            debug(f"No data found for metric '{metric}', skipping")
            continue

        sorted_dates = sorted(aggregated.keys())
        start_val = aggregated[sorted_dates[0]]
        debug(f"Start value for metric '{metric}' on '{sorted_dates[0]}': {start_val}")

        # **NEW STRONGER CHECK**:
        # Skip metric if start_val is zero or close to zero to avoid wild percent changes
        if start_val is None or abs(start_val) < 1e-6:
            debug(f"Start value for metric '{metric}' is zero or near zero; skipping metric.")
            continue

        series = []
        for d in sorted_dates:
            v = aggregated[d]
            try:
                date_str = d if granularity != 'monthly' else d + "-01"
                percent_change = ((v - start_val) / start_val) * 100
                series.append({"date": date_str, "value": percent_change})
            except Exception:
                continue

        metric_series[metric] = series

    conn.close()

    debug(f"Compiled metric_series keys: {list(metric_series.keys())}")

    if reference_metric not in metric_series:
        return json.dumps({"error": "Reference metric not found or lacks data."})

    others = {k: v for k, v in metric_series.items() if k != reference_metric}
    debug(f"Other metrics series keys: {list(others.keys())}")

    result = {
        "reference": reference_metric,
        "reference_series": metric_series[reference_metric],
        "other_series": others
    }
    debug(f"Result prepared for JSON response")
    print("DEBUG: Final JSON response:")
    print(json.dumps(result))

    return json.dumps(result)
