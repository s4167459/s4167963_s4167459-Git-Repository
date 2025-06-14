from similar_climate_utils import get_similar_climate_metrics, get_similar_climate_metrics_csv
import json

def get_page_html(form_data, export_csv=False):
    print("Generating Deep-Dive Page...")

    result_data = None
    csv_output = None

    if form_data:
        try:
            if export_csv:
                csv_output = get_similar_climate_metrics_csv(form_data)
            else:
                result_data = json.loads(get_similar_climate_metrics(form_data))
        except Exception as e:
            print("Error while processing form:", e)

    metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Deep-Dive into Metric Similarities</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }
        h1, h2 { color: #2c3e50; }
        label { display: inline-block; margin-top: 10px; font-weight: bold; }
        select, input { margin: 5px 10px; padding: 5px; }
        button { margin: 10px 10px; padding: 10px 20px; background: #27ae60; color: white; border: none; cursor: pointer; }
        button:hover { background: #1e874b; }
        canvas { max-width: 100%; margin-top: 20px; }
        .section { margin-bottom: 30px; }
    </style>
</head>
<body>
    <h1>Deep-Dive into Metric Similarities</h1>

    <form method="post">
        <div class="section">
            <h2>Time Range</h2>
            <label>Begin:</label>
            <input type="date" name="start_date" min="1970-01-01" max="2020-12-31" required>
            <label>End:</label>
            <input type="date" name="end_date" min="1970-01-01" max="2020-12-31" required>
        </div>

        <div class="section">
            <h2>Reference Metric</h2>
            <label>Choose Reference:</label>
            <select name="reference_metric" required>
    """
    for m in metrics:
        page_html += f"<option value='{m}'>{m}</option>\n"

    page_html += """
            </select>
        </div>

        <div class="section">
            <button type="submit" name="action" value="create">Create Graph and CSV from specified</button>
            <button type="submit" name="action" value="export">Export as .csv</button>
        </div>
    </form>
"""

    # Show chart if data returned
    if result_data and "similar_metrics" in result_data:
        chart_labels = [m["metric"] for m in result_data["similar_metrics"]]
        chart_values = [m["change"] for m in result_data["similar_metrics"]]

        page_html += f"""
    <div class="section">
        <h2>Most Similar Metrics to {result_data["reference_metric"]}</h2>
        <canvas id="barChart" width="800" height="400"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('barChart').getContext('2d');
        new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: 'Percentage Change Similarity',
                    data: {json.dumps(chart_values)},
                    backgroundColor: 'rgba(52, 152, 219, 0.6)',
                    borderColor: 'rgba(41, 128, 185, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Percentage Change (%)'
                        }}
                    }}
                }}
            }}
        }});
    </script>
"""
    elif csv_output:
        page_html += f"""
    <div class="section">
        <h2>CSV Export</h2>
        <textarea rows="10" cols="100" readonly>{csv_output}</textarea>
    </div>
"""

    page_html += """
    <p><a href="/">Back to Landing Page</a></p>
</body>
</html>
"""
    return page_html
