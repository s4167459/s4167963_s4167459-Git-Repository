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

def get_focused_climate_data(form_data):
    """Enhanced focused view with state selection, latitude filtering, and sorting"""
    try:
        start_date = form_data.get("start_date")
        end_date = form_data.get("end_date")
        climate_type = form_data.get("climate_type")
        selected_state = form_data.get("selected_state")
        start_lat = form_data.get("start_lat")
        end_lat = form_data.get("end_lat")
        sort_by = form_data.get("sort_by", "date")
        sort_order = form_data.get("sort_order", "ASC")

        if not (start_date and end_date and climate_type and selected_state):
            return json.dumps({"error": "Missing required form fields."})

        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        if end_dt <= start_dt:
            return json.dumps({"error": "End date must be later than start date."})

        conn = sqlite3.connect("climate.db")
        c = conn.cursor()

        # Build the WHERE clause for latitude filtering
        lat_filter = ""
        params = [selected_state, start_date, end_date]
        
        if start_lat and end_lat:
            try:
                start_lat_val = float(start_lat)
                end_lat_val = float(end_lat)
                if start_lat_val > end_lat_val:
                    start_lat_val, end_lat_val = end_lat_val, start_lat_val
                lat_filter = "AND ws.latitude BETWEEN ? AND ?"
                params.extend([start_lat_val, end_lat_val])
            except ValueError:
                return json.dumps({"error": "Invalid latitude values."})

        # Get detailed station data for table
        detail_query = f"""
            SELECT ws.name, ws.site_id, ws.latitude, ws.longitude, 
                   AVG(CAST(wd.{climate_type} AS REAL)) as avg_value,
                   COUNT(wd.{climate_type}) as data_points,
                   MIN(wd.dmy) as first_date,
                   MAX(wd.dmy) as last_date
            FROM weather_station ws
            JOIN weather_data wd ON ws.site_id = wd.location
            WHERE ws.state = ? 
              AND wd.dmy BETWEEN ? AND ?
              AND wd.{climate_type} IS NOT NULL
              AND wd.{climate_type} != ''
              {lat_filter}
            GROUP BY ws.name, ws.site_id, ws.latitude, ws.longitude
            HAVING COUNT(wd.{climate_type}) > 0
        """
        
        # Add sorting
        sort_columns = {
            "name": "ws.name",
            "latitude": "ws.latitude", 
            "longitude": "ws.longitude",
            "avg_value": "avg_value",
            "data_points": "data_points",
            "date": "first_date"
        }
        
        if sort_by in sort_columns:
            detail_query += f" ORDER BY {sort_columns[sort_by]} {sort_order}"
        else:
            detail_query += " ORDER BY ws.name ASC"

        c.execute(detail_query, params)
        station_details = c.fetchall()

        # Get timeseries data (averaged across all matching stations)
        timeseries_query = f"""
            SELECT wd.dmy, AVG(CAST(wd.{climate_type} AS REAL)) as avg_value
            FROM weather_station ws
            JOIN weather_data wd ON ws.site_id = wd.location
            WHERE ws.state = ? 
              AND wd.dmy BETWEEN ? AND ?
              AND wd.{climate_type} IS NOT NULL
              AND wd.{climate_type} != ''
              {lat_filter}
            GROUP BY wd.dmy
            HAVING COUNT(wd.{climate_type}) > 0
            ORDER BY wd.dmy
        """
        
        c.execute(timeseries_query, params)
        timeseries_rows = c.fetchall()

        timeseries = [
            {"date": date, "value": round(float(value), 2)}
            for date, value in timeseries_rows
        ]

        # Format station details for the table
        stations = []
        for row in station_details:
            name, site_id, lat, lon, avg_val, data_points, first_date, last_date = row
            stations.append({
                "name": name,
                "site_id": site_id,
                "latitude": round(float(lat), 4) if lat else None,
                "longitude": round(float(lon), 4) if lon else None,
                "avg_value": round(float(avg_val), 2) if avg_val else None,
                "data_points": data_points,
                "first_date": first_date,
                "last_date": last_date
            })

        # Get state summary for context
        summary_query = f"""
            SELECT COUNT(DISTINCT ws.site_id) as station_count,
                   AVG(CAST(wd.{climate_type} AS REAL)) as overall_avg,
                   MIN(CAST(wd.{climate_type} AS REAL)) as min_value,
                   MAX(CAST(wd.{climate_type} AS REAL)) as max_value
            FROM weather_station ws
            JOIN weather_data wd ON ws.site_id = wd.location
            WHERE ws.state = ? 
              AND wd.dmy BETWEEN ? AND ?
              AND wd.{climate_type} IS NOT NULL
              AND wd.{climate_type} != ''
              {lat_filter}
        """
        
        c.execute(summary_query, params)
        summary_row = c.fetchone()
        
        summary = {}
        if summary_row:
            station_count, overall_avg, min_val, max_val = summary_row
            summary = {
                "station_count": station_count,
                "overall_avg": round(float(overall_avg), 2) if overall_avg else None,
                "min_value": round(float(min_val), 2) if min_val else None,
                "max_value": round(float(max_val), 2) if max_val else None
            }

        conn.close()

        return json.dumps({
            "timeseries": timeseries,
            "stations": stations,
            "summary": summary,
            "filters": {
                "state": selected_state,
                "metric": climate_type,
                "start_date": start_date,
                "end_date": end_date,
                "lat_range": f"{start_lat} to {end_lat}" if start_lat and end_lat else "All latitudes"
            }
        })

    except Exception as e:
        return json.dumps({"error": str(e)})

def get_available_states():
    """Get list of available states from database"""
    conn = sqlite3.connect("climate.db")
    c = conn.cursor()
    
    c.execute("SELECT DISTINCT state FROM weather_station WHERE state IS NOT NULL ORDER BY state")
    states = [row[0] for row in c.fetchall()]
    
    conn.close()
    return states

def get_state_lat_range(state):
    """Get latitude range for a specific state"""
    conn = sqlite3.connect("climate.db")
    c = conn.cursor()
    
    c.execute("""
        SELECT MIN(latitude) as min_lat, MAX(latitude) as max_lat
        FROM weather_station 
        WHERE state = ? AND latitude IS NOT NULL
    """, (state,))
    
    result = c.fetchone()
    conn.close()
    
    if result and result[0] is not None and result[1] is not None:
        return {
            "min_lat": round(float(result[0]), 2),
            "max_lat": round(float(result[1]), 2)
        }
    return {"min_lat": -45.0, "max_lat": -10.0}  # Default Australian range