#!/usr/bin/env python3
"""
Simple web app designed specifically for Render.com deployment.
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    """Home page with embedded graph visualization."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DebtSweeper Graph</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #000;
                color: white;
                text-align: center;
                padding: 20px;
                margin: 0;
            }
            h1 {
                color: #3DDC84;
                font-size: 32px;
                margin-bottom: 10px;
            }
            p {
                margin-bottom: 20px;
            }
            .graph {
                width: 90%;
                max-width: 800px;
                height: 400px;
                margin: 0 auto 20px;
                background: #111;
                border: 2px solid #3DDC84;
                position: relative;
            }
            .node {
                position: absolute;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }
            .line {
                position: absolute;
                height: 2px;
                background: #aaa;
                transform-origin: 0 0;
            }
            .legend {
                background: #222;
                padding: 15px;
                border-radius: 5px;
                display: inline-block;
                margin: 0 auto;
                text-align: left;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .legend-color {
                width: 15px;
                height: 15px;
                border-radius: 50%;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <h1>DebtSweeper Knowledge Graph</h1>
        <p>Visualization of code dependencies and technical debt</p>
        
        <div class="graph">
            <!-- Nodes -->
            <div class="node" style="width: 60px; height: 60px; background: #3DDC84; left: 70px; top: 80px;">Module A</div>
            <div class="node" style="width: 50px; height: 50px; background: #FFC107; left: 250px; top: 70px;">Class B</div>
            <div class="node" style="width: 40px; height: 40px; background: #e84118; left: 400px; top: 120px;">Func C</div>
            <div class="node" style="width: 45px; height: 45px; background: #3DDC84; left: 250px; top: 220px;">Method D</div>
            <div class="node" style="width: 55px; height: 55px; background: #FFC107; left: 80px; top: 240px;">Module E</div>
            
            <!-- Edges -->
            <div class="line" style="width: 180px; left: 100px; top: 80px; transform: rotate(0deg);"></div>
            <div class="line" style="width: 160px; left: 95px; top: 110px; transform: rotate(35deg);"></div>
            <div class="line" style="width: 170px; left: 275px; top: 95px; transform: rotate(45deg);"></div>
            <div class="line" style="width: 150px; left: 250px; top: 220px; transform: rotate(200deg);"></div>
            <div class="line" style="width: 190px; left: 120px; top: 240px; transform: rotate(315deg);"></div>
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
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)