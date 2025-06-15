def get_page_html(form_data):
    """
    Landing page for the Climate Change WebApp
    Provides navigation to all main features and brief overview
    """
    
    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Climate Change WebApp - Australian Weather Data Explorer</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            padding: 40px 0;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        
        .feature-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: center;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            display: block;
        }
        
        .feature-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.5rem;
        }
        
        .feature-card p {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.6;
        }
        
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .data-info {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 30px;
            margin: 40px 0;
            color: white;
            text-align: center;
        }
        
        .data-info h2 {
            margin-bottom: 20px;
            font-size: 2rem;
        }
        
        .data-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .stat-item {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #fff;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .footer {
            text-align: center;
            color: white;
            padding: 30px 0;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .header p {
                font-size: 1rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .feature-card {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Climate Change WebApp</h1>
            <p>Explore Australian weather data from 1970-2020. Understand climate trends through interactive visualizations and comprehensive analysis tools.</p>
        </header>
        
        <div class="data-info">
            <h2>Australian Weather Data Explorer</h2>
            <p>Access decades of comprehensive climate data from weather stations across Australia. Our platform provides tools for researchers, policymakers, and curious citizens to understand climate patterns and trends.</p>
            
            <div class="data-stats">
                <div class="stat-item">
                    <span class="stat-number">50+</span>
                    <span class="stat-label">Years of Data</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">22</span>
                    <span class="stat-label">Climate Metrics</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">9</span>
                    <span class="stat-label">Regions Covered</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">1000s</span>
                    <span class="stat-label">Weather Stations</span>
                </div>
            </div>
        </div>
        
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <h3>Focused Analysis</h3>
                <p>Dive deep into specific climate metrics across different time periods and regions. Create custom visualizations and compare trends across Australian states.</p>
                <a href="/focused" class="btn">Explore Data</a>
            </div>
            
            <div class="feature-card">
                <span class="feature-icon">🔍</span>
                <h3>Deep Dive Comparison</h3>
                <p>Compare multiple climate metrics simultaneously to understand correlations and patterns. Perfect for researchers and data analysts.</p>
                <a href="/deep-dive" class="btn">Compare Metrics</a>
            </div>
            
            <div class="feature-card">
                <span class="feature-icon">🎯</span>
                <h3>Mission & Team</h3>
                <p>Learn about our mission to make climate data accessible and meet the team behind this project. Understand our target personas and goals.</p>
                <a href="/m-statement" class="btn">About Us</a>
            </div>
        </div>
        
        <div class="data-info">
            <h2>Available Climate Metrics</h2>
            <p>Our comprehensive dataset includes precipitation, temperature, humidity, evaporation, sunshine hours, and cloud cover measurements collected from weather stations across all Australian states and territories.</p>
        </div>
        
        <footer class="footer">
            <p>&copy; 2024 Climate Change WebApp | Australian Weather Data Explorer</p>
            <p>Data covers the period 1970-2020 from Bureau of Meteorology stations</p>
        </footer>
    </div>
</body>
</html>"""
    
    return page_html