from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    """Simple index page with link to graph visualization."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>DebtSweeper Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #000;
                color: white;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #3DDC84;
            }
            a {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #000;
                color: #3DDC84;
                text-decoration: none;
                border: 2px solid #3DDC84;
                border-radius: 4px;
            }
            a:hover {
                background: #3DDC84;
                color: #000;
            }
        </style>
    </head>
    <body>
        <h1>DebtSweeper Dashboard</h1>
        <p>View the interactive visualization of your code dependencies and technical debt.</p>
        <a href="/graph">View Debt Knowledge Graph</a>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/graph')
def graph():
    """Render graph visualization."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>DebtSweeper Graph</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #000;
                color: white;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                color: #3DDC84;
            }
            .graph-container {
                width: 800px;
                height: 500px;
                margin: 20px auto;
                border: 2px solid #3DDC84;
                background: #111;
                position: relative;
            }
            .node {
                position: absolute;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }
            .line {
                position: absolute;
                height: 2px;
                background: #aaa;
                transform-origin: 0 0;
            }
            .legend {
                margin-top: 20px;
                display: inline-block;
                background: #222;
                padding: 15px;
                border-radius: 5px;
                text-align: left;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .legend-color {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                margin-right: 10px;
            }
            a {
                color: #3DDC84;
                text-decoration: none;
                margin-top: 20px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>DebtSweeper Knowledge Graph</h1>
        <p>Static visualization of code dependencies and technical debt.</p>
        
        <div class="graph-container">
            <!-- Hard-coded nodes -->
            <div class="node" style="width: 80px; height: 80px; background: #3DDC84; left: 100px; top: 100px;">Module A</div>
            <div class="node" style="width: 70px; height: 70px; background: #FFC107; left: 300px; top: 80px;">Class B</div>
            <div class="node" style="width: 60px; height: 60px; background: #e84118; left: 450px; top: 150px;">Func C</div>
            <div class="node" style="width: 65px; height: 65px; background: #3DDC84; left: 280px; top: 250px;">Method D</div>
            <div class="node" style="width: 75px; height: 75px; background: #FFC107; left: 120px; top: 280px;">Module E</div>
            
            <!-- Hard-coded edges (positioned and rotated with inline styles) -->
            <div class="line" style="width: 205px; left: 140px; top: 100px; transform: rotate(0deg);"></div>
            <div class="line" style="width: 180px; left: 135px; top: 135px; transform: rotate(35deg);"></div>
            <div class="line" style="width: 190px; left: 335px; top: 115px; transform: rotate(45deg);"></div>
            <div class="line" style="width: 170px; left: 310px; top: 250px; transform: rotate(200deg);"></div>
            <div class="line" style="width: 220px; left: 175px; top: 280px; transform: rotate(315deg);"></div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #3DDC84;"></div>
                <span>High test coverage (>80%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #FFC107;"></div>
                <span>Medium test coverage (50-80%)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e84118;"></div>
                <span>Low test coverage (<50%)</span>
            </div>
            <div class="legend-item">
                <span>Node size represents code complexity</span>
            </div>
        </div>
        
        <p><a href="/">Back to Dashboard</a></p>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)