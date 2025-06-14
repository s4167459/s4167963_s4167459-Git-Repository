from similar_climate_utils import get_similarity_data
import json

def get_page_html(form_data):
    result_data = None
    error_message = None
    start_val = ""
    end_val = ""
    ref_metric_val = ""
    other_metrics_val = []

    if form_data:
        start_val = form_data.get("start_date", "")
        end_val = form_data.get("end_date", "")
        ref_metric_val = form_data.get("reference_metric", "")

        # Robustly handle multiple "other_metrics"
        other_metrics_val = form_data.get("other_metrics", [])
        if isinstance(other_metrics_val, str):
            other_metrics_val = [other_metrics_val]

        # Defensive: ensure no duplicates
        other_metrics_val = list(dict.fromkeys(other_metrics_val))

        # Prepare form copy for utils
        form_copy = form_data.copy()
        form_copy["other_metrics"] = other_metrics_val

        json_result = get_similarity_data(form_copy)
        # Debug print removed or keep if needed
        # print("DEBUG json_result:", json_result)
        parsed = json.loads(json_result)
        if "error" not in parsed:
            result_data = parsed
        else:
            error_message = parsed["error"]

    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    def checked(metric):
        return "checked" if metric in other_metrics_val else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Deep Dive into Metric Similarities</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 960px; }}
        h1 {{ color: #2c3e50; }}
        label {{ display: block; margin-top: 10px; }}
        .metric-checkboxes {{ margin-top: 10px; }}
        .metric-checkboxes label {{ display: inline-block; margin-right: 10px; }}
        input[type="checkbox"]:checked + span {{
            background-color: #27ae60;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        canvas {{ margin-top: 30px; }}
        button {{ margin-top: 20px; padding: 10px 15px; background: #27ae60; color: white; border: none; cursor: pointer; }}
        button:disabled {{ background: #ccc; cursor: not-allowed; }}
        button:hover:not(:disabled) {{ background: #1e8449; }}
        #formError {{ color: red; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>Deep Dive into Metric Similarities</h1>
    <form method="post" onsubmit="return validateForm();">
        <label>Start Date:</label>
        <input type="date" name="start_date" id="start" required value="{start_val}" min="1970-01-01" max="2020-12-31">

        <label>End Date:</label>
        <input type="date" name="end_date" id="end" required value="{end_val}" min="1970-01-01" max="2020-12-31">

        <label>Reference Metric:</label>
        <select name="reference_metric" id="reference_metric" required onchange="updateCheckboxes()">
    """

    for metric in valid_metrics:
        selected = "selected" if metric == ref_metric_val else ""
        html += f'<option value="{metric}" {selected}>{metric}</option>'

    html += '</select>\n<label>Other Metrics:</label>\n<div class="metric-checkboxes">\n'

    for metric in valid_metrics:
        html += f"""
            <label>
                <input type="checkbox" name="other_metrics" value="{metric}" {checked(metric)} id="chk_{metric}">
                <span>{metric}</span>
            </label>
        """

    html += """
        </div>
        <button type="submit" id="submitBtn" disabled>Compare Metrics</button>
        <p id="formError" style="display:none;"></p>
    </form>

    <canvas id="comparisonChart" width="900" height="400"></canvas>

    <script>
        function validateForm() {
            const start = document.getElementById("start").value;
            const end = document.getElementById("end").value;
            const errorBox = document.getElementById("formError");
            const checkedOthers = document.querySelectorAll('input[name="other_metrics"]:checked');
            if (start && end && start >= end) {
                errorBox.textContent = "End date must be later than start date.";
                errorBox.style.display = "block";
                return false;
            }
            if (checkedOthers.length === 0) {
                errorBox.textContent = "Please select at least one Other Metric.";
                errorBox.style.display = "block";
                return false;
            }
            errorBox.style.display = "none";
            return true;
        }

        function updateCheckboxes() {
            const refMetric = document.getElementById("reference_metric").value;
            const allCheckboxes = document.querySelectorAll('input[type="checkbox"][name="other_metrics"]');
            allCheckboxes.forEach(cb => {
                cb.disabled = cb.value === refMetric;
                const labelSpan = cb.nextElementSibling;
                if (cb.disabled) {
                    cb.checked = false;
                    labelSpan.style.opacity = 0.3;
                } else {
                    labelSpan.style.opacity = 1.0;
                }
            });
            updateSubmitButton();
        }

        function updateSubmitButton() {
            const checkedOthers = document.querySelectorAll('input[name="other_metrics"]:checked');
            const btn = document.getElementById("submitBtn");
            btn.disabled = checkedOthers.length === 0;
        }

        // Add event listeners to checkboxes to update submit button state on change
        document.addEventListener('DOMContentLoaded', () => {
            updateCheckboxes();
            const allCheckboxes = document.querySelectorAll('input[type="checkbox"][name="other_metrics"]');
            allCheckboxes.forEach(cb => {
                cb.addEventListener('change', updateSubmitButton);
            });
        });
    </script>
"""

    if error_message:
        html += f'<p style="color:red;">Error: {error_message}</p>'

    if result_data:
        ref_series = result_data["reference_series"]
        others = result_data["other_series"]

        # Build datasets list in Python, then JSON dump once
        datasets_list = [{
            "label": result_data['reference'],
            "data": [{"x": pt["date"], "y": pt["value"]} for pt in ref_series],
            "borderColor": "black",
            "fill": False,
            "borderWidth": 2,
            "tension": 0.1
        }]

        colors = ['red','blue','green','orange','purple','brown','teal','magenta','darkblue','darkgreen']
        for i, (metric, series) in enumerate(others.items()):
            datasets_list.append({
                "label": metric,
                "data": [{"x": pt["date"], "y": pt["value"]} for pt in series],
                "borderColor": colors[i % len(colors)],
                "fill": False,
                "borderWidth": 1,
                "tension": 0.1
            })

        html += f"""
    <script>
        const ctx = document.getElementById("comparisonChart").getContext("2d");
        const datasets = {json.dumps(datasets_list)};

        new Chart(ctx, {{
            type: 'line',
            data: {{
                datasets: datasets
            }},
            options: {{
                responsive: true,
                parsing: false,
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            parser: 'yyyy-MM-dd',
                            tooltipFormat: 'yyyy-MM-dd',
                            unit: 'month',
                            displayFormats: {{
                                month: 'MMM yyyy'
                            }}
                        }},
                        title: {{
                            display: true,
                            text: 'Date'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Value'
                        }}
                    }}
                }},
                plugins: {{
                    tooltip: {{
                        enabled: true
                    }},
                    legend: {{
                        display: true
                    }}
                }}
            }}
        }});
    </script>
"""

    html += '<p><a href="/">Back to Landing Page</a></p></body></html>'
    return html
