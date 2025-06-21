from filtered_climate_utils import get_filtered_climate_data
import json

def get_page_html(form_data):
    print("Generating Focused View Page...")

    filtered_data = None
    selected_metric = None

    if form_data:
        try:
            selected_metric = form_data.get("climate_type")
            result_json = get_filtered_climate_data(form_data)
            result_dict = json.loads(result_json)
            if "error" in result_dict:
                print("Data error:", result_dict["error"])
                filtered_data = None
            else:
                filtered_data = result_dict
        except Exception as e:
            print("Failed to get filtered data:", e)

    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    metric_units = {
        "precipitation": "mm",
        "evaporation": "mm",
        "maxTemp": "°C",
        "minTemp": "°C",
        "sunshine": "hours",
        "humid00": "%", "humid03": "%", "humid06": "%", "humid09": "%",
        "humid12": "%", "humid15": "%", "humid18": "%", "humid21": "%",
        "okta00": "oktas", "okta03": "oktas", "okta06": "oktas", "okta09": "oktas",
        "okta12": "oktas", "okta15": "oktas", "okta18": "oktas", "okta21": "oktas"
    }

    y_axis_label = metric_units.get(selected_metric, "Value")

    station_ranges = {
        "WA": (1007, 13017), "VIC": (76031, 90015), "TAS": (91107, 99005), "SA": (16001, 18115),
        "QLD": (28004, 44021), "NT": (14015, 15602), "NSW": (48027, 75041),
        "AET": (200283, 200288), "AAT": (300000, 300004)
    }

    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Focused View by Climate Metric</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        label {{ display: inline-block; margin-top: 10px; font-weight: bold; }}
        select, input {{ margin: 5px 10px; padding: 5px; }}
        button {{ margin: 10px 10px; padding: 10px 20px; background: #2980b9; color: white; border: none; cursor: pointer; }}
        button:hover {{ background: #1c5980; }}
        canvas {{ max-width: 100%; margin-top: 20px; }}
        .section {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>Focused View by Climate Metric</h1>

    <form method="post">
        <div class="section">
            <h2>Time Range</h2>
            <label>Begin:</label>
            <input type="date" name="start_date" min="1970-01-01" max="2020-12-31" required>
            <label>End:</label>
            <input type="date" name="end_date" min="1970-01-01" max="2020-12-31" required>
            <div id="date-error" style="color:red; font-weight:bold;"></div>
        </div>

        <div class="section">
            <h2>Filters</h2>
            <label>Climate Type:</label>
            <select name="climate_type" required>
    """
    for metric in valid_metrics:
        page_html += f"<option value='{metric}'>{metric}</option>\n"

    page_html += """
            </select>

            <label>Station ID Start Range:</label>
            <select name="start_station" required>
    """
    for state, (start, _) in station_ranges.items():
        page_html += f"<option value='{start}'>{state} ({start})</option>\n"

    page_html += """
            </select>

            <label>Station ID End Range:</label>
            <select name="end_station" required>
    """
    for state, (_, end) in station_ranges.items():
        page_html += f"<option value='{end}'>{state} ({end})</option>\n"

    page_html += """
            </select>
        </div>

        <div class="section">
            <button type="submit" name="action" value="graph">Create graph and csv from specified</button>
        </div>
    </form>

    <div class="section">
        <h2>Climate Trend Graph</h2>
        <p>This graph shows the daily values of the selected climate metric for the selected weather station ID range over the selected date range.</p>
        <canvas id="lineGraph" width="800" height="400"></canvas>
    </div>

    <div class="section">
        <h2>Summary Table (State Totals)</h2>
        <canvas id="summaryGraph" width="800" height="300"></canvas>
        <p>This chart summarizes the total value of the selected climate metric across <strong>all states</strong> for the selected date range.</p>
    </div>
"""

    if filtered_data:
        page_html += f"""
    <script>
        const lineData = {json.dumps(filtered_data.get("timeseries", []))};
        const barData = {json.dumps(filtered_data.get("bar_totals", []))};

        const ctxLine = document.getElementById('lineGraph').getContext('2d');
        const ctxBar = document.getElementById('summaryGraph').getContext('2d');

        new Chart(ctxLine, {{
            type: 'line',
            data: {{
                labels: lineData.map(dp => dp.date),
                datasets: [{{
                    label: 'Climate Value',
                    data: lineData.map(dp => dp.value),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{ title: {{ display: true, text: 'Date' }} }},
                    y: {{ title: {{ display: true, text: '{y_axis_label}' }} }}
                }}
            }}
        }});

        new Chart(ctxBar, {{
            type: 'bar',
            data: {{
                labels: barData.map(dp => dp.state),
                datasets: [{{
                    label: 'Total by State',
                    data: barData.map(dp => dp.total),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, title: {{ display: true, text: '{y_axis_label}' }} }}
                }}
            }}
        }});
    </script>
"""

    page_html += """
    <script>
        document.querySelector("form").addEventListener("submit", function(e) {
            const startDate = document.querySelector("input[name='start_date']").value;
            const endDate = document.querySelector("input[name='end_date']").value;
            const errorDiv = document.getElementById("date-error");
            errorDiv.textContent = "";

            if (startDate && endDate && endDate <= startDate) {
                e.preventDefault();
                errorDiv.textContent = "End date must be after start date.";
            }
        });
    </script>

    <p><a href="/">Back to Landing Page</a></p>
</body>
</html>
"""
    return page_html
