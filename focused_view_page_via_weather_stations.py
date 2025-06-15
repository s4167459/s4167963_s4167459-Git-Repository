from level2_focused_utils import get_focused_climate_data, get_available_states, get_state_lat_range
import json

def get_page_html(form_data):
    print("Generating Enhanced Focused View Page...")

    filtered_data = None
    error_message = None
    
    # Form values for preservation
    selected_state = form_data.get("selected_state", "") if form_data else ""
    start_lat = form_data.get("start_lat", "") if form_data else ""
    end_lat = form_data.get("end_lat", "") if form_data else ""
    climate_type = form_data.get("climate_type", "") if form_data else ""
    start_date = form_data.get("start_date", "") if form_data else ""
    end_date = form_data.get("end_date", "") if form_data else ""
    sort_by = form_data.get("sort_by", "name") if form_data else "name"
    sort_order = form_data.get("sort_order", "ASC") if form_data else "ASC"

    if form_data and form_data.get("action") == "analyze":
        try:
            result_json = get_focused_climate_data(form_data)
            result_dict = json.loads(result_json)
            if "error" in result_dict:
                error_message = result_dict["error"]
            else:
                filtered_data = result_dict
        except Exception as e:
            error_message = f"Analysis error: {str(e)}"

    # Get available states and metrics
    available_states = get_available_states()
    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Enhanced Focused Climate Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: auto; padding: 20px; background: #f5f5f5; }
        h1, h2 { color: #2c3e50; }
        .form-container { 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            margin-bottom: 20px; 
        }
        .form-row { display: flex; gap: 20px; margin-bottom: 15px; align-items: end; }
        .form-group { flex: 1; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        select, input { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            font-size: 14px;
        }
        button { 
            background: #3498db; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px;
        }
        button:hover { background: #2980b9; }
        .results-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .summary-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 { margin: 0 0 5px 0; color: #2c3e50; }
        .stat-card .value { font-size: 1.5em; font-weight: bold; color: #3498db; }
        canvas { max-width: 100%; margin: 20px 0; }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px;
            background: white;
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        th { 
            background: #34495e; 
            color: white; 
            position: sticky;
            top: 0;
            cursor: pointer;
        }
        th:hover { background: #2c3e50; }
        tr:nth-child(even) { background: #f8f9fa; }
        .error { color: #e74c3c; background: #fdf2f2; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .sort-indicator { float: right; }
        .filters-summary {
            background: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }
    </style>
</head>
<body>
    <h1>🔍 Enhanced Focused Climate Analysis</h1>
    
    <div class="form-container">
        <form method="post" onsubmit="return validateForm()">
            <div class="form-row">
                <div class="form-group">
                    <label>Select State:</label>
                    <select name="selected_state" id="selectedState" required onchange="updateLatitudeRange()">
                        <option value="">Choose a state...</option>"""

    # Add state options
    for state in available_states:
        selected = "selected" if state == selected_state else ""
        page_html += f'<option value="{state}" {selected}>{state}</option>'

    page_html += f"""
                    </select>
                </div>
                <div class="form-group">
                    <label>Climate Metric:</label>
                    <select name="climate_type" required>
                        <option value="">Choose metric...</option>"""

    # Add metric options
    for metric in valid_metrics:
        selected = "selected" if metric == climate_type else ""
        page_html += f'<option value="{metric}" {selected}>{metric}</option>'

    page_html += f"""
                    </select>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Start Date:</label>
                    <input type="date" name="start_date" value="{start_date}" min="1970-01-01" max="2020-12-31" required>
                </div>
                <div class="form-group">
                    <label>End Date:</label>
                    <input type="date" name="end_date" value="{end_date}" min="1970-01-01" max="2020-12-31" required>
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Start Latitude (optional):</label>
                    <input type="number" name="start_lat" value="{start_lat}" step="0.01" placeholder="e.g., -35.00">
                </div>
                <div class="form-group">
                    <label>End Latitude (optional):</label>
                    <input type="number" name="end_lat" value="{end_lat}" step="0.01" placeholder="e.g., -25.00">
                </div>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label>Sort Results By:</label>
                    <select name="sort_by">
                        <option value="name" {"selected" if sort_by == "name" else ""}>Station Name</option>
                        <option value="latitude" {"selected" if sort_by == "latitude" else ""}>Latitude</option>
                        <option value="longitude" {"selected" if sort_by == "longitude" else ""}>Longitude</option>
                        <option value="avg_value" {"selected" if sort_by == "avg_value" else ""}>Average Value</option>
                        <option value="data_points" {"selected" if sort_by == "data_points" else ""}>Data Points</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Sort Order:</label>
                    <select name="sort_order">
                        <option value="ASC" {"selected" if sort_order == "ASC" else ""}>Ascending</option>
                        <option value="DESC" {"selected" if sort_order == "DESC" else ""}>Descending</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" name="action" value="analyze">🔍 Analyze Climate Data</button>
        </form>
    </div>"""

    if error_message:
        page_html += f'<div class="error">❌ Error: {error_message}</div>'

    if filtered_data:
        summary = filtered_data.get("summary", {})
        filters = filtered_data.get("filters", {})
        
        page_html += f"""
    <div class="results-container">
        <div class="filters-summary">
            <strong>Analysis Summary:</strong> {summary.get('station_count', 0)} stations in {filters.get('state')} 
            for {filters.get('metric')} from {filters.get('start_date')} to {filters.get('end_date')}
            <br><strong>Latitude Range:</strong> {filters.get('lat_range')}
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <h3>Stations Found</h3>
                <div class="value">{summary.get('station_count', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>Overall Average</h3>
                <div class="value">{summary.get('overall_avg', 'N/A')}</div>
            </div>
            <div class="stat-card">
                <h3>Minimum Value</h3>
                <div class="value">{summary.get('min_value', 'N/A')}</div>
            </div>
            <div class="stat-card">
                <h3>Maximum Value</h3>
                <div class="value">{summary.get('max_value', 'N/A')}</div>
            </div>
        </div>
        
        <h2>📈 Climate Trend Over Time</h2>
        <canvas id="trendChart" width="800" height="400"></canvas>
        
        <h2>🏢 Weather Stations Detail</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th onclick="sortTable(6)">First Date <span class="sort-indicator">↕</span></th>
                        <th onclick="sortTable(7)">Last Date <span class="sort-indicator">↕</span></th>
                    </tr>
                </thead>
                <tbody>"""

        stations = filtered_data.get("stations", [])
        for station in stations:
            page_html += f"""
                    <tr>
                        <td>{station.get('name', 'N/A')}</td>
                        <td>{station.get('site_id', 'N/A')}</td>
                        <td>{station.get('latitude', 'N/A')}</td>
                        <td>{station.get('longitude', 'N/A')}</td>
                        <td>{station.get('avg_value', 'N/A')}</td>
                        <td>{station.get('data_points', 'N/A')}</td>
                        <td>{station.get('first_date', 'N/A')}</td>
                        <td>{station.get('last_date', 'N/A')}</td>
                    </tr>"""

        page_html += """
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const trendData = """ + json.dumps(filtered_data.get("timeseries", [])) + """;
        
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: trendData.map(dp => dp.date),
                datasets: [{
                    label: 'Average Climate Value',
                    data: trendData.map(dp => dp.value),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Date' },
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    },
                    y: { 
                        title: { display: true, text: 'Value' },
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    }
                }
            }
        });
        
        // Table sorting functionality
        function sortTable(n) {
            const table = document.querySelector('table');
            let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
            switching = true;
            dir = "asc";
            
            while (switching) {
                switching = false;
                rows = table.rows;
                
                for (i = 1; i < (rows.length - 1); i++) {
                    shouldSwitch = false;
                    x = rows[i].getElementsByTagName("TD")[n];
                    y = rows[i + 1].getElementsByTagName("TD")[n];
                    
                    let xContent = x.innerHTML.toLowerCase();
                    let yContent = y.innerHTML.toLowerCase();
                    
                    // Try to parse as numbers if possible
                    if (!isNaN(xContent) && !isNaN(yContent)) {
                        xContent = parseFloat(xContent);
                        yContent = parseFloat(yContent);
                    }
                    
                    if (dir == "asc") {
                        if (xContent > yContent) {
                            shouldSwitch = true;
                            break;
                        }
                    } else if (dir == "desc") {
                        if (xContent < yContent) {
                            shouldSwitch = true;
                            break;
                        }
                    }
                }
                
                if (shouldSwitch) {
                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                    switching = true;
                    switchcount++;
                } else {
                    if (switchcount == 0 && dir == "asc") {
                        dir = "desc";
                        switching = true;
                    }
                }
            }
        }
    </script>"""

    page_html += """
    <script>
        function validateForm() {
            const startDate = document.querySelector('input[name="start_date"]').value;
            const endDate = document.querySelector('input[name="end_date"]').value;
            const startLat = document.querySelector('input[name="start_lat"]').value;
            const endLat = document.querySelector('input[name="end_lat"]').value;
            
            if (startDate && endDate && startDate >= endDate) {
                alert('End date must be later than start date.');
                return false;
            }
            
            if (startLat && endLat && parseFloat(startLat) > parseFloat(endLat)) {
                alert('End latitude must be greater than start latitude.');
                return false;
            }
            
            return true;
        }
        
        function updateLatitudeRange() {
            const state = document.getElementById('selectedState').value;
            // You could add AJAX call here to get state-specific lat ranges
            // For now, just show helpful placeholder text
            const startLatInput = document.querySelector('input[name="start_lat"]');
            const endLatInput = document.querySelector('input[name="end_lat"]');
            
            if (state) {
                startLatInput.placeholder = 'Southern latitude (e.g., -45.00)';
                endLatInput.placeholder = 'Northern latitude (e.g., -10.00)';
            }
        }
    </script>

    <p><a href="/">← Back to Landing Page</a></p>
</body>
</html>"""
    
    return page_html