from filtered_climate_utils import get_filtered_climate_data
import json

def get_page_html(form_data):
    print("Generating Focused View Page...")

    filtered_data = None
    if form_data:
        try:
            action = form_data.get("action")
            if action == "graph":
                result_json = get_filtered_climate_data(form_data)
                result_dict = json.loads(result_json)
                if "error" in result_dict:
                    print("Data error:", result_dict["error"])
                else:
                    filtered_data = result_dict
        except Exception as e:
            print("Failed to get filtered data:", e)

    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

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
        body { font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }
        h1, h2 { color: #2c3e50; }
        label { display: inline-block; margin-top: 10px; font-weight: bold; }
        select, input { margin: 5px 10px; padding: 5px; }
        button { margin: 10px 10px; padding: 10px 20px; background: #2980b9; color: white; border: none; cursor: pointer; }
        button:hover { background: #1c5980; }
        canvas { max-width: 100%; margin-top: 20px; }
        .section { margin-bottom: 30px; }
        .error-tooltip {
            color: red;
            display: none;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Focused View by Climate Metric</h1>

    <form method="post" onsubmit="return validateDates()">
        <div class="section">
            <h2>Time Range</h2>
            <label>Begin:</label>
            <input type="date" id="startDate" name="start_date" min="1970-01-01" max="2020-12-31" required>
            <label>End:</label>
            <input type="date" id="endDate" name="end_date" min="1970-01-01" max="2020-12-31" required>
            <div id="dateError" class="error-tooltip">End date must be later than start date.</div>
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
            <button type="submit" name="action" value="graph">Create graph from specified</button>
        </div>
    </form>

    <div class="section">
        <h2>Climate Trend Graph</h2>
        <canvas id="lineGraph" width="800" height="400"></canvas>
    </div>

    <div class="section">
        <h2>Summary Table (State Averages)</h2>
        <canvas id="summaryGraph" width="800" height="300"></canvas>
    </div>
"""

    if filtered_data:
        page_html += """
    <script>
        const lineData = """ + json.dumps(filtered_data.get("timeseries", [])) + """;
        const barData = """ + json.dumps(filtered_data.get("bar_totals", [])) + """;

        const ctxLine = document.getElementById('lineGraph').getContext('2d');
        const ctxBar = document.getElementById('summaryGraph').getContext('2d');

        new Chart(ctxLine, {
            type: 'line',
            data: {
                labels: lineData.map(dp => dp.date),
                datasets: [{
                    label: 'Average Climate Value',
                    data: lineData.map(dp => dp.value),
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { title: { display: true, text: 'Date' } },
                    y: { title: { display: true, text: 'Value' } }
                }
            }
        });

        new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: barData.map(dp => dp.state),
                datasets: [{
                    label: 'Average by State',
                    data: barData.map(dp => dp.total),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: 'Average Value' } }
                }
            }
        });
    </script>
"""
    page_html += """
    <script>
        function validateDates() {
            const start = document.getElementById("startDate").value;
            const end = document.getElementById("endDate").value;
            const errorBox = document.getElementById("dateError");
            if (start && end && start >= end) {
                errorBox.style.display = "block";
                return false;
            }
            errorBox.style.display = "none";
            return true;
        }
    </script>

    <p><a href="/">Back to Landing Page</a></p>
</body>
</html>
"""
    return page_html

