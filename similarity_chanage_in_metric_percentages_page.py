from level3_similarity_utils import get_station_similarity_data, get_available_stations, get_station_metrics_data
import json

def get_page_html(form_data):
    print("Generating Weather Station Similarity Analysis Page...")

    analysis_results = None
    error_message = None
    
    # Form values for preservation
    reference_station = form_data.get("reference_station", "") if form_data else ""
    primary_metric = form_data.get("primary_metric", "") if form_data else ""
    secondary_metric = form_data.get("secondary_metric", "") if form_data else ""
    period1_start = form_data.get("period1_start", "") if form_data else ""
    period1_end = form_data.get("period1_end", "") if form_data else ""
    period2_start = form_data.get("period2_start", "") if form_data else ""
    period2_end = form_data.get("period2_end", "") if form_data else ""
    num_stations = form_data.get("num_stations", "5") if form_data else "5"

    if form_data and form_data.get("action") == "find_similar":
        try:
            result_json = get_station_similarity_data(form_data)
            result_dict = json.loads(result_json)
            if "error" in result_dict:
                error_message = result_dict["error"]
            else:
                analysis_results = result_dict
        except Exception as e:
            error_message = f"Analysis error: {str(e)}"

    # Get available stations and metrics
    available_stations = get_available_stations()
    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21"
    ]

    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Weather Station Similarity Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 1400px; 
            margin: auto; 
            padding: 20px; 
            background: #f8f9fa;
        }
        h1, h2 { color: #2c3e50; }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .form-section {
            margin-bottom: 25px;
            padding: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            background: #f8f9fa;
        }
        .form-section h3 {
            margin-top: 0;
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 8px;
        }
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .form-group {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: bold;
            color: #495057;
            margin-bottom: 5px;
        }
        select, input {
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 14px;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 5px rgba(0,123,255,0.25);
        }
        button {
            background: linear-gradient(45deg, #007bff, #0056b3);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(0,123,255,0.3); }
        .results-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .analysis-summary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
        }
        .reference-info {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #2196f3;
            margin-bottom: 25px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
        .metric-card {
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .metric-card h4 { margin: 0 0 10px 0; color: #2c3e50; }
        .metric-value { font-size: 1.4em; font-weight: bold; color: #007bff; }
        .change-indicator {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .increase { background: #ffebee; color: #c62828; }
        .decrease { background: #e8f5e8; color: #2e7d32; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }
        th {
            background: #495057;
            color: white;
            font-weight: bold;
        }
        tr:hover { background: #f8f9fa; }
        .similarity-score {
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 20px;
            color: white;
            text-align: center;
        }
        .very-similar { background: #28a745; }
        .similar { background: #17a2b8; }
        .somewhat-similar { background: #ffc107; color: #212529; }
        .not-similar { background: #dc3545; }
        .error {
            color: #721c24;
            background: #f8d7da;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #f5c6cb;
            margin: 15px 0;
        }
        canvas { max-width: 100%; margin: 20px 0; }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>🔍 Weather Station Similarity Analysis</h1>
    <p>Find weather stations with similar climate change patterns based on rate of change analysis.</p>

    <div class="form-container">
        <form method="post" onsubmit="return validateForm()">
            <div class="form-section">
                <h3>🏢 Reference Station & Metrics</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Reference Weather Station:</label>
                        <select name="reference_station" required>
                            <option value="">Choose reference station...</option>"""

    # Group stations by state
    stations_by_state = {}
    for station_id, name, state in available_stations:
        if state not in stations_by_state:
            stations_by_state[state] = []
        stations_by_state[state].append((station_id, name))

    # Add station options grouped by state
    for state in sorted(stations_by_state.keys()):
        page_html += f'<optgroup label="{state}">'
        for station_id, name in sorted(stations_by_state[state], key=lambda x: x[1]):
            selected = "selected" if str(station_id) == reference_station else ""
            page_html += f'<option value="{station_id}" {selected}>{name} ({station_id})</option>'
        page_html += '</optgroup>'

    page_html += f"""
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Primary Climate Metric:</label>
                        <select name="primary_metric" required>
                            <option value="">Choose primary metric...</option>"""

    for metric in valid_metrics:
        selected = "selected" if metric == primary_metric else ""
        page_html += f'<option value="{metric}" {selected}>{metric}</option>'

    page_html += f"""
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Secondary Climate Metric:</label>
                        <select name="secondary_metric" required>
                            <option value="">Choose secondary metric...</option>"""

    for metric in valid_metrics:
        selected = "selected" if metric == secondary_metric else ""
        page_html += f'<option value="{metric}" {selected}>{metric}</option>'

    page_html += f"""
                        </select>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>📅 Time Periods for Comparison</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Period 1 Start:</label>
                        <input type="date" name="period1_start" value="{period1_start}" min="1970-01-01" max="2020-12-31" required>
                    </div>
                    <div class="form-group">
                        <label>Period 1 End:</label>
                        <input type="date" name="period1_end" value="{period1_end}" min="1970-01-01" max="2020-12-31" required>
                    </div>
                    <div class="form-group">
                        <label>Period 2 Start:</label>
                        <input type="date" name="period2_start" value="{period2_start}" min="1970-01-01" max="2020-12-31" required>
                    </div>
                    <div class="form-group">
                        <label>Period 2 End:</label>
                        <input type="date" name="period2_end" value="{period2_end}" min="1970-01-01" max="2020-12-31" required>
                    </div>
                </div>
            </div>

            <div class="form-section">
                <h3>⚙️ Analysis Settings</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>Number of Similar Stations to Find:</label>
                        <select name="num_stations">
                            <option value="3" {"selected" if num_stations == "3" else ""}>3 stations</option>
                            <option value="5" {"selected" if num_stations == "5" else ""}>5 stations</option>
                            <option value="10" {"selected" if num_stations == "10" else ""}>10 stations</option>
                            <option value="15" {"selected" if num_stations == "15" else ""}>15 stations</option>
                        </select>
                    </div>
                </div>
            </div>

            <button type="submit" name="action" value="find_similar">🔍 Find Similar Stations</button>
        </form>
    </div>"""

    if error_message:
        page_html += f'<div class="error">❌ Error: {error_message}</div>'

    if analysis_results:
        ref_station = analysis_results["reference_station"]
        similar_stations = analysis_results["similar_stations"]
        params = analysis_results["parameters"]

        page_html += f"""
    <div class="results-container">
        <div class="analysis-summary">
            <h2>📊 Analysis Results</h2>
            <p><strong>Reference Station:</strong> {ref_station["name"]} (ID: {ref_station["id"]})</p>
            <p><strong>Metrics:</strong> {params["primary_metric"]} vs {params["secondary_metric"]}</p>
            <p><strong>Period 1:</strong> {params["period1"]} | <strong>Period 2:</strong> {params["period2"]}</p>
        </div>

        <div class="reference-info">
            <h3>📍 Reference Station Rate of Change</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>{params["primary_metric"]}</h4>
                    <div class="metric-value">{ref_station["primary_change"]:.2f}%</div>
                    <div class="change-indicator {'increase' if ref_station['primary_change'] > 0 else 'decrease'}">
                        {'↑' if ref_station['primary_change'] > 0 else '↓'} 
                        {abs(ref_station["primary_change"]):.2f}%
                    </div>
                    <div style="font-size: 0.85em; margin-top: 8px; color: #666;">
                        Period 1: {ref_station["primary_period1_avg"]:.2f}<br>
                        Period 2: {ref_station["primary_period2_avg"]:.2f}
                    </div>
                </div>
                <div class="metric-card">
                    <h4>{params["secondary_metric"]}</h4>
                    <div class="metric-value">{ref_station["secondary_change"]:.2f}%</div>
                    <div class="change-indicator {'increase' if ref_station['secondary_change'] > 0 else 'decrease'}">
                        {'↑' if ref_station['secondary_change'] > 0 else '↓'} 
                        {abs(ref_station["secondary_change"]):.2f}%
                    </div>
                    <div style="font-size: 0.85em; margin-top: 8px; color: #666;">
                        Period 1: {ref_station["secondary_period1_avg"]:.2f}<br>
                        Period 2: {ref_station["secondary_period2_avg"]:.2f}
                    </div>
                </div>
            </div>
        </div>

        <h3>🏆 Most Similar Weather Stations</h3>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Station Name</th>
                        <th>State</th>
                        <th>Location</th>
                        <th>Similarity Score</th>
                        <th>{params["primary_metric"]} Change</th>
                        <th>{params["secondary_metric"]} Change</th>
                        <th>Pattern Match</th>
                    </tr>
                </thead>
                <tbody>"""

        def get_similarity_class(score):
            if score < 5:
                return "very-similar"
            elif score < 15:
                return "similar"
            elif score < 30:
                return "somewhat-similar"
            else:
                return "not-similar"

        def get_pattern_description(primary_change, secondary_change, ref_primary, ref_secondary):
            primary_direction = "↑" if primary_change > 0 else "↓"
            secondary_direction = "↑" if secondary_change > 0 else "↓"
            ref_primary_direction = "↑" if ref_primary > 0 else "↓"
            ref_secondary_direction = "↑" if ref_secondary > 0 else "↓"
            
            if (primary_direction == ref_primary_direction and 
                secondary_direction == ref_secondary_direction):
                return f"Same trend {primary_direction}{secondary_direction}"
            else:
                return f"Different trend {primary_direction}{secondary_direction}"

        for idx, station in enumerate(similar_stations, 1):
            similarity_class = get_similarity_class(station["similarity_score"])
            pattern = get_pattern_description(
                station["primary_change"], station["secondary_change"],
                ref_station["primary_change"], ref_station["secondary_change"]
            )
            
            page_html += f"""
                    <tr>
                        <td><strong>#{idx}</strong></td>
                        <td>{station["name"]}</td>
                        <td>{station["state"]}</td>
                        <td>{station["latitude"]:.3f}, {station["longitude"]:.3f}</td>
                        <td><span class="similarity-score {similarity_class}">{station["similarity_score"]:.2f}</span></td>
                        <td>
                            <span class="change-indicator {'increase' if station['primary_change'] > 0 else 'decrease'}">
                                {station["primary_change"]:.2f}%
                            </span>
                        </td>
                        <td>
                            <span class="change-indicator {'increase' if station['secondary_change'] > 0 else 'decrease'}">
                                {station["secondary_change"]:.2f}%
                            </span>
                        </td>
                        <td>{pattern}</td>
                    </tr>"""

        page_html += """
                </tbody>
            </table>
        </div>

        <div class="chart-container">
            <h3>📈 Rate of Change Visualization</h3>
            <canvas id="changeChart" width="800" height="400"></canvas>
        </div>

        <div class="chart-container">
            <h3>🗺️ Similarity Score Distribution</h3>
            <canvas id="similarityChart" width="800" height="300"></canvas>
        </div>
    </div>

    <script>
        // Rate of Change Scatter Plot
        const changeCtx = document.getElementById('changeChart').getContext('2d');
        
        const referenceData = [{
            x: """ + str(ref_station["primary_change"]) + """,
            y: """ + str(ref_station["secondary_change"]) + """,
            label: '""" + ref_station["name"] + """ (Reference)'
        }];
        
        const similarStationsData = [""" + ",".join([
            f'{{x: {station["primary_change"]}, y: {station["secondary_change"]}, label: "{station["name"]}", similarity: {station["similarity_score"]}}}'
            for station in similar_stations
        ]) + """];

        new Chart(changeCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Reference Station',
                    data: referenceData,
                    backgroundColor: '#ff6b6b',
                    borderColor: '#ff5252',
                    pointRadius: 10,
                    pointHoverRadius: 12
                }, {
                    label: 'Similar Stations',
                    data: similarStationsData,
                    backgroundColor: '#4ecdc4',
                    borderColor: '#26a69a',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Rate of Change Comparison: """ + params["primary_metric"] + """ vs """ + params["secondary_metric"] + """'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.parsed;
                                const rawData = context.raw;
                                if (rawData.similarity !== undefined) {
                                    return `${rawData.label}: (${point.x.toFixed(2)}%, ${point.y.toFixed(2)}%) - Similarity: ${rawData.similarity}`;
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
                            text: '""" + params["primary_metric"] + """ Change (%)'
                        },
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '""" + params["secondary_metric"] + """ Change (%)'
                        },
                        grid: { color: 'rgba(0,0,0,0.1)' }
                    }
                }
            }
        });

        // Similarity Score Bar Chart
        const similarityCtx = document.getElementById('similarityChart').getContext('2d');
        
        const stationNames = [""" + ",".join([f'"{station["name"]}"' for station in similar_stations]) + """];
        const similarityScores = [""" + ",".join([str(station["similarity_score"]) for station in similar_stations]) + """];
        
        // Color bars based on similarity score
        const barColors = similarityScores.map(score => {
            if (score < 5) return '#28a745';
            if (score < 15) return '#17a2b8';
            if (score < 30) return '#ffc107';
            return '#dc3545';
        });

        new Chart(similarityCtx, {
            type: 'bar',
            data: {
                labels: stationNames,
                datasets: [{
                    label: 'Similarity Score (Lower = More Similar)',
                    data: similarityScores,
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
                        text: 'Similarity Scores to Reference Station'
                    },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Similarity Score'
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
    </script>"""

    page_html += """
    <script>
        function validateForm() {
            const period1Start = document.querySelector('input[name="period1_start"]').value;
            const period1End = document.querySelector('input[name="period1_end"]').value;
            const period2Start = document.querySelector('input[name="period2_start"]').value;
            const period2End = document.querySelector('input[name="period2_end"]').value;
            const primaryMetric = document.querySelector('select[name="primary_metric"]').value;
            const secondaryMetric = document.querySelector('select[name="secondary_metric"]').value;
            
            if (period1Start && period1End && period1Start >= period1End) {
                alert('Period 1 end date must be later than start date.');
                return false;
            }
            
            if (period2Start && period2End && period2Start >= period2End) {
                alert('Period 2 end date must be later than start date.');
                return false;
            }
            
            if (primaryMetric && secondaryMetric && primaryMetric === secondaryMetric) {
                alert('Primary and secondary metrics must be different.');
                return false;
            }
            
            return true;
        }
        
        // Add dynamic validation for metric selection
        document.addEventListener('DOMContentLoaded', function() {
            const primarySelect = document.querySelector('select[name="primary_metric"]');
            const secondarySelect = document.querySelector('select[name="secondary_metric"]');
            
            function updateMetricOptions() {
                const primaryValue = primarySelect.value;
                const secondaryValue = secondarySelect.value;
                
                // Reset all options
                Array.from(primarySelect.options).forEach(option => {
                    option.disabled = false;
                    option.style.color = '';
                });
                Array.from(secondarySelect.options).forEach(option => {
                    option.disabled = false;
                    option.style.color = '';
                });
                
                // Disable selected option in the other select
                if (primaryValue) {
                    Array.from(secondarySelect.options).forEach(option => {
                        if (option.value === primaryValue) {
                            option.disabled = true;
                            option.style.color = '#ccc';
                        }
                    });
                }
                
                if (secondaryValue) {
                    Array.from(primarySelect.options).forEach(option => {
                        if (option.value === secondaryValue) {
                            option.disabled = true;
                            option.style.color = '#ccc';
                        }
                    });
                }
            }
            
            primarySelect.addEventListener('change', updateMetricOptions);
            secondarySelect.addEventListener('change', updateMetricOptions);
            updateMetricOptions(); // Initial call
        });
    </script>

    <p><a href="/">← Back to Landing Page</a> | <a href="/focused">🔍 Focused Analysis</a> | <a href="/deep-dive">🌊 Deep Dive</a></p>
</body>
</html>"""
    
    return page_html