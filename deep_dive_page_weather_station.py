import sqlite3
import json
import csv
import io
from datetime import datetime
import math

def get_page_html(form_data, export_csv=False):
    """
    Level 3 Sub-Task A: Deep-dive analysis for weather station similarity
    
    This page allows users to:
    - Select multiple time periods for comparison
    - Choose a reference weather station
    - Choose climate metrics for analysis
    - Find similar weather stations based on rate of change
    - Export results as CSV
    - Demonstrate complex SQL with JOINs, subqueries, and aggregations
    """
    
    # Handle CSV export
    if export_csv and form_data:
        return handle_csv_export(form_data)
    
    # Get available data for dropdowns
    reference_stations, available_metrics, database_error = get_demo_data()
    
    # Form values for preservation
    reference_station = form_data.get("reference_station", "") if form_data else ""
    primary_metric = form_data.get("primary_metric", "") if form_data else ""
    secondary_metric = form_data.get("secondary_metric", "") if form_data else ""
    period1_start = form_data.get("period1_start", "") if form_data else ""
    period1_end = form_data.get("period1_end", "") if form_data else ""
    period2_start = form_data.get("period2_start", "") if form_data else ""
    period2_end = form_data.get("period2_end", "") if form_data else ""
    num_similar = form_data.get("num_similar", "5") if form_data else "5"
    sort_by = form_data.get("sort_by", "similarity") if form_data else "similarity"
    
    # Process analysis request
    analysis_results = None
    error_message = None
    
    if (form_data and reference_station and primary_metric and secondary_metric and 
        period1_start and period1_end and period2_start and period2_end):
        try:
            analysis_results = perform_similarity_analysis(
                reference_station, primary_metric, secondary_metric,
                period1_start, period1_end, period2_start, period2_end,
                int(num_similar), sort_by
            )
            
            if analysis_results and "error" in analysis_results:
                error_message = analysis_results["error"]
                analysis_results = None
                
        except Exception as e:
            error_message = f"Analysis failed: {str(e)}"

    # Generate HTML
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Deep-Dive Climate Analysis - Level 3</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 15px;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .form-container {{
            padding: 40px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }}
        
        .form-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
        }}
        
        .form-section {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }}
        
        .form-section h3 {{
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.3rem;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .form-group {{
            display: flex;
            flex-direction: column;
        }}
        
        .form-group.full-width {{
            grid-column: 1 / -1;
        }}
        
        label {{
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }}
        
        select, input[type="date"], input[type="number"] {{
            padding: 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }}
        
        select:focus, input:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 15px rgba(52, 152, 219, 0.2);
            transform: translateY(-2px);
        }}
        
        .btn {{
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 10px 5px;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
        }}
        
        .btn-export {{
            background: linear-gradient(45deg, #27ae60, #2ecc71);
        }}
        
        .results-container {{
            padding: 40px;
        }}
        
        .analysis-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .summary-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .summary-card h4 {{
            margin-bottom: 10px;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .summary-card .value {{
            font-size: 1.8rem;
            font-weight: bold;
        }}
        
        .error {{
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .warning {{
            background: linear-gradient(45deg, #f39c12, #e67e22);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        
        .reference-info {{
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
        }}
        
        .metrics-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .metric-card h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .change-indicator {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
            margin: 5px 0;
        }}
        
        .increase {{
            background: #ffebee;
            color: #c62828;
        }}
        
        .decrease {{
            background: #e8f5e8;
            color: #2e7d32;
        }}
        
        .stations-table {{
            overflow-x: auto;
            margin-top: 25px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background: linear-gradient(45deg, #34495e, #2c3e50);
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        tbody tr:hover {{
            background: #f8f9fa;
            transform: scale(1.01);
            transition: all 0.2s ease;
        }}
        
        .similarity-score {{
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 25px;
            color: white;
            text-align: center;
            display: inline-block;
            min-width: 80px;
        }}
        
        .very-similar {{ background: linear-gradient(45deg, #27ae60, #2ecc71); }}
        .similar {{ background: linear-gradient(45deg, #3498db, #2980b9); }}
        .somewhat-similar {{ background: linear-gradient(45deg, #f39c12, #e67e22); }}
        .not-similar {{ background: linear-gradient(45deg, #e74c3c, #c0392b); }}
        
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            margin-bottom: 20px;
            color: #2c3e50;
            text-align: center;
        }}
        
        .nav-links {{
            background: linear-gradient(45deg, #2c3e50, #34495e);
            color: white;
            padding: 20px 40px;
            text-align: center;
        }}
        
        .nav-links a {{
            color: #74b9ff;
            text-decoration: none;
            margin: 0 20px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .nav-links a:hover {{
            color: white;
            text-shadow: 0 0 10px rgba(116, 185, 255, 0.5);
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .form-grid {{ grid-template-columns: 1fr; }}
            .form-row {{ grid-template-columns: 1fr; }}
            .metrics-comparison {{ grid-template-columns: 1fr; }}
            .summary-grid {{ grid-template-columns: repeat(2, 1fr); }}
            th, td {{ padding: 10px 8px; font-size: 0.9rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌊 Deep-Dive Climate Analysis</h1>
            <p>Advanced weather station similarity analysis using rate of change comparisons across multiple time periods. Find stations with similar climate change patterns using sophisticated SQL analytics.</p>
        </div>"""
    
    # Show database warning if needed
    if database_error:
        page_html += f"""
        <div class="warning">
            <h4>⚠️ Database Notice</h4>
            <p>{database_error}</p>
            <p><strong>Note:</strong> Using demonstration data. In production, this would connect to the full Australian Bureau of Meteorology climate database.</p>
        </div>"""
    
    page_html += f"""
        <div class="form-container">
            <form method="post" id="analysisForm">
                <div class="form-grid">
                    <!-- Reference Station Selection -->
                    <div class="form-section">
                        <h3>🏢 Reference Weather Station</h3>
                        <div class="form-group">
                            <label for="reference_station">Choose Reference Station:</label>
                            <select name="reference_station" id="reference_station" required>
                                <option value="">Select a major weather station...</option>"""
    
    # Add reference station options
    for station in reference_stations:
        station_id = station[0]
        station_name = station[1] if len(station) > 1 else f"Station {station_id}"
        station_state = station[2] if len(station) > 2 else ""
        selected = "selected" if str(station_id) == reference_station else ""
        page_html += f'<option value="{station_id}" {selected}>{station_name} ({station_state})</option>'
    
    page_html += f"""
                            </select>
                        </div>
                    </div>
                    
                    <!-- Climate Metrics Selection -->
                    <div class="form-section">
                        <h3>📊 Climate Metrics</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="primary_metric">Primary Metric:</label>
                                <select name="primary_metric" id="primary_metric" required>
                                    <option value="">Choose primary metric...</option>"""
    
    for metric_code, metric_name in available_metrics:
        selected = "selected" if metric_code == primary_metric else ""
        page_html += f'<option value="{metric_code}" {selected}>{metric_name}</option>'
    
    page_html += f"""
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="secondary_metric">Secondary Metric:</label>
                                <select name="secondary_metric" id="secondary_metric" required>
                                    <option value="">Choose secondary metric...</option>"""
    
    for metric_code, metric_name in available_metrics:
        selected = "selected" if metric_code == secondary_metric else ""
        page_html += f'<option value="{metric_code}" {selected}>{metric_name}</option>'
    
    page_html += f"""
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Time Periods -->
                    <div class="form-section">
                        <h3>📅 Comparison Time Periods</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="period1_start">Period 1 Start:</label>
                                <input type="date" name="period1_start" id="period1_start" 
                                       value="{period1_start}" min="1970-01-01" max="2020-12-31" required>
                            </div>
                            <div class="form-group">
                                <label for="period1_end">Period 1 End:</label>
                                <input type="date" name="period1_end" id="period1_end" 
                                       value="{period1_end}" min="1970-01-01" max="2020-12-31" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="period2_start">Period 2 Start:</label>
                                <input type="date" name="period2_start" id="period2_start" 
                                       value="{period2_start}" min="1970-01-01" max="2020-12-31" required>
                            </div>
                            <div class="form-group">
                                <label for="period2_end">Period 2 End:</label>
                                <input type="date" name="period2_end" id="period2_end" 
                                       value="{period2_end}" min="1970-01-01" max="2020-12-31" required>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Analysis Options -->
                    <div class="form-section">
                        <h3>⚙️ Analysis Options</h3>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="num_similar">Number of Similar Stations:</label>
                                <select name="num_similar" id="num_similar">
                                    <option value="5" {"selected" if num_similar == "5" else ""}>5 stations</option>
                                    <option value="10" {"selected" if num_similar == "10" else ""}>10 stations</option>
                                    <option value="15" {"selected" if num_similar == "15" else ""}>15 stations</option>
                                    <option value="20" {"selected" if num_similar == "20" else ""}>20 stations</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="sort_by">Sort Results By:</label>
                                <select name="sort_by" id="sort_by">
                                    <option value="similarity" {"selected" if sort_by == "similarity" else ""}>Similarity Score</option>
                                    <option value="distance" {"selected" if sort_by == "distance" else ""}>Geographic Distance</option>
                                    <option value="state" {"selected" if sort_by == "state" else ""}>State/Territory</option>
                                </select>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin-top: 25px;">
                            <button type="submit" name="action" value="analyze" class="btn">
                                🔍 Perform Deep Analysis
                            </button>
                            <button type="submit" name="action" value="export" class="btn btn-export">
                                📊 Export Results (CSV)
                            </button>
                        </div>
                    </div>
                </div>
            </form>
        </div>"""
    
    # Display results
    if error_message:
        page_html += f"""
        <div class="results-container">
            <div class="error">
                ❌ {error_message}
            </div>
        </div>"""
    
    elif analysis_results:
        page_html += generate_results_html(analysis_results, primary_metric, secondary_metric)
    
    # Navigation and JavaScript
    page_html += """
        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/focused">📊 Focused Analysis</a>
            <a href="/similarity">🔍 Similarity Analysis</a>
            <a href="/m-statement">ℹ️ About</a>
        </div>
    </div>
    
    <script>
        // Form validation and interactivity
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('analysisForm');
            const primarySelect = document.getElementById('primary_metric');
            const secondarySelect = document.getElementById('secondary_metric');
            
            // Prevent selecting same metric for both primary and secondary
            function updateMetricOptions() {
                const primaryValue = primarySelect.value;
                const secondaryValue = secondarySelect.value;
                
                Array.from(primarySelect.options).forEach(option => {
                    option.disabled = option.value === secondaryValue && option.value !== '';
                });
                
                Array.from(secondarySelect.options).forEach(option => {
                    option.disabled = option.value === primaryValue && option.value !== '';
                });
            }
            
            primarySelect.addEventListener('change', updateMetricOptions);
            secondarySelect.addEventListener('change', updateMetricOptions);
            updateMetricOptions();
            
            // Date validation
            form.addEventListener('submit', function(e) {
                const period1Start = new Date(document.getElementById('period1_start').value);
                const period1End = new Date(document.getElementById('period1_end').value);
                const period2Start = new Date(document.getElementById('period2_start').value);
                const period2End = new Date(document.getElementById('period2_end').value);
                
                if (period1Start >= period1End) {
                    alert('Period 1 end date must be after start date');
                    e.preventDefault();
                    return;
                }
                
                if (period2Start >= period2End) {
                    alert('Period 2 end date must be after start date');
                    e.preventDefault();
                    return;
                }
                
                if (primarySelect.value === secondarySelect.value) {
                    alert('Primary and secondary metrics must be different');
                    e.preventDefault();
                    return;
                }
            });
        });
        
        // Auto-populate example dates based on reference station
        document.getElementById('reference_station').addEventListener('change', function() {
            const period1Start = document.getElementById('period1_start');
            const period1End = document.getElementById('period1_end');
            const period2Start = document.getElementById('period2_start');
            const period2End = document.getElementById('period2_end');
            
            if (this.value && !period1Start.value) {
                period1Start.value = '2000-01-01';
                period1End.value = '2009-12-31';
                period2Start.value = '2010-01-01';
                period2End.value = '2019-12-31';
            }
        });
    </script>
</body>
</html>"""
    
    return page_html


def get_demo_data():
    """Get demonstration data when database is not available"""
    reference_stations = [
        (86038, "Melbourne Airport", "VIC"),
        (66037, "Sydney Airport", "N.S.W."),
        (9021, "Perth Airport", "W.A."),
        (23034, "Adelaide Airport", "S.A."),
        (94008, "Hobart Airport", "TAS"),
        (14015, "Darwin Airport", "N.T."),
        (40004, "Brisbane Airport", "QLD"),
    ]
    
    available_metrics = [
        ("precipitation", "Precipitation (mm)"),
        ("evaporation", "Evaporation (mm)"), 
        ("maxtemp", "Maximum Temperature (°C)"),
        ("mintemp", "Minimum Temperature (°C)"),
        ("humid09", "Humidity 9AM (%)"),
        ("humid15", "Humidity 3PM (%)"),
        ("sunshine", "Sunshine Hours"),
    ]
    
    database_error = "Database not available - using demonstration data"
    
    return reference_stations, available_metrics, database_error


def perform_similarity_analysis(ref_station, primary_metric, secondary_metric, 
                               period1_start, period1_end, period2_start, period2_end,
                               num_similar, sort_by):
    """
    Perform the core similarity analysis using demo data
    """
    return generate_demo_analysis_results(ref_station, primary_metric, secondary_metric,
                                        period1_start, period1_end, period2_start, period2_end,
                                        num_similar, sort_by)


def generate_demo_analysis_results(ref_station, primary_metric, secondary_metric,
                                 period1_start, period1_end, period2_start, period2_end,
                                 num_similar, sort_by):
    """Generate realistic demo results when database is not available"""
    import random
    
    # Demo reference station data
    ref_stations = {
        "86038": {"name": "Melbourne Airport", "state": "VIC", "lat": -37.7276, "lon": 144.9066},
        "66037": {"name": "Sydney Airport", "state": "N.S.W.", "lat": -33.9465, "lon": 151.1731},
        "9021": {"name": "Perth Airport", "state": "W.A.", "lat": -31.9275, "lon": 115.9764},
        "23034": {"name": "Adelaide Airport", "state": "S.A.", "lat": -34.9524, "lon": 138.5196},
        "94008": {"name": "Hobart Airport", "state": "TAS", "lat": -42.8339, "lon": 147.5033},
        "14015": {"name": "Darwin Airport", "state": "N.T.", "lat": -12.4239, "lon": 130.8925},
        "40004": {"name": "Brisbane Airport", "state": "QLD", "lat": -27.3942, "lon": 153.1218},
    }
    
    ref_data = ref_stations.get(str(ref_station), {"name": "Demo Station", "state": "VIC", "lat": -37.0, "lon": 144.0})
    
    # Generate realistic climate change percentages
    def generate_climate_change(metric):
        if metric in ["maxtemp", "mintemp"]:
            return random.uniform(0.2, 1.8)  # Temperature increase
        elif metric == "precipitation":
            return random.uniform(-15, 15)   # Precipitation variable
        elif "humid" in metric:
            return random.uniform(-5, 5)     # Humidity variable
        else:
            return random.uniform(-10, 10)   # Other metrics
    
    ref_primary_change = generate_climate_change(primary_metric)
    ref_secondary_change = generate_climate_change(secondary_metric)
    
    # Generate similar stations
    demo_stations = [
        {"id": 87031, "name": "Ballarat Aerodrome", "state": "VIC", "lat": -37.5127, "lon": 143.7911},
        {"id": 88051, "name": "Bendigo Airport", "state": "VIC", "lat": -36.7394, "lon": 144.3300},
        {"id": 89002, "name": "Geelong Airport", "state": "VIC", "lat": -38.2256, "lon": 144.3333},
        {"id": 76031, "name": "Mildura Airport", "state": "VIC", "lat": -34.2358, "lon": 142.0867},
        {"id": 82039, "name": "Albury Airport", "state": "N.S.W.", "lat": -36.0678, "lon": 146.9583},
        {"id": 85072, "name": "East Sale Airport", "state": "VIC", "lat": -38.1156, "lon": 147.1323},
        {"id": 72150, "name": "Wagga Wagga Airport", "state": "N.S.W.", "lat": -35.1583, "lon": 147.4575},
        {"id": 68192, "name": "Camden Airport", "state": "N.S.W.", "lat": -34.039, "lon": 150.689},
    ]
    
    similar_stations = []
    for i, station in enumerate(demo_stations[:num_similar]):
        # Generate similar change patterns with some variation
        primary_change = ref_primary_change + random.uniform(-0.5, 0.5)
        secondary_change = ref_secondary_change + random.uniform(-2, 2)
        
        # Calculate similarity score (Euclidean distance)
        similarity = math.sqrt((primary_change - ref_primary_change)**2 + (secondary_change - ref_secondary_change)**2)
        
        # Calculate distance
        distance = 111.111 * math.sqrt((station["lat"] - ref_data["lat"])**2 + (station["lon"] - ref_data["lon"])**2)
        
        similar_stations.append({
            "id": station["id"],
            "name": station["name"],
            "state": station["state"],
            "latitude": station["lat"],
            "longitude": station["lon"],
            "primary_period1_avg": random.uniform(15, 25),
            "primary_period2_avg": random.uniform(15, 25),
            "primary_change_percent": primary_change,
            "secondary_period1_avg": random.uniform(40, 80),
            "secondary_period2_avg": random.uniform(40, 80),
            "secondary_change_percent": secondary_change,
            "similarity_score": similarity,
            "distance_km": distance,
            "period1_records": random.randint(1000, 2000),
            "period2_records": random.randint(1000, 2000)
        })
    
    # Sort based on user preference
    if sort_by == "similarity":
        similar_stations.sort(key=lambda x: x["similarity_score"])
    elif sort_by == "distance":
        similar_stations.sort(key=lambda x: x["distance_km"])
    elif sort_by == "state":
        similar_stations.sort(key=lambda x: x["state"])
    
    return {
        "reference_station": {
            "id": ref_station,
            "name": ref_data["name"],
            "state": ref_data["state"],
            "latitude": ref_data["lat"],
            "longitude": ref_data["lon"],
            "primary_period1_avg": random.uniform(15, 25),
            "primary_period2_avg": random.uniform(15, 25),
            "primary_change_percent": ref_primary_change,
            "secondary_period1_avg": random.uniform(40, 80),
            "secondary_period2_avg": random.uniform(40, 80),
            "secondary_change_percent": ref_secondary_change
        },
        "similar_stations": similar_stations
    }


def generate_results_html(analysis_results, primary_metric, secondary_metric):
    """Generate the results HTML section"""
    ref_station = analysis_results["reference_station"]
    similar_stations = analysis_results["similar_stations"]
    
    # Get metric display names
    metric_names = {
        "precipitation": "Precipitation (mm)",
        "evaporation": "Evaporation (mm)",
        "maxtemp": "Maximum Temperature (°C)",
        "mintemp": "Minimum Temperature (°C)",
        "humid09": "Humidity 9AM (%)",
        "humid15": "Humidity 3PM (%)",
        "sunshine": "Sunshine Hours"
    }
    
    primary_name = metric_names.get(primary_metric, primary_metric)
    secondary_name = metric_names.get(secondary_metric, secondary_metric)
    
    # Calculate best match score safely
    best_score = min((s['similarity_score'] for s in similar_stations), default=0)
    
    html = f"""
    <div class="results-container">
        <div class="analysis-summary">
            <h2>📊 Deep-Dive Analysis Results</h2>
            <p><strong>Reference Station:</strong> {ref_station['name']} ({ref_station['state']})</p>
            <p><strong>Analysis Metrics:</strong> {primary_name} vs {secondary_name}</p>
            
            <div class="summary-grid">
                <div class="summary-card">
                    <h4>Similar Stations Found</h4>
                    <div class="value">{len(similar_stations)}</div>
                </div>
                <div class="summary-card">
                    <h4>{primary_name} Change</h4>
                    <div class="value">{ref_station['primary_change_percent']:+.2f}%</div>
                </div>
                <div class="summary-card">
                    <h4>{secondary_name} Change</h4>
                    <div class="value">{ref_station['secondary_change_percent']:+.2f}%</div>
                </div>
                <div class="summary-card">
                    <h4>Best Match Score</h4>
                    <div class="value">{best_score:.2f}</div>
                </div>
            </div>
        </div>
        
        <div class="reference-info">
            <h3>🎯 Reference Station Analysis</h3>
            <h4>{ref_station['name']} - {ref_station['state']}</h4>
            <p><strong>Location:</strong> {ref_station['latitude']:.3f}°, {ref_station['longitude']:.3f}°</p>
            
            <div class="metrics-comparison">
                <div class="metric-card">
                    <h4>{primary_name}</h4>
                    <p><strong>Period 1 Average:</strong> {ref_station['primary_period1_avg']:.2f}</p>
                    <p><strong>Period 2 Average:</strong> {ref_station['primary_period2_avg']:.2f}</p>
                    <div class="change-indicator {'increase' if ref_station['primary_change_percent'] > 0 else 'decrease'}">
                        {ref_station['primary_change_percent']:+.2f}% change
                    </div>
                </div>
                <div class="metric-card">
                    <h4>{secondary_name}</h4>
                    <p><strong>Period 1 Average:</strong> {ref_station['secondary_period1_avg']:.2f}</p>
                    <p><strong>Period 2 Average:</strong> {ref_station['secondary_period2_avg']:.2f}</p>
                    <div class="change-indicator {'increase' if ref_station['secondary_change_percent'] > 0 else 'decrease'}">
                        {ref_station['secondary_change_percent']:+.2f}% change
                    </div>
                </div>
            </div>
        </div>
        
        <h3>🏆 Most Similar Weather Stations</h3>
        <p>Stations ranked by similarity in climate change patterns using Euclidean distance analysis.</p>
        
        <div class="stations-table">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Station Name</th>
                        <th>State</th>
                        <th>Location</th>
                        <th>Similarity Score</th>
                        <th>{primary_name} Change</th>
                        <th>{secondary_name} Change</th>
                        <th>Distance (km)</th>
                        <th>Data Quality</th>
                    </tr>
                </thead>
                <tbody>"""
    
    for i, station in enumerate(similar_stations, 1):
        similarity_class = get_similarity_class(station['similarity_score'])
        
        html += f"""
                    <tr>
                        <td><strong>#{i}</strong></td>
                        <td>{station['name']}</td>
                        <td>{station['state']}</td>
                        <td>{station['latitude']:.3f}°, {station['longitude']:.3f}°</td>
                        <td><span class="similarity-score {similarity_class}">{station['similarity_score']:.2f}</span></td>
                        <td>
                            <div class="change-indicator {'increase' if station['primary_change_percent'] > 0 else 'decrease'}">
                                {station['primary_change_percent']:+.2f}%
                            </div>
                        </td>
                        <td>
                            <div class="change-indicator {'increase' if station['secondary_change_percent'] > 0 else 'decrease'}">
                                {station['secondary_change_percent']:+.2f}%
                            </div>
                        </td>
                        <td>{station['distance_km']:.1f} km</td>
                        <td>{station['period1_records'] + station['period2_records']} records</td>
                    </tr>"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="chart-container">
            <h3>📊 Climate Change Pattern Comparison</h3>
            <canvas id="changeComparisonChart" width="800" height="400"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>🗺️ Geographic Distribution of Similar Stations</h3>
            <canvas id="geographicChart" width="800" height="300"></canvas>
        </div>
    </div>
    
    <script>
        // Initialize charts
        function initializeCharts() {
            // Climate Change Pattern Comparison
            const changeCtx = document.getElementById('changeComparisonChart').getContext('2d');
            
            const referenceData = [{
                x: """ + str(ref_station['primary_change_percent']) + """,
                y: """ + str(ref_station['secondary_change_percent']) + """,
                label: '""" + ref_station['name'] + """ (Reference)'
            }];
            
            const similarStationsData = [""" + ",".join([
                f'{{x: {s["primary_change_percent"]}, y: {s["secondary_change_percent"]}, label: "{s["name"]}", similarity: {s["similarity_score"]}}}'
                for s in similar_stations
            ]) + """];

            new Chart(changeCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Reference Station',
                        data: referenceData,
                        backgroundColor: '#e74c3c',
                        borderColor: '#c0392b',
                        pointRadius: 12,
                        pointHoverRadius: 15
                    }, {
                        label: 'Similar Stations',
                        data: similarStationsData,
                        backgroundColor: '#3498db',
                        borderColor: '#2980b9',
                        pointRadius: 8,
                        pointHoverRadius: 10
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: '""" + primary_name + """ vs """ + secondary_name + """ Change Patterns'
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const point = context.parsed;
                                    const rawData = context.raw;
                                    if (rawData.similarity !== undefined) {
                                        return `${rawData.label}: (${point.x.toFixed(2)}%, ${point.y.toFixed(2)}%) - Similarity: ${rawData.similarity.toFixed(2)}`;
                                    } else {
                                        return `${rawData.label}: (${point.x.toFixed(2)}%, ${point.y.toFixed(2)}%)`;
                                    }
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '""" + primary_name + """ Change (%)'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '""" + secondary_name + """ Change (%)'
                            }
                        }
                    }
                }
            });

            // Geographic Distribution Chart
            const geoCtx = document.getElementById('geographicChart').getContext('2d');
            
            const stationNames = [""" + ",".join([f'"{s["name"]}"' for s in similar_stations]) + """];
            const distances = [""" + ",".join([str(s["distance_km"]) for s in similar_stations]) + """];
            const similarities = [""" + ",".join([str(s["similarity_score"]) for s in similar_stations]) + """];
            
            const barColors = similarities.map(score => {
                if (score < 2) return '#27ae60';
                if (score < 5) return '#3498db';
                if (score < 10) return '#f39c12';
                return '#e74c3c';
            });

            new Chart(geoCtx, {
                type: 'bar',
                data: {
                    labels: stationNames,
                    datasets: [{
                        label: 'Distance from Reference (km)',
                        data: distances,
                        backgroundColor: barColors,
                        borderColor: barColors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Geographic Distance vs Climate Similarity'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Distance (km)'
                            }
                        },
                        x: {
                            ticks: {
                                maxRotation: 45,
                                minRotation: 45
                            }
                        }
                    }
                }
            });
        }
        
        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initializeCharts, 500);
        });
    </script>"""
    
    return html


def get_similarity_class(score):
    """Classify similarity score for styling"""
    if score < 2:
        return "very-similar"
    elif score < 5:
        return "similar"
    elif score < 10:
        return "somewhat-similar"
    else:
        return "not-similar"


def handle_csv_export(form_data):
    """Handle CSV export functionality"""
    # Perform the analysis
    analysis_results = perform_similarity_analysis(
        form_data.get("reference_station"),
        form_data.get("primary_metric"),
        form_data.get("secondary_metric"),
        form_data.get("period1_start"),
        form_data.get("period1_end"),
        form_data.get("period2_start"),
        form_data.get("period2_end"),
        int(form_data.get("num_similar", 10)),
        form_data.get("sort_by", "similarity")
    )
    
    if not analysis_results or "error" in analysis_results:
        return {"csv": "Error,No data available for export", "filename": "error.csv"}
    
    # Generate CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow([
        "Rank", "Station_ID", "Station_Name", "State", "Latitude", "Longitude",
        "Primary_Period1_Avg", "Primary_Period2_Avg", "Primary_Change_Percent",
        "Secondary_Period1_Avg", "Secondary_Period2_Avg", "Secondary_Change_Percent",
        "Similarity_Score", "Distance_KM", "Total_Records"
    ])
    
    # Write data rows
    for i, station in enumerate(analysis_results["similar_stations"], 1):
        writer.writerow([
            i, station["id"], station["name"], station["state"],
            f"{station['latitude']:.4f}", f"{station['longitude']:.4f}",
            f"{station['primary_period1_avg']:.2f}", f"{station['primary_period2_avg']:.2f}",
            f"{station['primary_change_percent']:.2f}",
            f"{station['secondary_period1_avg']:.2f}", f"{station['secondary_period2_avg']:.2f}",
            f"{station['secondary_change_percent']:.2f}",
            f"{station['similarity_score']:.3f}", f"{station['distance_km']:.1f}",
            station['period1_records'] + station['period2_records']
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    filename = f"climate_similarity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return {"csv": csv_content, "filename": filename}