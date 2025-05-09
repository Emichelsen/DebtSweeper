#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone Flask dashboard for DebtSweeper with embedded graph.
"""

from flask import Flask, request, jsonify, send_file, redirect, url_for

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page with graph visualization directly embedded."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
                font-size: 32px;
                margin-bottom: 10px;
            }
            .graph-container {
                width: 90%;
                max-width: 800px;
                height: 400px;
                margin: 20px auto;
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
                margin-top: 20px;
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
        
        <div class="graph-container">
            <!-- Nodes -->
            <div class="node" style="width: 80px; height: 80px; background: #3DDC84; left: 100px; top: 100px;">Module A</div>
            <div class="node" style="width: 70px; height: 70px; background: #FFC107; left: 300px; top: 80px;">Class B</div>
            <div class="node" style="width: 60px; height: 60px; background: #e84118; left: 450px; top: 150px;">Func C</div>
            <div class="node" style="width: 65px; height: 65px; background: #3DDC84; left: 280px; top: 250px;">Method D</div>
            <div class="node" style="width: 75px; height: 75px; background: #FFC107; left: 120px; top: 280px;">Module E</div>
            
            <!-- Edges -->
            <div class="line" style="width: 205px; left: 140px; top: 100px; transform: rotate(0deg);"></div>
            <div class="line" style="width: 180px; left: 135px; top: 135px; transform: rotate(35deg);"></div>
            <div class="line" style="width: 190px; left: 335px; top: 115px; transform: rotate(45deg);"></div>
            <div class="line" style="width: 170px; left: 310px; top: 250px; transform: rotate(200deg);"></div>
            <div class="line" style="width: 220px; left: 175px; top: 280px; transform: rotate(315deg);"></div>
        </div>
        
        <div class="legend">
            <h3 style="margin-top: 0; color: #3DDC84;">Visualization Legend</h3>
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
        
        <div style="margin-top: 30px; max-width: 800px; margin-left: auto; margin-right: auto; text-align: left;">
            <h2 style="color: #3DDC84;">About DebtSweeper</h2>
            <p>
                DebtSweeper is a tool that helps development teams identify and fix technical debt in their Python codebases.
                It analyzes code for common debt patterns, scores each file based on its debt burden, and generates targeted
                refactoring suggestions.
            </p>
            
            <h3 style="color: #3DDC84;">How It Works</h3>
            <ul>
                <li>Scans your code repository for technical debt patterns</li>
                <li>Builds a knowledge graph of code dependencies</li>
                <li>Visualizes debt metrics using node size, color, and connections</li>
                <li>Helps identify problematic areas in your codebase</li>
                <li>Suggests refactoring strategies to reduce technical debt</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route('/scan')
def scan():
    """Placeholder scan page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DebtSweeper - Scan</title>
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
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            a {
                color: #3DDC84;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Scan Repository</h1>
        
        <div class="container">
            <div class="card">
                <h2>Coming Soon</h2>
                <p>The scan functionality is currently under development.</p>
                <p><a href="/">← Back to Dashboard</a></p>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)