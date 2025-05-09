#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified standalone Flask dashboard for DebtSweeper with minimal graph visualization.
Uses a direct, simpler approach to ensure the graph is visible.
"""

import os
import json
from flask import Flask, render_template_string, Response

# Create Flask app
app = Flask(__name__)

# HTML template with inline CSS and JavaScript - everything in one file
INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DebtSweeper Graph</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Cytoscape.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
    <style>
        body {
            background-color: #121212;
            color: white;
            font-family: Arial, sans-serif;
        }
        
        .container {
            margin-top: 20px;
        }
        
        h1 {
            color: #3DDC84;
            text-align: center;
            margin-bottom: 30px;
        }
        
        #graph-container {
            width: 100%;
            height: 600px;
            border: 2px solid #3DDC84;
            background-color: #1e1e1e;
            margin-bottom: 20px;
            position: relative;
        }
        
        .info-panel {
            background-color: #2a2a2a;
            border: 1px solid #3DDC84;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        
        .debug-log {
            background-color: #000;
            color: #00ff00;
            font-family: monospace;
            padding: 10px;
            height: 150px;
            overflow-y: auto;
            border: 1px solid #444;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DebtSweeper - Knowledge Graph</h1>
        
        <div id="graph-container"></div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="info-panel">
                    <h4>Graph Controls</h4>
                    <ul>
                        <li>Click on a node to see its details</li>
                        <li>Drag nodes to reposition them</li>
                        <li>Scroll to zoom in/out</li>
                    </ul>
                    <button id="reset-btn" class="btn btn-primary mt-2">Reset View</button>
                </div>
            </div>
            <div class="col-md-6">
                <div class="info-panel">
                    <h4>Graph Legend</h4>
                    <div class="d-flex align-items-center mb-2">
                        <div style="width: 15px; height: 15px; background-color: #3DDC84; border-radius: 50%; margin-right: 10px;"></div>
                        <span>High test coverage (>80%)</span>
                    </div>
                    <div class="d-flex align-items-center mb-2">
                        <div style="width: 15px; height: 15px; background-color: #FFC107; border-radius: 50%; margin-right: 10px;"></div>
                        <span>Medium test coverage (50-80%)</span>
                    </div>
                    <div class="d-flex align-items-center">
                        <div style="width: 15px; height: 15px; background-color: #e84118; border-radius: 50%; margin-right: 10px;"></div>
                        <span>Low test coverage (<50%)</span>
                    </div>
                    <p class="mt-2"><small>Node size indicates complexity</small></p>
                </div>
            </div>
        </div>
        
        <div class="debug-log" id="debug-log">
            <div>DEBUG LOG:</div>
        </div>
    </div>

    <script>
    // Debug logger function
    function log(message) {
        const logElement = document.getElementById('debug-log');
        const entry = document.createElement('div');
        entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
        console.log(message);
    }
    
    // Wait for DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        log('DOM loaded');
        
        // Ensure container exists and has dimensions
        const container = document.getElementById('graph-container');
        if (!container) {
            log('ERROR: Graph container not found');
            return;
        }
        
        log(`Container dimensions: ${container.offsetWidth}x${container.offsetHeight}`);
        
        // Graph data - a simple demo graph
        const graphData = {{graph_data|safe}};
        log(`Loaded graph data with ${graphData.nodes.length} nodes and ${graphData.edges.length} edges`);
        
        // Create tooltip div for node info
        const tooltip = document.createElement('div');
        tooltip.style.cssText = `
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #3DDC84;
            pointer-events: none;
            display: none;
            z-index: 999;
            max-width: 250px;
        `;
        document.body.appendChild(tooltip);
        
        // Initialize Cytoscape
        try {
            log('Initializing Cytoscape...');
            
            const cy = cytoscape({
                container: container,
                elements: [...graphData.nodes, ...graphData.edges],
                style: [
                    {
                        selector: 'node',
                        style: {
                            'label': 'data(label)',
                            'background-color': function(ele) {
                                // Color based on test coverage
                                const coverage = ele.data('coverage');
                                if (coverage >= 80) return '#3DDC84';
                                if (coverage >= 50) return '#FFC107';
                                return '#e84118';
                            },
                            'width': function(ele) {
                                // Size based on complexity
                                const complexity = ele.data('complexity');
                                return 20 + Math.min(complexity * 3, 60);
                            },
                            'height': function(ele) {
                                const complexity = ele.data('complexity');
                                return 20 + Math.min(complexity * 3, 60);
                            },
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': '#000',
                            'font-size': '14px'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'curve-style': 'bezier',
                            'width': 2,
                            'line-color': '#aaa',
                            'target-arrow-color': '#aaa',
                            'target-arrow-shape': 'triangle'
                        }
                    },
                    {
                        selector: 'edge[relation="calls"]',
                        style: {
                            'line-color': '#3DDC84',
                            'target-arrow-color': '#3DDC84'
                        }
                    },
                    {
                        selector: 'edge[relation="imports"]',
                        style: {
                            'line-color': '#FFC107',
                            'target-arrow-color': '#FFC107',
                            'line-style': 'dashed'
                        }
                    }
                ],
                layout: {
                    name: 'cose',
                    animate: false,
                    nodeDimensionsIncludeLabels: true,
                    randomize: true,
                    nodeRepulsion: 10000,
                    idealEdgeLength: 100,
                    edgeElasticity: 100,
                    nestingFactor: 5,
                    gravity: 80,
                    numIter: 1000,
                    initialTemp: 200,
                    coolingFactor: 0.95,
                    minTemp: 1.0
                }
            });
            
            log('Cytoscape initialized');
            
            // Node tooltip
            cy.on('tap', 'node', function(evt) {
                const node = evt.target;
                const position = node.renderedPosition();
                const data = node.data();
                
                tooltip.innerHTML = `
                    <strong>${data.label}</strong><br>
                    Type: ${data.type || 'Unknown'}<br>
                    Complexity: ${data.complexity || 0}<br>
                    Coverage: ${data.coverage || 0}%<br>
                    Churn: ${data.churn || 0} commits
                `;
                
                tooltip.style.display = 'block';
                tooltip.style.left = (position.x + 10) + 'px';
                tooltip.style.top = (position.y + 10) + 'px';
                
                log(`Node clicked: ${data.label}`);
            });
            
            // Hide tooltip on background click
            cy.on('tap', function(evt) {
                if (evt.target === cy) {
                    tooltip.style.display = 'none';
                }
            });
            
            // Reset button
            document.getElementById('reset-btn').addEventListener('click', function() {
                cy.fit();
                log('View reset');
            });
            
            // Wait for layout to complete then fit
            setTimeout(function() {
                cy.fit();
                log('Graph layout complete, view fitted');
            }, 1000);
            
        } catch (error) {
            log(`ERROR initializing: ${error.message}`);
            console.error(error);
        }
    });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the simplified graph visualization."""
    # Create a simple mock graph that will definitely render
    graph_data = {
        "nodes": [
            # Core modules
            {"data": {"id": "module1", "label": "Module 1", "complexity": 5, "coverage": 85, "churn": 10, "type": "module"}},
            {"data": {"id": "module2", "label": "Module 2", "complexity": 8, "coverage": 65, "churn": 15, "type": "module"}},
            {"data": {"id": "module3", "label": "Module 3", "complexity": 3, "coverage": 90, "churn": 5, "type": "module"}},
            
            # Classes
            {"data": {"id": "class1", "label": "Class 1", "complexity": 12, "coverage": 75, "churn": 18, "type": "class"}},
            {"data": {"id": "class2", "label": "Class 2", "complexity": 9, "coverage": 60, "churn": 12, "type": "class"}},
            
            # Functions and methods
            {"data": {"id": "function1", "label": "Function 1", "complexity": 7, "coverage": 80, "churn": 8, "type": "function"}},
            {"data": {"id": "function2", "label": "Function 2", "complexity": 15, "coverage": 40, "churn": 20, "type": "function"}},
            {"data": {"id": "method1", "label": "Method 1", "complexity": 6, "coverage": 70, "churn": 10, "type": "method"}},
            {"data": {"id": "method2", "label": "Method 2", "complexity": 18, "coverage": 30, "churn": 25, "type": "method"}}
        ],
        "edges": [
            {"data": {"source": "module1", "target": "module2", "relation": "imports"}},
            {"data": {"source": "module1", "target": "module3", "relation": "imports"}},
            {"data": {"source": "module2", "target": "class1", "relation": "imports"}},
            {"data": {"source": "class1", "target": "method1", "relation": "calls"}},
            {"data": {"source": "class1", "target": "method2", "relation": "calls"}},
            {"data": {"source": "module3", "target": "function1", "relation": "calls"}},
            {"data": {"source": "function1", "target": "function2", "relation": "calls"}},
            {"data": {"source": "method1", "target": "function2", "relation": "calls"}},
            {"data": {"source": "module2", "target": "class2", "relation": "imports"}},
            {"data": {"source": "class2", "target": "function1", "relation": "calls"}}
        ]
    }
    
    # Render the template with the graph data
    # Using safe json.dumps to ensure proper formatting
    return render_template_string(
        INDEX_HTML, 
        graph_data=json.dumps(graph_data)
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)