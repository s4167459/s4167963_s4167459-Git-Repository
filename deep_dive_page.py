import similar_climate_utils
import json
from datetime import datetime

def get_page_html(form_data, export_flag=None):
    from similar_climate_utils import get_similar_climate_metrics

    result_data = None
    error_message = None
    start_val = ""
    end_val = ""
    ref_metric_val = ""
    other_metrics_val = []

    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    def checked(metric):
        return "checked" if metric in other_metrics_val else ""

    if form_data:
        try:
            start_val = form_data.get("start_date", "")
            end_val = form_data.get("end_date", "")
            if not start_val or not end_val:
                raise ValueError("Start and end dates are required.")

            start_dt = datetime.strptime(start_val, "%Y-%m-%d")
            end_dt = datetime.strptime(end_val, "%Y-%m-%d")

            if start_dt >= end_dt:
                error_message = "Start date must be earlier than end date."
            else:
                ref_metric_val = form_data.get("reference_metric", "")
                if ref_metric_val not in valid_metrics:
                    error_message = "Reference metric is invalid."
                else:
                    # **IMPORTANT FIX: Handle multiple checkbox values properly**
                    # Your pyhtml form_data might have getlist, if not fallback:
                    if hasattr(form_data, "getlist"):
                        other_metrics_val = form_data.getlist("other_metrics[]")
                    else:
                        # fallback for dict-like form_data
                        other_metrics_val = form_data.get("other_metrics[]", [])
                        if isinstance(other_metrics_val, str):
                            other_metrics_val = [other_metrics_val]

                    # Remove duplicates and ensure list
                    other_metrics_val = list(dict.fromkeys(other_metrics_val))
                    # Remove reference metric if selected in other_metrics
                    if ref_metric_val in other_metrics_val:
                        other_metrics_val.remove(ref_metric_val)
                    if len(other_metrics_val) == 0:
                        error_message = "Please select at least one Other Metric."
                    if not error_message:
                        form_copy = form_data.copy()
                        form_copy["other_metrics"] = other_metrics_val
                        json_result = get_similar_climate_metrics(form_copy)
                        parsed = json.loads(json_result)
                        if "error" not in parsed:
                            result_data = parsed
                        else:
                            error_message = parsed["error"]
        except Exception as e:
            error_message = str(e)

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
        <select name="reference_metric" id="reference_metric" required onchange="updateCheckboxes()">"""
    for metric in valid_metrics:
        selected = "selected" if metric == ref_metric_val else ""
        html += f'<option value="{metric}" {selected}>{metric}</option>'

    html += '</select>\n<label>Other Metrics:</label>\n<div class="metric-checkboxes">\n'
    for metric in valid_metrics:
        disabled = 'disabled' if metric == ref_metric_val else ''
        checked_attr = checked(metric)
        # **IMPORTANT FIX: change name to other_metrics[] to send multiple values**
        html += f"""
            <label>
                <input type="checkbox" name="other_metrics[]" value="{metric}" {checked_attr} id="chk_{metric}" {disabled}>
                <span>{metric}</span>
            </label>
        """

    html += """
        </div>
        <button type="submit" id="submitBtn" disabled>Compare Metrics</button>
        <p id="formError" style="display:none;"></p>
    </form>
    <p>This graph compares the percentage change in the selected climate metrics over time. The reference metric is shown in bold; other metrics are measured against it.</p>
    <canvas id="comparisonChart" width="900" height="400"></canvas>
    <script>
        function validateForm() {
            const start = document.getElementById("start").value;
            const end = document.getElementById("end").value;
            const errorBox = document.getElementById("formError");
            const checkedOthers = document.querySelectorAll('input[name="other_metrics[]"]:checked');
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
            const allCheckboxes = document.querySelectorAll('input[type="checkbox"][name="other_metrics[]"]');
            allCheckboxes.forEach(cb => {
                cb.disabled = (cb.value === refMetric);
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
            const checkedOthers = document.querySelectorAll('input[name="other_metrics[]"]:checked');
            const btn = document.getElementById("submitBtn");
            btn.disabled = checkedOthers.length === 0;
        }

        document.addEventListener('DOMContentLoaded', () => {
            updateCheckboxes();
            const allCheckboxes = document.querySelectorAll('input[name="other_metrics[]"]');
            allCheckboxes.forEach(cb => {
                cb.addEventListener('change', updateSubmitButton);
            });
            updateSubmitButton();
        });
    </script>
"""

    if error_message:
        html += f'<p style="color:red;">Error: {error_message}</p>'

    if result_data:
        ref_metric = result_data.get("reference", "")
        ref_series = result_data.get("reference_series", [])
        other_series = result_data.get("other_series", {})

        labels = [point["date"] for point in ref_series]

        datasets = []

        datasets.append({
            "label": ref_metric,
            "data": [point["value"] for point in ref_series],
            "borderColor": "blue",
            "backgroundColor": "blue",
            "fill": False,
            "borderWidth": 3,
            "tension": 0.1
        })

        colors = ['red', 'green', 'orange', 'purple', 'brown', 'magenta']

        for i, (metric, series) in enumerate(other_series.items()):
            datasets.append({
                "label": metric,
                "data": [point["value"] for point in series],
                "borderColor": colors[i % len(colors)],
                "backgroundColor": colors[i % len(colors)],
                "fill": False,
                "borderWidth": 1,
                "tension": 0.1
            })

        labels_json = json.dumps(labels)
        datasets_json = json.dumps(datasets)

        html += f"""
        <script>
            const ctx = document.getElementById("comparisonChart").getContext("2d");
            const data = {{
                labels: {labels_json},
                datasets: {datasets_json}
            }};
            new Chart(ctx, {{
                type: 'line',
                data: data,
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Percentage Change (%)'
                            }}
                        }},
                        x: {{
                            title: {{
                                display: true,
                                text: 'Date'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true
                        }},
                        tooltip: {{
                            enabled: true
                        }}
                    }}
                }}
            }});
        </script>
        """

    html += '<p><a href="/">Back to Landing Page</a></p></body></html>'
    return html
