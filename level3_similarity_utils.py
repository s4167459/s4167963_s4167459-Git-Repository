import sqlite3
import json
from datetime import datetime
import math
from collections import defaultdict

def debug(msg):
    """Debug helper function"""
    print(f"DEBUG: {msg}")

def get_available_stations():
    """Get list of all available weather stations"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT site_id, name, state 
        FROM weather_station 
        ORDER BY state, name
    """)
    
    stations = cur.fetchall()
    conn.close()
    return stations

def get_station_metrics_data(station_id, metric, start_date, end_date):
    """Get metric data for a specific station and time period"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    query = f"""
        SELECT DMY, {metric}
        FROM weather_data
        WHERE location = ?
          AND {metric} IS NOT NULL
          AND DMY BETWEEN ? AND ?
        ORDER BY DMY
    """
    
    cur.execute(query, (station_id, start_date, end_date))
    data = cur.fetchall()
    conn.close()
    
    # Convert to numeric values
    result = []
    for dmy, value in data:
        try:
            if value is not None:
                result.append((dmy, float(value)))
        except (ValueError, TypeError):
            continue
    
    return result

def calculate_average(data_list):
    """Calculate average from list of (date, value) tuples"""
    if not data_list:
        return None
    
    values = [value for _, value in data_list]
    return sum(values) / len(values) if values else None

def calculate_rate_of_change(period1_avg, period2_avg):
    """Calculate percentage rate of change between two periods"""
    if period1_avg is None or period2_avg is None or period1_avg == 0:
        return None
    
    return ((period2_avg - period1_avg) / abs(period1_avg)) * 100

def calculate_similarity_score(ref_primary_change, ref_secondary_change, 
                             station_primary_change, station_secondary_change):
    """
    Calculate similarity score based on Euclidean distance between rate of change vectors
    Lower score = more similar
    """
    if any(x is None for x in [ref_primary_change, ref_secondary_change, 
                               station_primary_change, station_secondary_change]):
        return float('inf')
    
    # Euclidean distance between the two rate-of-change vectors
    distance = math.sqrt(
        (ref_primary_change - station_primary_change) ** 2 + 
        (ref_secondary_change - station_secondary_change) ** 2
    )
    
    return distance

def get_station_similarity_data(form_data):
    """
    Find weather stations with similar climate change patterns
    Based on rate of change analysis between two time periods
    """
    debug(f"Processing similarity analysis request")
    
    try:
        # Extract form parameters
        reference_station_id = int(form_data.get("reference_station", 0))
        primary_metric = form_data.get("primary_metric", "")
        secondary_metric = form_data.get("secondary_metric", "")
        period1_start = form_data.get("period1_start", "")
        period1_end = form_data.get("period1_end", "")
        period2_start = form_data.get("period2_start", "")
        period2_end = form_data.get("period2_end", "")
        num_stations = int(form_data.get("num_stations", 5))
        
        # Validate inputs
        if not all([reference_station_id, primary_metric, secondary_metric, 
                   period1_start, period1_end, period2_start, period2_end]):
            return json.dumps({"error": "Missing required parameters"})
        
        if primary_metric == secondary_metric:
            return json.dumps({"error": "Primary and secondary metrics must be different"})
        
        # Validate dates
        try:
            datetime.strptime(period1_start, "%Y-%m-%d")
            datetime.strptime(period1_end, "%Y-%m-%d")
            datetime.strptime(period2_start, "%Y-%m-%d")
            datetime.strptime(period2_end, "%Y-%m-%d")
        except ValueError:
            return json.dumps({"error": "Invalid date format"})
        
        debug(f"Reference station: {reference_station_id}")
        debug(f"Metrics: {primary_metric}, {secondary_metric}")
        debug(f"Period 1: {period1_start} to {period1_end}")
        debug(f"Period 2: {period2_start} to {period2_end}")
        
        # Get reference station info
        conn = sqlite3.connect("climate.db")
        cur = conn.cursor()
        
        cur.execute("""
            SELECT site_id, name, latitude, longitude, state, region
            FROM weather_station
            WHERE site_id = ?
        """, (reference_station_id,))
        
        ref_station_row = cur.fetchone()
        if not ref_station_row:
            conn.close()
            return json.dumps({"error": "Reference station not found"})
        
        # Calculate reference station's rate of change
        ref_primary_period1 = get_station_metrics_data(
            reference_station_id, primary_metric, period1_start, period1_end
        )
        ref_primary_period2 = get_station_metrics_data(
            reference_station_id, primary_metric, period2_start, period2_end
        )
        ref_secondary_period1 = get_station_metrics_data(
            reference_station_id, secondary_metric, period1_start, period1_end
        )
        ref_secondary_period2 = get_station_metrics_data(
            reference_station_id, secondary_metric, period2_start, period2_end
        )
        
        # Calculate reference station averages
        ref_primary_period1_avg = calculate_average(ref_primary_period1)
        ref_primary_period2_avg = calculate_average(ref_primary_period2)
        ref_secondary_period1_avg = calculate_average(ref_secondary_period1)
        ref_secondary_period2_avg = calculate_average(ref_secondary_period2)
        
        # Calculate reference station rate of change
        ref_primary_change = calculate_rate_of_change(ref_primary_period1_avg, ref_primary_period2_avg)
        ref_secondary_change = calculate_rate_of_change(ref_secondary_period1_avg, ref_secondary_period2_avg)
        
        if ref_primary_change is None or ref_secondary_change is None:
            conn.close()
            return json.dumps({"error": "Insufficient data for reference station in specified periods"})
        
        debug(f"Reference primary change: {ref_primary_change}%")
        debug(f"Reference secondary change: {ref_secondary_change}%")
        
        # Get all other stations to compare
        cur.execute("""
            SELECT site_id, name, latitude, longitude, state, region
            FROM weather_station
            WHERE site_id != ?
            ORDER BY site_id
        """, (reference_station_id,))
        
        all_stations = cur.fetchall()
        conn.close()
        
        debug(f"Comparing against {len(all_stations)} stations")
        
        # Calculate similarity for each station
        station_similarities = []
        
        for station_row in all_stations:
            station_id, name, lat, lon, state, region = station_row
            
            try:
                # Get station data for both periods and metrics
                station_primary_period1 = get_station_metrics_data(
                    station_id, primary_metric, period1_start, period1_end
                )
                station_primary_period2 = get_station_metrics_data(
                    station_id, primary_metric, period2_start, period2_end
                )
                station_secondary_period1 = get_station_metrics_data(
                    station_id, secondary_metric, period1_start, period1_end
                )
                station_secondary_period2 = get_station_metrics_data(
                    station_id, secondary_metric, period2_start, period2_end
                )
                
                # Calculate averages
                station_primary_period1_avg = calculate_average(station_primary_period1)
                station_primary_period2_avg = calculate_average(station_primary_period2)
                station_secondary_period1_avg = calculate_average(station_secondary_period1)
                station_secondary_period2_avg = calculate_average(station_secondary_period2)
                
                # Calculate rate of change
                station_primary_change = calculate_rate_of_change(
                    station_primary_period1_avg, station_primary_period2_avg
                )
                station_secondary_change = calculate_rate_of_change(
                    station_secondary_period1_avg, station_secondary_period2_avg
                )
                
                # Skip if insufficient data
                if station_primary_change is None or station_secondary_change is None:
                    continue
                
                # Calculate similarity score
                similarity_score = calculate_similarity_score(
                    ref_primary_change, ref_secondary_change,
                    station_primary_change, station_secondary_change
                )
                
                station_similarities.append({
                    "station_id": station_id,
                    "name": name,
                    "latitude": lat,
                    "longitude": lon,
                    "state": state,
                    "region": region,
                    "primary_change": station_primary_change,
                    "secondary_change": station_secondary_change,
                    "primary_period1_avg": station_primary_period1_avg,
                    "primary_period2_avg": station_primary_period2_avg,
                    "secondary_period1_avg": station_secondary_period1_avg,
                    "secondary_period2_avg": station_secondary_period2_avg,
                    "similarity_score": similarity_score
                })
                
            except Exception as e:
                debug(f"Error processing station {station_id}: {e}")
                continue
        
        # Sort by similarity score (lower = more similar) and take top N
        station_similarities.sort(key=lambda x: x["similarity_score"])
        top_similar = station_similarities[:num_stations]
        
        debug(f"Found {len(top_similar)} similar stations")
        
        # Prepare result
        result = {
            "reference_station": {
                "id": ref_station_row[0],
                "name": ref_station_row[1],
                "latitude": ref_station_row[2],
                "longitude": ref_station_row[3],
                "state": ref_station_row[4],
                "region": ref_station_row[5],
                "primary_change": ref_primary_change,
                "secondary_change": ref_secondary_change,
                "primary_period1_avg": ref_primary_period1_avg,
                "primary_period2_avg": ref_primary_period2_avg,
                "secondary_period1_avg": ref_secondary_period1_avg,
                "secondary_period2_avg": ref_secondary_period2_avg
            },
            "similar_stations": top_similar,
            "parameters": {
                "primary_metric": primary_metric,
                "secondary_metric": secondary_metric,
                "period1": f"{period1_start} to {period1_end}",
                "period2": f"{period2_start} to {period2_end}",
                "num_stations_requested": num_stations
            }
        }
        
        return json.dumps(result)
        
    except Exception as e:
        debug(f"Error in similarity analysis: {e}")
        return json.dumps({"error": f"Analysis failed: {str(e)}"})


def get_station_data_quality_summary(station_id, metric, start_date, end_date):
    """Get data quality summary for a station and metric"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    quality_field = f"{metric}Qual"
    
    query = f"""
        SELECT {quality_field}, COUNT(*) as count
        FROM weather_data
        WHERE location = ?
          AND {metric} IS NOT NULL
          AND DMY BETWEEN ? AND ?
        GROUP BY {quality_field}
        ORDER BY count DESC
    """
    
    cur.execute(query, (station_id, start_date, end_date))
    quality_data = cur.fetchall()
    conn.close()
    
    return quality_data


def get_data_coverage_summary(station_id, start_date, end_date):
    """Get data coverage summary for a station across all metrics"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    metrics = [
        "precipitation", "evaporation", "maxtemp", "mintemp", 
        "sunshine", "humid00", "humid03", "humid06", "humid09", 
        "humid12", "humid15", "humid18", "humid21"
    ]
    
    coverage = {}
    
    for metric in metrics:
        query = f"""
            SELECT COUNT(*) as total_records,
                   COUNT({metric}) as valid_records
            FROM weather_data
            WHERE location = ?
              AND DMY BETWEEN ? AND ?
        """
        
        cur.execute(query, (station_id, start_date, end_date))
        result = cur.fetchone()
        
        if result and result[0] > 0:
            coverage[metric] = {
                "total_records": result[0],
                "valid_records": result[1],
                "coverage_percentage": (result[1] / result[0]) * 100 if result[0] > 0 else 0
            }
    
    conn.close()
    return coverage


def validate_metric_name(metric):
    """Validate that metric name exists in the database"""
    valid_metrics = [
        "precipitation", "evaporation", "maxtemp", "mintemp", 
        "sunshine", "humid00", "humid03", "humid06", "humid09", 
        "humid12", "humid15", "humid18", "humid21", "raindaysnum"
    ]
    
    return metric.lower() in valid_metrics


def get_station_location_info(station_id):
    """Get detailed location information for a station"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT site_id, name, latitude, longitude, state, region
        FROM weather_station
        WHERE site_id = ?
    """, (station_id,))
    
    result = cur.fetchone()
    conn.close()
    
    if result:
        return {
            "station_id": result[0],
            "name": result[1],
            "latitude": result[2],
            "longitude": result[3],
            "state": result[4],
            "region": result[5]
        }
    
    return None


def get_temporal_data_range(station_id, metric):
    """Get the temporal range of available data for a station and metric"""
    conn = sqlite3.connect("climate.db")
    cur = conn.cursor()
    
    query = f"""
        SELECT MIN(DMY) as earliest_date,
               MAX(DMY) as latest_date,
               COUNT(*) as total_records
        FROM weather_data
        WHERE location = ?
          AND {metric} IS NOT NULL
          AND DMY != ''
    """
    
    cur.execute(query, (station_id,))
    result = cur.fetchone()
    conn.close()
    
    if result:
        return {
            "earliest_date": result[0],
            "latest_date": result[1],
            "total_records": result[2]
        }
    
    return None