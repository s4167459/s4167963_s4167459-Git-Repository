import sqlite3
import json
import csv
import io
from datetime import datetime
from collections import defaultdict


def determine_granularity(start_date, end_date):
    delta = (end_date - start_date).days
    if delta <= 90:
        return 'daily'
    elif delta <= 730:
        return 'monthly'
    else:
        return 'yearly'


def parse_dmy_to_date(dmy_str):
    try:
        return datetime.strptime(dmy_str, "%d/%m/%Y")
    except:
        return None


def aggregate_by_granularity(data, granularity):
    grouped = defaultdict(list)
    for dmy, value in data:
        date_obj = parse_dmy_to_date(dmy)
        if not date_obj or value is None:
            continue
        if granularity == 'daily':
            key = date_obj.strftime("%Y-%m-%d")
        elif granularity == 'monthly':
            key = date_obj.strftime("%Y-%m")
        else:
            key = date_obj.strftime("%Y")
        grouped[key].append(value)
    aggregated = {k: sum(v)/len(v) for k, v in grouped.items() if v}
    return aggregated


def calculate_percentage_change(values_dict, split_date):
    first_period = []
    second_period = []
    for date_str, value in values_dict.items():
        if len(date_str) == 10:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        elif len(date_str) == 7:
            date_obj = datetime.strptime(date_str, "%Y-%m")
        else:
            date_obj = datetime.strptime(date_str, "%Y")
        if date_obj < split_date:
            first_period.append(value)
        else:
            second_period.append(value)
    if not first_period or not second_period:
        return None
    avg1 = sum(first_period) / len(first_period)
    avg2 = sum(second_period) / len(second_period)
    if avg1 == 0:
        return None
    return ((avg2 - avg1) / avg1) * 100


def get_similar_climate_metrics(form_data):
    start_date = datetime.strptime(form_data["start_date"], "%Y-%m-%d")
    end_date = datetime.strptime(form_data["end_date"], "%Y-%m-%d")
    reference_metric = form_data["reference_metric"]

    granularity = determine_granularity(start_date, end_date)
    midpoint = start_date + (end_date - start_date) / 2

    metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    conn = sqlite3.connect("database/climate_data.db")
    cur = conn.cursor()

    metric_changes = {}

    for metric in metrics:
        query = f"""
            SELECT DMY, {metric}
            FROM weather_data
            WHERE {metric} IS NOT NULL
              AND DMY != ''
              AND DMY BETWEEN ? AND ?
        """
        cur.execute(query, (form_data["start_date"], form_data["end_date"]))
        rows = cur.fetchall()
        aggregated = aggregate_by_granularity(rows, granularity)
        change = calculate_percentage_change(aggregated, midpoint)
        if change is not None:
            metric_changes[metric] = change

    conn.close()

    if reference_metric not in metric_changes:
        return json.dumps({"error": "Reference metric not found or lacks data."})

    reference_change = metric_changes[reference_metric]
    similarities = []
    for metric, change in metric_changes.items():
        if metric == reference_metric:
            continue
        similarity = abs(change - reference_change)
        similarities.append((metric, change, similarity))

    similarities.sort(key=lambda x: x[2])
    result = [{"metric": m, "change": round(c, 2)} for m, c, _ in similarities]

    return json.dumps({
        "reference_metric": reference_metric,
        "reference_change": round(reference_change, 2),
        "similar_metrics": result
    })


def get_similar_climate_metrics_csv(form_data):
    json_result = json.loads(get_similar_climate_metrics(form_data))
    output = io.StringIO()
    writer = csv.writer(output)

    if "error" in json_result:
        writer.writerow(["Error"])
        writer.writerow([json_result["error"]])
    else:
        writer.writerow(["Reference Metric", json_result["reference_metric"]])
        writer.writerow(["Reference Change (%)", json_result["reference_change"]])
        writer.writerow([])
        writer.writerow(["Similar Metric", "Change (%)"])
        for row in json_result["similar_metrics"]:
            writer.writerow([row["metric"], row["change"]])

    return output.getvalue()
