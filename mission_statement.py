def get_mission_statement_page(form_data):
    print("About to return Mission Statement page")
    
    # Hard-coded mission statement and purpose
    mission_statement = """
    <h2>Mission Statement</h2>
    <p>
        Our website seeks to ease the social challenge of understanding Anthropomorphic Climate Change by providing 
        unbiased, factual, and accessible climate data to inform the general public, corporations, 
        and policymakers. Users can explore climate trends from the beginning of 1970 to the end of 2020 with tools tailored 
        to diverse needs and interests.
    </p>
    <p>
        The site enables understanding of climate change impacts in the Australian context, empowering 
        informed decision-making and awareness.
    </p>
    """
    
    # Query personas and team members from database
    persona_query = "SELECT persona_name, description FROM Personas ORDER BY persona_name;"
    team_query = "SELECT name, student_number FROM TeamMembers ORDER BY name;"
    
    personas = pyhtml.get_results_from_query("database/climate_data.db", persona_query)
    team_members = pyhtml.get_results_from_query("database/climate_data.db", team_query)
    
    # Build the HTML page
    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Mission Statement - Climate Change WebApp</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 900px; margin: auto; padding: 20px; }
        h1, h2 { color: #2c3e50; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin-bottom: 8px; }
        .section { margin-bottom: 30px; }
        a { text-decoration: none; color: #2980b9; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Mission Statement</h1>
    <div class="section">
    """ + mission_statement + """
    </div>
    
    <div class="section">
        <h2>Target Personas</h2>
        <ul>
    """
    # Add personas
    for persona_name, description in personas:
        page_html += f"<li><strong>{persona_name}</strong>: {description}</li>\n"
    
    page_html += """
        </ul>
    </div>
    
    <div class="section">
        <h2>Team Members</h2>
        <ul>
    """
    # Add team members
    for name, student_number in team_members:
        page_html += f"<li>{name} - {student_number}</li>\n"
    
    page_html += """
        </ul>
    </div>
    
    <p><a href="/">Back to Landing Page</a></p>
</body>
</html>
"""
    return page_html
