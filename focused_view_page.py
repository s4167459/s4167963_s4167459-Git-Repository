from pyhtml import html, head, body, div, h1, h2, label, input_, select, option, button, canvas, script, style, p, title

def get_focused_view_page(form_data):
    print("About to return Focused View by Climate Metric page")

    # All valid measurable metrics
    valid_metrics = [
        "precipitation", "evaporation", "maxTemp", "minTemp", "sunshine",
        "humid00", "humid03", "humid06", "humid09", "humid12", "humid15", "humid18", "humid21",
        "okta00", "okta03", "okta06", "okta09", "okta12", "okta15", "okta18", "okta21"
    ]

    # Measurement units for each metric
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

    station_ranges = {
        "WA": (1007, 13017), "VIC": (76031, 90015), "TAS": (91107, 99005), "SA": (16001, 18115),
        "QLD": (28004, 44021), "NT": (14015, 15602), "NSW": (48027, 75041),
        "AET": (200283, 200288), "AAT": (300000, 300004)
    }

    page = html(
        head(
            title("Focused View by Climate Metric"),
            style("""
                body { font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }
                h1, h2 { color: #2c3e50; }
                label { display: inline-block; margin-top: 10px; font-weight: bold; }
                select, input { margin: 5px 10px; padding: 5px; }
                button { margin: 10px 10px; padding: 10px 20px; background: #2980b9; color: white; border: none; cursor: pointer; }
                button:hover { background: #1c5980; }
                canvas { max-width: 100%; margin-top: 20px; }
                .section { margin-bottom: 30px; }
            """)
        ),
        body(
            h1("Focused View by Climate Metric"),
            div({"class": "section"},
                h2("Time Range"),
                label("Begin: "), input_({"type": "date", "name": "start_date", "min": "1970-01-01", "max": "2020-12-31"}),
                label("End: "), input_({"type": "date", "name": "end_date", "min": "1970-01-01", "max": "2020-12-31"})
            ),
            div({"class": "section"},
                h2("Filters"),
                label("Climate Type: "),
                select({"name": "climate_type", "id": "climate_type"}, *[option(metric, value=metric) for metric in valid_metrics]),

                label("Station ID Start Range: "),
                select({"name": "start_station"}, *[
                    option(f"{state} ({r[0]})", value=r[0]) for state, r in station_ranges.items()
                ]),

                label("End Range: "),
                select({"name": "end_station"}, *[
                    option(f"{state} ({r[1]})", value=r[1]) for state, r in station_ranges.items()
                ])
            ),

            div({"class": "section"},
                button({"onclick": "createGraphAndTable()"}, "Create graph and csv from specified"),
                button({"onclick": "exportCSV()"}, "Export as .csv")
            ),

            div({"class": "section"},
                h2("Climate Trend Graph"),
                canvas({"id": "lineGraph", "width": "800", "height": "400"})
            ),

            div({"class": "section"},
                h2("Summary Table (State Totals)"),
                canvas({"id": "summaryGraph", "width": "800", "height": "300"})
            ),

            script({"src": "https://cdn.jsdelivr.net/npm/chart.js"}),

            # JS includes date validation and unit extraction
            script(f"""
                const metricUnits = {str(metric_units).replace("'", '"')};

                function createGraphAndTable() {{
                    const start = new Date(document.querySelector('input[name="start_date"]').value);
                    const end = new Date(document.querySelector('input[name="end_date"]').value);
                    const metric = document.getElementById('climate_type').value;
                    const unit = metricUnits[metric];

                    if (!start || !end || isNaN(start) || isNaN(end)) {{
                        alert("Please select both a valid start and end date.");
                        return;
                    }}

                    if (end <= start) {{
                        alert("End date must be later than start date.");
                        return;
                    }}

                    if (start < new Date("1970-01-01") || end > new Date("2020-12-31")) {{
                        alert("Dates must be between 01/01/1970 and 31/12/2020.");
                        return;
                    }}

                    alert("Validated! Would now fetch and draw graph for " + metric + " (" + unit + ").");

                    // TODO: Fetch backend data and draw graphs
                }}

                function exportCSV() {{
                    alert('Export logic will be implemented here.');
                    // TODO: Generate and download CSV
                }}
            """)
        )
    )

    return str(page)

