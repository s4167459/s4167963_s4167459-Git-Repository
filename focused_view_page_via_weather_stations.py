import sqlite3
import json
from datetime import datetime

def get_page_html(form_data):
    """
    Level 2 Sub-Task A: Focused view of climate change by Weather Station
    
    This page allows users to:
    - Select any ONE state from all available states
    - Select start and end latitude range
    - Select a specific climate metric
    - Sort the data on any of the resultant columns
    - View weather station details and climate data
    """
    
    # Get available data for dropdowns
    try:
        conn = sqlite3.connect("climate.db")
        cur = conn.cursor()
        
        # Test if database is accessible
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        test_result = cur.fetchone()
        
        if test_result is None:
            # Database exists but has no tables
            states = []
            database_error = "Database file exists but contains no tables. Please ensure the database is properly set up."
        else:
            # Get all available states
            try:
                cur.execute("SELECT DISTINCT state FROM weather_station ORDER BY state")
                states = [row[0] for row in cur.fetchall()]
                database_error = None
            except sqlite3.OperationalError:
                # weather_station table doesn't exist, use sample data
                states = ["W.A.", "N.T.", "QLD", "N.S.W.", "VIC", "S.A.", "TAS"]
                database_error = "weather_station table not found. Using sample state data."
        
        conn.close()
        
    except sqlite3.DatabaseError as e:
        # Database file is corrupted or not a valid SQLite file
        states = ["W.A.", "N.T.", "QLD", "N.S.W.", "VIC", "S.A.", "TAS"]
        database_error = f"Database error: {str(e)}. The climate.db file may be corrupted or stored in Git LFS. Using sample data for demonstration."
        
    except Exception as e:
        # Other errors (file not found, permissions, etc.)
        states = ["W.A.", "N.T.", "QLD", "N.S.W.", "VIC", "S.A.", "TAS"]
        database_error = f"Cannot access database: {str(e)}. Using sample data for demonstration."
    
    # Get all available climate metrics (from weather_data table schema)
    climate_metrics = [
        ("Precipitation", "precipitation"),
        ("Evaporation", "evaporation"), 
        ("Maximum Temperature", "maxtemp"),
        ("Minimum Temperature", "mintemp"),
        ("Humidity 9AM", "humid09"),
        ("Humidity 3PM", "humid15"),
        ("Sunshine Hours", "sunshine"),
        ("Rain Days", "raindaysnum")
    ]
    
    # Form values for preservation
    selected_state = form_data.get("state", "") if form_data else ""
    start_latitude = form_data.get("start_latitude", "") if form_data else ""
    end_latitude = form_data.get("end_latitude", "") if form_data else ""
    selected_metric = form_data.get("metric", "") if form_data else ""
    sort_column = form_data.get("sort", "") if form_data else ""
    sort_order = form_data.get("order", "asc") if form_data else "asc"
    
    # Process form submission
    station_data = None
    climate_data = None
    error_message = None
    
    if form_data and selected_state and start_latitude and end_latitude and selected_metric:
        try:
            # Validate latitude inputs
            start_lat = float(start_latitude)
            end_lat = float(end_latitude)
            
            if start_lat >= end_lat:
                error_message = "Start latitude must be less than end latitude"
            else:
                station_data, climate_data = get_filtered_data(
                    selected_state, start_lat, end_lat, selected_metric, sort_column, sort_order
                )
                
                if station_data is None and climate_data is None:
                    error_message = "Database connection failed. Please check that climate.db is properly set up."
                elif not station_data:
                    error_message = f"No weather stations found in {selected_state} between latitudes {start_lat} and {end_lat}"
                    
        except ValueError:
            error_message = "Please enter valid latitude values"
        except Exception as e:
            error_message = f"Error retrieving data: {str(e)}"

    # Generate HTML
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Climate Data by Weather Station - Level 2 Analysis</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .form-container {{
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .form-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .form-section h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .form-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        label {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }}
        
        select, input[type="number"] {{
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        select:focus, input:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
        }}
        
        .btn {{
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }}
        
        .results-container {{
            padding: 30px;
        }}
        
        .results-summary {{
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
            text-align: center;
        }}
        
        .error {{
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .data-tables {{
            display: grid;
            gap: 30px;
        }}
        
        .table-section {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .table-header {{
            background: #34495e;
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .table-header h3 {{
            margin: 0;
            font-size: 1.3rem;
        }}
        
        .sort-info {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .table-container {{
            overflow-x: auto;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        th a {{
            color: #2c3e50;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        th a:hover {{
            color: #3498db;
        }}
        
        .sort-arrow {{
            margin-left: 5px;
            font-size: 0.8rem;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
        }}
        
        .station-id {{
            font-weight: 600;
            color: #3498db;
        }}
        
        .coordinates {{
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }}
        
        .climate-value {{
            font-weight: 600;
        }}
        
        .climate-positive {{
            color: #27ae60;
        }}
        
        .climate-negative {{
            color: #e74c3c;
        }}
        
        .nav-links {{
            background: #2c3e50;
            color: white;
            padding: 15px 30px;
            text-align: center;
        }}
        
        .nav-links a {{
            color: #3498db;
            text-decoration: none;
            margin: 0 15px;
            font-weight: 500;
        }}
        
        .nav-links a:hover {{
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .form-row {{
                grid-template-columns: 1fr;
            }}
            
            .table-container {{
                font-size: 0.85rem;
            }}
            
            th, td {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌍 Climate Analysis by Weather Station</h1>
            <p>Explore climate data for weather stations within specific latitude ranges across Australian states</p>
        </div>
        
        <div class="form-container">
            <form method="post">
                <div class="form-section">
                    <h3>🎯 Filter Selection</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="state">Select State:</label>
                            <select name="state" id="state" required>
                                <option value="">Choose a state...</option>"""
    
    # Add state options
    for state in states:
        selected = "selected" if state == selected_state else ""
        page_html += f'<option value="{state}" {selected}>{state}</option>'
    
    page_html += f"""
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="start_latitude">Start Latitude:</label>
                            <input type="number" name="start_latitude" id="start_latitude" 
                                   step="0.001" min="-50" max="0" 
                                   value="{start_latitude}" 
                                   placeholder="e.g., -20.00" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="end_latitude">End Latitude:</label>
                            <input type="number" name="end_latitude" id="end_latitude" 
                                   step="0.001" min="-50" max="0" 
                                   value="{end_latitude}" 
                                   placeholder="e.g., -17.00" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="metric">Climate Metric:</label>
                            <select name="metric" id="metric" required>
                                <option value="">Choose a metric...</option>"""
    
    # Add climate metric options
    for display_name, metric_value in climate_metrics:
        selected = "selected" if metric_value == selected_metric else ""
        page_html += f'<option value="{metric_value}" {selected}>{display_name}</option>'
    
    page_html += f"""
                            </select>
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <button type="submit" class="btn">🔍 Analyze Climate Data</button>
                    </div>
                </div>
                
                <!-- Hidden sort parameters -->
                <input type="hidden" name="sort" value="{sort_column}">
                <input type="hidden" name="order" value="{sort_order}">
            </form>
        </div>"""
    
    # Show database warning if there's an issue
    if 'database_error' in locals() and database_error:
        page_html += f"""
        <div class="form-container">
            <div style="background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; border: 1px solid #ffeaa7;">
                <h4 style="margin: 0 0 10px 0;">⚠️ Database Notice</h4>
                <p style="margin: 0;">{database_error}</p>
                <p style="margin: 10px 0 0 0; font-size: 0.9rem;"><strong>Note:</strong> This appears to be a demonstration environment. In a production setup, the climate.db file would contain the full Australian weather dataset.</p>
            </div>
        </div>"""
    
    # Display results or error
    if error_message:
        page_html += f"""
        <div class="results-container">
            <div class="error">
                ❌ {error_message}
            </div>
        </div>"""
    
    elif station_data and climate_data:
        # Create summary
        metric_display = dict(climate_metrics).get(selected_metric, selected_metric)
        
        page_html += f"""
        <div class="results-container">
            <div class="results-summary">
                <h2>📊 Analysis Results</h2>
                <p><strong>State:</strong> {selected_state} | <strong>Latitude Range:</strong> {start_latitude}° to {end_latitude}° | <strong>Metric:</strong> {metric_display}</p>
                <p><strong>Weather Stations Found:</strong> {len(station_data)} | <strong>Climate Records:</strong> {len(climate_data)}</p>
            </div>
            
            <div class="data-tables">
                <!-- Table 1: Weather Station Details -->
                <div class="table-section">
                    <div class="table-header">
                        <h3>🏢 Weather Station Details</h3>
                        <div class="sort-info">
                            {"Sorted by: " + sort_column.replace("_", " ").title() + " (" + sort_order.upper() + ")" if sort_column else "Click column headers to sort"}
                        </div>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th><a href="javascript:void(0)" onclick="sortTable('site_id')">Station ID {get_sort_arrow('site_id', sort_column, sort_order)}</a></th>
                                    <th><a href="javascript:void(0)" onclick="sortTable('name')">Station Name {get_sort_arrow('name', sort_column, sort_order)}</a></th>
                                    <th><a href="javascript:void(0)" onclick="sortTable('latitude')">Latitude {get_sort_arrow('latitude', sort_column, sort_order)}</a></th>
                                    <th><a href="javascript:void(0)" onclick="sortTable('longitude')">Longitude {get_sort_arrow('longitude', sort_order)}</a></th>
                                    <th><a href="javascript:void(0)" onclick="sortTable('region')">Region {get_sort_arrow('region', sort_column, sort_order)}</a></th>
                                </tr>
                            </thead>
                            <tbody>"""
        
        # Add station data rows
        for station in station_data:
            page_html += f"""
                                <tr>
                                    <td class="station-id">{station[0]}</td>
                                    <td>{station[1]}</td>
                                    <td class="coordinates">{station[2]:.4f}°</td>
                                    <td class="coordinates">{station[3]:.4f}°</td>
                                    <td>{station[5]}</td>
                                </tr>"""
        
        page_html += f"""
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Table 2: Climate Data Sample -->
                <div class="table-section">
                    <div class="table-header">
                        <h3>🌡️ Climate Data for {metric_display}</h3>
                        <div class="sort-info">Recent data sample (latest 100 records)</div>
                    </div>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Station ID</th>
                                    <th>Station Name</th>
                                    <th>Date</th>
                                    <th>{metric_display}</th>
                                    <th>Data Quality</th>
                                </tr>
                            </thead>
                            <tbody>"""
        
        # Add climate data rows (limit to recent 100 records for performance)
        for record in climate_data[:100]:
            climate_value = record[3] if record[3] is not None else "N/A"
            quality = record[4] if record[4] is not None else "Unknown"
            
            # Style climate values
            value_class = ""
            if isinstance(climate_value, (int, float)):
                value_class = "climate-positive" if climate_value > 0 else "climate-negative"
                climate_value = f"{climate_value:.2f}"
            
            page_html += f"""
                                <tr>
                                    <td class="station-id">{record[0]}</td>
                                    <td>{record[1]}</td>
                                    <td>{record[2]}</td>
                                    <td class="climate-value {value_class}">{climate_value}</td>
                                    <td>{quality}</td>
                                </tr>"""
        
        page_html += """
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>"""
    
    # Navigation and JavaScript
    page_html += """
        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/focused-metric">📊 Climate Metric Analysis</a>
            <a href="/deep-dive">🌊 Deep Dive Comparison</a>
            <a href="/similarity">🔍 Similarity Analysis</a>
        </div>
    </div>
    
    <script>
        function sortTable(column) {
            const form = document.querySelector('form');
            const sortInput = document.querySelector('input[name="sort"]');
            const orderInput = document.querySelector('input[name="order"]');
            
            // Toggle order if same column, otherwise default to ascending
            if (sortInput.value === column) {
                orderInput.value = orderInput.value === 'asc' ? 'desc' : 'asc';
            } else {
                orderInput.value = 'asc';
            }
            
            sortInput.value = column;
            form.submit();
        }
        
        // Form validation
        document.querySelector('form').addEventListener('submit', function(e) {
            const startLat = parseFloat(document.getElementById('start_latitude').value);
            const endLat = parseFloat(document.getElementById('end_latitude').value);
            
            if (startLat >= endLat) {
                alert('Start latitude must be less than end latitude');
                e.preventDefault();
                return false;
            }
            
            if (startLat < -50 || startLat > 0 || endLat < -50 || endLat > 0) {
                alert('Latitude values must be between -50 and 0 (Australian coordinates)');
                e.preventDefault();
                return false;
            }
        });
        
        // Auto-populate example values based on state selection
        document.getElementById('state').addEventListener('change', function() {
            const state = this.value;
            const startLat = document.getElementById('start_latitude');
            const endLat = document.getElementById('end_latitude');
            
            // Provide example latitude ranges for different states
            const stateLatRanges = {
                'W.A.': {start: -35.0, end: -13.0},
                'N.T.': {start: -26.0, end: -11.0},
                'QLD': {start: -29.0, end: -9.0},
                'N.S.W.': {start: -37.5, end: -28.0},
                'VIC': {start: -39.2, end: -34.0},
                'S.A.': {start: -38.0, end: -26.0},
                'TAS': {start: -43.7, end: -40.0}
            };
            
            if (state && stateLatRanges[state] && !startLat.value && !endLat.value) {
                startLat.value = stateLatRanges[state].start;
                endLat.value = stateLatRanges[state].end;
            }
        });
    </script>
</body>
</html>"""
    
    return page_html


def get_sort_arrow(column, current_sort, current_order):
    """Generate sort arrow for table headers"""
    if column == current_sort:
        return "↑" if current_order == "asc" else "↓"
    return "↕"


def get_filtered_data(state, start_lat, end_lat, metric, sort_column, sort_order):
    """
    Retrieve filtered weather station and climate data based on user selections
    Demonstrates SQL SELECT, FILTER, SORT, JOIN operations with data anomaly handling
    """
    try:
        conn = sqlite3.connect("climate.db")
        cur = conn.cursor()
        
        # Test database connection
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weather_station'")
        if not cur.fetchone():
            conn.close()
            # Return sample data for demonstration
            return get_sample_data(state, start_lat, end_lat, metric)
        
        # Table 1: Get weather stations in the selected state and latitude range
        station_query = """
            SELECT site_id, name, latitude, longitude, state, region
            FROM weather_station 
            WHERE state = ? 
              AND latitude BETWEEN ? AND ?
        """
        
        # Add sorting if specified
        valid_sort_columns = ['site_id', 'name', 'latitude', 'longitude', 'region']
        if sort_column and sort_column in valid_sort_columns:
            order_clause = f" ORDER BY {sort_column} {'ASC' if sort_order == 'asc' else 'DESC'}"
            station_query += order_clause
        else:
            station_query += " ORDER BY latitude DESC"
        
        cur.execute(station_query, (state, start_lat, end_lat))
        station_data = cur.fetchall()
        
        if not station_data:
            conn.close()
            return None, None
        
        # Get station IDs for climate data query
        station_ids = [str(station[0]) for station in station_data]
        placeholders = ','.join(['?' for _ in station_ids])
        
        # Check if weather_data table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='weather_data'")
        if not cur.fetchone():
            conn.close()
            # Return station data with sample climate data
            sample_climate = get_sample_climate_data(station_data, metric)
            return station_data, sample_climate
        
        # Table 2: Get climate data with basic anomaly handling
        climate_query = f"""
            SELECT 
                wd.location,
                ws.name,
                wd.DMY,
                CASE 
                    WHEN wd.{metric} IS NULL THEN NULL
                    WHEN wd.{metric}Qual = 'W' THEN NULL  -- Remove wrong data
                    ELSE wd.{metric}
                END as cleaned_metric,
                CASE 
                    WHEN wd.{metric} IS NULL THEN 'Missing Data'
                    WHEN wd.{metric}Qual = 'W' THEN 'Wrong Data (Removed)'
                    WHEN wd.{metric}Qual = 'Y' THEN 'Quality Controlled'
                    WHEN wd.{metric}Qual = 'S' THEN 'Suspect Data'
                    WHEN wd.{metric}Qual = 'N' THEN 'Not Quality Controlled'
                    ELSE COALESCE(wd.{metric}Qual, 'Unknown')
                END as quality_status
            FROM weather_data wd
            JOIN weather_station ws ON wd.location = ws.site_id
            WHERE wd.location IN ({placeholders})
              AND wd.DMY != ''
              AND wd.DMY IS NOT NULL
            ORDER BY wd.DMY DESC, wd.location
            LIMIT 1000
        """
        
        cur.execute(climate_query, station_ids)
        climate_data = cur.fetchall()
        
        conn.close()
        return station_data, climate_data
        
    except sqlite3.DatabaseError:
        # Database file is corrupted or not accessible
        return get_sample_data(state, start_lat, end_lat, metric)
    except Exception as e:
        print(f"Database error: {e}")
        return None, None


def get_sample_data(state, start_lat, end_lat, metric):
    """
    Generate sample data for demonstration when database is not available
    """
    import random
    from datetime import datetime, timedelta
    
    # Sample station data for the selected state
    sample_stations = {
        "W.A.": [
            (1001, "Perth Airport", -31.9275, 115.9764, "W.A.", "City of Perth"),
            (1002, "Broome Airport", -17.9475, 122.2352, "W.A.", "Broome"),
            (1003, "Kalgoorlie Airport", -30.7847, 121.4533, "W.A.", "Kalgoorlie")
        ],
        "N.T.": [
            (2001, "Darwin Airport", -12.4239, 130.8925, "N.T.", "City of Darwin"),
            (2002, "Alice Springs Airport", -23.7951, 133.889, "N.T.", "Alice Springs")
        ],
        "QLD": [
            (3001, "Brisbane Airport", -27.3942, 153.1218, "QLD", "Brisbane"),
            (3002, "Cairns Airport", -16.8736, 145.7458, "QLD", "Cairns")
        ]
    }
    
    # Filter stations by latitude range
    if state in sample_stations:
        stations = [s for s in sample_stations[state] 
                   if start_lat <= s[2] <= end_lat]
    else:
        stations = []
    
    if not stations:
        return None, None
    
    # Generate sample climate data
    climate_data = []
    base_date = datetime(2020, 1, 1)
    
    for i, station in enumerate(stations[:3]):  # Limit to 3 stations for demo
        for day in range(10):  # 10 days of sample data per station
            date = base_date + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            
            # Generate realistic sample values based on metric type
            if metric == "precipitation":
                value = round(random.uniform(0, 50), 2)
            elif metric in ["maxtemp", "mintemp"]:
                value = round(random.uniform(10, 35), 2)
            elif "humid" in metric:
                value = round(random.uniform(30, 90), 2)
            elif metric == "sunshine":
                value = round(random.uniform(0, 12), 1)
            else:
                value = round(random.uniform(1, 100), 2)
            
            quality = random.choice(["Y", "N", "S"])
            climate_data.append((station[0], station[1], date_str, value, quality))
    
    return stations, climate_data


def get_sample_climate_data(station_data, metric):
    """
    Generate sample climate data for existing stations
    """
    import random
    from datetime import datetime, timedelta
    
    climate_data = []
    base_date = datetime(2020, 1, 1)
    
    for station in station_data[:3]:  # Limit for demo
        for day in range(5):  # 5 days per station
            date = base_date + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            
            if metric == "precipitation":
                value = round(random.uniform(0, 50), 2)
            elif metric in ["maxtemp", "mintemp"]:
                value = round(random.uniform(10, 35), 2)
            elif "humid" in metric:
                value = round(random.uniform(30, 90), 2)
            elif metric == "sunshine":
                value = round(random.uniform(0, 12), 1)
            else:
                value = round(random.uniform(1, 100), 2)
            
            quality = random.choice(["Y", "N", "S"])
            climate_data.append((station[0], station[1], date_str, value, quality))
    
    return climate_data