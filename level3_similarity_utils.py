import sqlite3
import json
from datetime import datetime
from collections import defaultdict
import math

def get_station_similarity_data(form_data):
    """Find weather stations with similar rate of change patterns"""
    try:
        # Extract form parameters
        reference_station = form_data.get("reference_station")
        primary_metric = form_data.get("primary_metric")
        secondary_metric = form_data.get("secondary_metric")
        time_period_1_start = form_data.get("period1_start")
        time_period_1_end = form_data.get("period1_end")
        time_period_2_start = form_data.get("period2_start")
        time_period_2_end = form_data.get("period2_end")
        num_similar_stations = int(form_data.get("num_stations", 5))
        
        if not all([reference_station, primary_metric, secondary_metric, 
                   time_period_1_start, time_period_1_end,
                   time_period_2_start, time_period_2_end]):
            return json.dumps({"error": "Missing required parameters"})

        # Validate dates
        try:
            p1_start = datetime.strptime(time_period_1_start, "%Y-%m-%d")
            p1_end = datetime.strptime(time_period_1_end, "%Y-%m-%d")
            p2_start = datetime.strptime(time_period_2_start, "%Y-%m-%d")
            p2_end = datetime.strptime(time_period_2_end, "%Y-%m-%d")
            
            if p1_end <= p1_start or p2_end <= p2_start:
                return json.dumps({"error": "End dates must be later than start dates"})
                
        except ValueError:
            return json.dumps({"error": "Invalid date format"})

        conn = sqlite3.connect("climate.db")
        c = conn.cursor()

        # Get reference station info
        c.execute("SELECT name FROM weather_station WHERE site_id = ?", (reference_station,))
        ref_station_info = c.fetchone()
        if not ref_station_info:
            return json.dumps({"error": "Reference station not found"})

        # Calculate rate of change for reference station
        ref_changes = calculate_rate_of_change(
            c, reference_station, primary_metric, secondary_metric,
            time_period_1_start, time_period_1_end,
            time_period_2_start, time_period_2_end
        )
        
        if not ref_changes:
            return json.dumps({"error": "Insufficient data for reference station"})

        # Get all other stations and calculate their rate of change
        c.execute("""
            SELECT DISTINCT site_id, name, state, latitude, longitude 
            FROM weather_station 
            WHERE site_id != ?
            ORDER BY name
        """, (reference_station,))
        
        all_stations = c.fetchall()
        station_similarities = []

        for station_id, name, state, lat, lon in all_stations:
            station_changes = calculate_rate_of_change(
                c, station_id, primary_metric, secondary_metric,
                time_period_1_start, time_period_1_end,
                time_period_2_start, time_period_2_end
            )
            
            if station_changes:
                # Calculate similarity score
                similarity = calculate_similarity_score(ref_changes, station_changes)
                
                if similarity is not None:
                    station_similarities.append({
                        "station_id": station_id,
                        "name": name,
                        "state": state,
                        "latitude": lat,
                        "longitude": lon,
                        "similarity_score": similarity,
                        "primary_change": station_changes.get(primary_metric, 0),
                        "secondary_change": station_changes.get(secondary_metric, 0),
                        "primary_period1_avg": station_changes.get(f"{primary_metric}_p1_avg", 0),
                        "primary_period2_avg": station_changes.get(f"{primary_metric}_p2_avg", 0),
                        "secondary_period1_avg": station_changes.get(f"{secondary_metric}_p1_avg", 0),
                        "secondary_period2_avg": station_changes.get(f"{secondary_metric}_p2_avg", 0)
                    })

        # Sort by similarity score (lower is more similar)
        station_similarities.sort(key=lambda x: x["similarity_score"])
        
        # Get top N most similar stations
        most_similar = station_similarities[:num_similar_stations]

        conn.close()

        return json.dumps({
            "reference_station": {
                "id": reference_station,
                "name": ref_station_info[0],
                "primary_change": ref_changes.get(primary_metric, 0),
                "secondary_change": ref_changes.get(secondary_metric, 0),
                "primary_period1_avg": ref_changes.get(f"{primary_metric}_p1_avg", 0),
                "primary_period2_avg": ref_changes.get(f"{primary_metric}_p2_avg", 0),
                "secondary_period1_avg": ref_changes.get(f"{secondary_metric}_p1_avg", 0),
                "secondary_period2_avg": ref_changes.get(f"{secondary_metric}_p2_avg", 0)
            },
            "similar_stations": most_similar,
            "parameters": {
                "primary_metric": primary_metric,
                "secondary_metric": secondary_metric,
                "period1": f"{time_period_1_start} to {time_period_1_end}",
                "period2": f"{time_period_2_start} to {time_period_2_end}",
                "num_stations": num_similar_stations
            }
        })

    except Exception as e:
        return json.dumps({"error": str(e)})

def calculate_rate_of_change(cursor, station_id, primary_metric, secondary_metric, 
                           p1_start, p1_end, p2_start, p2_end):
    """Calculate rate of change for both metrics between two time periods"""
    
    def get_period_average(metric, start_date, end_date):
        cursor.execute(f"""
            SELECT AVG(CAST({metric} AS REAL))
            FROM weather_data
            WHERE location = ? 
              AND dmy BETWEEN ? AND ?
              AND {metric} IS NOT NULL
              AND {metric} != ''
        """, (station_id, start_date, end_date))
        
        result = cursor.fetchone()
        return float(result[0]) if result and result[0] is not None else None

    # Get averages for both periods and both metrics
    primary_p1_avg = get_period_average(primary_metric, p1_start, p1_end)
    primary_p2_avg = get_period_average(primary_metric, p2_start, p2_end)
    secondary_p1_avg = get_period_average(secondary_metric, p1_start, p1_end)
    secondary_p2_avg = get_period_average(secondary_metric, p2_start, p2_end)

    # Check if we have sufficient data
    if None in [primary_p1_avg, primary_p2_avg, secondary_p1_avg, secondary_p2_avg]:
        return None

    # Calculate percentage changes
    primary_change = ((primary_p2_avg - primary_p1_avg) / primary_p1_avg * 100) if primary_p1_avg != 0 else 0
    secondary_change = ((secondary_p2_avg - secondary_p1_avg) / secondary_p1_avg * 100) if secondary_p1_avg != 0 else 0

    return {
        primary_metric: primary_change,
        secondary_metric: secondary_change,
        f"{primary_metric}_p1_avg": primary_p1_avg,
        f"{primary_metric}_p2_avg": primary_p2_avg,
        f"{secondary_metric}_p1_avg": secondary_p1_avg,
        f"{secondary_metric}_p2_avg": secondary_p2_avg
    }

def calculate_similarity_score(ref_changes, station_changes):
    """Calculate similarity score using Euclidean distance"""
    try:
        # Get the metric names (first two keys that don't end with '_avg')
        metrics = [key for key in ref_changes.keys() if not key.endswith('_avg')]
        
        if len(metrics) < 2:
            return None
            
        primary_metric, secondary_metric = metrics[0], metrics[1]
        
        # Calculate Euclidean distance between rate of change vectors
        ref_primary = ref_changes[primary_metric]
        ref_secondary = ref_changes[secondary_metric]
        station_primary = station_changes[primary_metric]
        station_secondary = station_changes[secondary_metric]
        
        distance = math.sqrt(
            (ref_primary - station_primary) ** 2 + 
            (ref_secondary - station_secondary) ** 2
        )
        
        return round(distance, 4)
        
    except (KeyError, TypeError, ValueError):
        return None

def get_available_stations():
    """Get list of all weather stations"""
    conn = sqlite3.connect("climate.db")
    c = conn.cursor()
    
    c.execute("""
        SELECT site_id, name, state
        FROM weather_station
        ORDER BY state, name
    """)
    
    stations = c.fetchall()
    conn.close()
    
    return stations

def get_station_metrics_data(station_ids, metrics, start_date, end_date):
    """Get detailed time series data for visualization"""
    conn = sqlite3.connect("climate.db")
    c = conn.cursor()
    
    results = {}
    
    for station_id in station_ids:
        station_data = {}
        
        for metric in metrics:
            c.execute(f"""
                SELECT dmy, CAST({metric} AS REAL)
                FROM weather_data
                WHERE location = ? 
                  AND dmy BETWEEN ? AND ?
                  AND {metric} IS NOT NULL
                  AND {metric} != ''
                ORDER BY dmy
            """, (station_id, start_date, end_date))
            
            rows = c.fetchall()
            station_data[metric] = [
                {"date": row[0], "value": float(row[1])}
                for row in rows if row[1] is not None
            ]
        
        # Get station name
        c.execute("SELECT name FROM weather_station WHERE site_id = ?", (station_id,))
        station_name = c.fetchone()
        
        results[station_id] = {
            "name": station_name[0] if station_name else f"Station {station_id}",
            "data": station_data
        }
    
    conn.close()
    return results