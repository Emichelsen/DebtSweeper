#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone Flask dashboard for DebtSweeper with improved graph visualization.
"""

import os
import json
import tempfile
import zipfile
import ast
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from flask import Flask, request, jsonify, send_file, redirect, url_for, Response

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# CSS styles as string (same as before)
CSS = """/* DebtSweeper High-Tech Theme */
:root {
  --primary-color: #3DDC84; /* Mint green */
  --secondary-color: #3DDC84;
  --dark-color: #000000;
  --light-color: #FFFFFF;
  --accent-color: #3DDC84;
  --danger-color: #e84118;
  --warning-color: #fbc531;
  --success-color: #3DDC84;
  --info-color: #3DDC84;
  --box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  --text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  --transition: all 0.3s ease;
}

body {
  font-family: 'JetBrains Mono', monospace;
  background-color: #000000;
  color: var(--light-color);
  line-height: 1.6;
}

/* Navbar styling */
.navbar {
  background: #000000;
  padding: 1rem 0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.navbar-brand, .logo-text {
  font-weight: 700;
  letter-spacing: 1px;
  position: relative;
  color: #FFFFFF;
  text-shadow: 0 0 4px rgba(255, 255, 255, 0.24);
}

/* Style for < and > characters */
.navbar-brand > span, .logo-text > span {
  color: var(--primary-color);
  text-shadow: 0 0 8px rgba(61, 220, 132, 0.41); /* Reduced glow by 15% */
}

.navbar-brand:hover {
  color: #FFFFFF;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.logo-text {
  margin-bottom: 1rem;
  font-size: 3.5rem;
  width: 100%;
  text-align: center;
  overflow-wrap: break-word;
  word-wrap: break-word;
  hyphens: auto;
}

.nav-link {
  position: relative;
  padding: 0.5rem 1rem;
  margin: 0 0.2rem;
  transition: var(--transition);
}

.nav-link::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--primary-color);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.nav-link:hover::before,
.nav-link.active::before {
  transform: scaleX(1);
}

/* Cyber-inspired hero section */
.hero {
  background: #000000;
  position: relative;
  overflow: hidden;
  padding: 5rem 0;
  margin-bottom: 2rem;
  box-shadow: var(--box-shadow);
  width: 100%;
}

.hero::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: repeating-linear-gradient(
    transparent 0,
    rgba(61, 220, 132, 0.05) 2px,
    transparent 3px
  );
  transform: rotate(45deg);
  z-index: 1;
  animation: grid-animation 20s linear infinite;
}

.hero h1 {
  position: relative;
  z-index: 2;
  text-shadow: var(--text-shadow);
  font-weight: 700;
  letter-spacing: 1px;
}

.hero p {
  position: relative;
  z-index: 2;
  opacity: 0.9;
}

@keyframes grid-animation {
  0% {
    transform: translateX(-50px) rotate(45deg);
  }
  100% {
    transform: translateX(50px) rotate(45deg);
  }
}

/* Cards with high-tech look */
.card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  box-shadow: var(--box-shadow);
  transition: var(--transition);
}

.card-header {
  background: #000000;
  border-bottom: 1px solid var(--primary-color);
  padding: 1rem 1.5rem;
}

.card-header h5, .card-title {
  margin: 0;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.card-title {
  position: relative;
  padding-bottom: 12px;
  margin-bottom: 15px;
}

.card-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background-color: var(--primary-color);
}

.debt-card {
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.debt-card::after {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    transparent,
    rgba(61, 220, 132, 0.2),
    transparent
  );
  transform: rotate(30deg);
  transition: var(--transition);
  opacity: 0;
}

.debt-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(61, 220, 132, 0.2);
}

.debt-card:hover::after {
  animation: card-shine 1.5s ease forwards;
}

@keyframes card-shine {
  0% {
    opacity: 0;
    left: -50%;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    left: 150%;
  }
}

/* Button styles */
.btn-primary, .bg-primary {
  background: #000000 !important;
  border: 2px solid var(--primary-color) !important;
  border-radius: 5px;
  box-shadow: 0 5px 15px rgba(61, 220, 132, 0.4);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
  z-index: 1;
  color: var(--primary-color) !important;
}

.btn-primary {
  padding: 0.7rem 1.5rem;
}

.btn-success {
  background: var(--primary-color) !important;
  border: none;
  color: #000000 !important;
  font-weight: bold;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: var(--transition);
  z-index: -1;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 168, 255, 0.5);
  background: #0088cc;
}

.btn-primary:hover::before {
  animation: btn-shine 1.5s infinite;
}

@keyframes btn-shine {
  100% {
    left: 200%;
  }
}

/* Circular steps */
.rounded-circle {
  transition: var(--transition);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  min-width: 40px;
  min-height: 40px;
  width: 40px !important;
  height: 40px !important;
  line-height: 40px;
  text-align: center;
  border-radius: 50% !important;
  flex-shrink: 0;
}

.d-flex:hover .rounded-circle {
  transform: scale(1.1);
  box-shadow: 0 5px 20px rgba(0, 168, 255, 0.4);
}

/* Footer */
footer {
  background: #000000;
  color: rgba(255, 255, 255, 0.7);
}

.creator {
  color: rgba(255, 255, 255, 0.85);
  font-style: italic;
  position: relative;
  transition: var(--transition);
}

.creator:hover {
  color: #FFFFFF;
}

/* Progress bars */
.progress {
  height: 12px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.progress-bar {
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.progress-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: progress-shine 2s infinite;
}

@keyframes progress-shine {
  100% {
    left: 200%;
  }
}

/* Code blocks */
pre {
  background: rgba(0, 0, 0, 0.3);
  border-left: 3px solid var(--primary-color);
  border-radius: 5px;
  padding: 1rem;
  font-family: 'JetBrains Mono', monospace;
  position: relative;
  overflow: hidden;
}

pre::before {
  content: "";
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: repeating-linear-gradient(
    transparent 0,
    rgba(0, 168, 255, 0.03) 2px,
    transparent 3px
  );
  transform: rotate(45deg);
  z-index: 1;
}

/* Tables */
.table {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  overflow: hidden;
}

.table thead th {
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 2px solid var(--primary-color);
  color: var(--primary-color);
}

.table tbody tr {
  transition: var(--transition);
}

.table tbody tr:hover {
  background: rgba(0, 168, 255, 0.05);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: #0088cc;
}

/* Specific fixes for the homepage container */
.homepage-container {
  padding-left: 30px !important;
  padding-right: 30px !important;
  max-width: 1140px;
  margin-left: auto;
  margin-right: auto;
}

/* Desktop specific fixes */
@media (min-width: 992px) {
  .homepage-container {
    max-width: 90%;
    width: 1020px;
  }
}

/* Mobile responsiveness fixes */
@media (max-width: 767px) {
  .logo-text {
    font-size: 2.8rem; /* Reduced size for mobile */
    padding: 0 10px;
  }

  .hero p.lead {
    font-size: 95%; /* Reduced by 5% as requested */
  }

  .container, .homepage-container {
    padding-left: 25px !important;
    padding-right: 25px !important;
  }
  
  /* Fix spacing for cards and other elements */
  .card {
    margin-left: 5px;
    margin-right: 5px;
  }
  
  .card-body {
    padding: 1.25rem;
  }
  
  /* Ensure buttons don't stretch to edges */
  .btn {
    margin: 5px 0;
  }

  /* Fix for iPhone portrait mode specific issues */
  @supports (-webkit-touch-callout: none) {
    .logo-text {
      /* Specific fixes for iOS */
      display: inline-block;
      max-width: 100%;
    }
    
    /* Fix for how it works bullets on iOS */
    .rounded-circle {
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      transform: translateZ(0);
      -webkit-transform: translateZ(0);
    }
  }
}

/* Cytoscape container styles */
#debt-graph {
    width: 100%;
    height: 600px;
    background-color: rgba(0, 0, 0, 0.6);
    border: 1px solid var(--primary-color);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: var(--box-shadow);
}

/* Node tooltip styles */
.cy-tooltip {
    position: absolute;
    background-color: #000;
    border: 1px solid var(--primary-color);
    color: #fff;
    padding: 12px;
    border-radius: 5px;
    z-index: 1000;
    font-size: 14px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    max-width: 300px;
    pointer-events: none;
}

@media (max-width: 767px) {
    #debt-graph {
        height: 450px;
    }
}
"""

# HTML templates as dictionaries
TEMPLATES = {
    'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DebtSweeper Dashboard</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Cytoscape.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
    <!-- Custom CSS -->
    <style>
    {{css}}
    </style>
</head>
<body>
    <div class="hero text-center">
        <h1 class="display-4 logo-text"><span>&lt;</span>DebtSweeper<span>&gt;</span></h1>
        <p class="lead">Automated technical debt detection and remediation</p>
    </div>

    <div class="homepage-container py-4">
        <div class="row mb-5">
            <div class="col-md-6 offset-md-3">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">Analyze Your Codebase</h5>
                    </div>
                    <div class="card-body">
                        <p>Upload a zipped repository to analyze its technical debt.</p>
                        <a href="/scan" class="btn btn-primary w-100">Start New Analysis</a>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-12">
                <h2>About DebtSweeper</h2>
                <p>
                    DebtSweeper is a tool that helps development teams identify and fix technical debt in their Python codebases.
                    It analyzes code for common debt patterns, scores each file based on its debt burden, and generates targeted
                    refactoring suggestions using AI.
                </p>
            </div>
        </div>

        <div class="row mb-5">
            <div class="col-md-4 mb-4">
                <div class="card h-100 debt-card">
                    <div class="card-body">
                        <h5 class="card-title">Precise Detection</h5>
                        <p class="card-text">Identifies specific debt patterns like long functions, high complexity, code duplication, and more.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 debt-card">
                    <div class="card-body">
                        <h5 class="card-title">AI-Powered Fixes</h5>
                        <p class="card-text">Leverages advanced language models to suggest targeted, context-aware code improvements.</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card h-100 debt-card">
                    <div class="card-body">
                        <h5 class="card-title">Debt Metrics</h5>
                        <p class="card-text">Provides quantitative scores to track and prioritize debt reduction efforts over time.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-5">
            <div class="col-12">
                <h2>Debt Knowledge Graph</h2>
                <p class="mb-4">
                    Visualize code dependencies and technical debt. Nodes represent functions and classes, 
                    while edges show relationships. Node size indicates complexity, and color reflects test coverage.
                </p>
                <div id="debt-graph"></div>
                <div class="mt-3 mb-4">
                    <small style="color: rgba(255, 255, 255, 0.8);">Click on nodes to see detailed debt metrics. Drag to pan, scroll to zoom.</small>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-12">
                <h2>How It Works</h2>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center">1</div>
                    <div class="ms-3">Upload your Python codebase as a zip file.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center">2</div>
                    <div class="ms-3">DebtSweeper analyzes code structure and patterns to identify technical debt.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center">3</div>
                    <div class="ms-3">Review debt items and their severity scores in an interactive dashboard.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center">4</div>
                    <div class="ms-3">Select debt items to fix and get AI-generated refactoring suggestions.</div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center">5</div>
                    <div class="ms-3">Apply patches to your codebase manually or through GitHub PRs.</div>
                </div>
            </div>
        </div>
    </div>

    <footer class="py-4 mt-5">
        <div class="homepage-container text-center">
            <p>DebtSweeper &copy; 2025 - <span class="creator">A product by Eduardo Michelsen</span></p>
        </div>
    </footer>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Debt Graph Visualization -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM loaded - initializing graph');
        
        // Make sure the container exists and has dimensions
        const container = document.getElementById('debt-graph');
        if (!container) {
            console.error('Container not found');
            return;
        }
        
        // Ensure container has dimensions
        if (container.offsetHeight < 100) {
            container.style.height = '600px';
        }
        
        // Parse the graph data
        let graphData;
        try {
            graphData = JSON.parse('{{ graph_json|safe }}');
            console.log('Graph data loaded with', graphData.nodes.length, 'nodes and', graphData.edges.length, 'edges');
        } catch (e) {
            console.error('Failed to parse graph data:', e);
            return;
        }
        
        // Create tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'cy-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            background-color: #000000;
            border: 1px solid #3DDC84;
            color: #ffffff;
            padding: 10px;
            border-radius: 5px;
            z-index: 9999;
            display: none;
            pointer-events: none;
            font-size: 14px;
        `;
        document.body.appendChild(tooltip);
        
        // Wait a bit for DOM to fully load
        setTimeout(() => {
            console.log('Initializing Cytoscape');
            
            try {
                // Create Cytoscape instance
                const cy = cytoscape({
                    container: container,
                    elements: graphData.nodes.concat(graphData.edges),
                    wheelSensitivity: 0.2,
                    minZoom: 0.1,
                    maxZoom: 2,
                    style: [
                        {
                            selector: 'node',
                            style: {
                                'label': 'data(label)',
                                'background-color': function(ele) {
                                    // Map coverage to color
                                    const coverage = ele.data('coverage');
                                    if (coverage >= 80) return '#3DDC84'; // High coverage (green)
                                    if (coverage >= 50) return '#FFC107'; // Medium coverage (yellow)
                                    return '#e84118';                     // Low coverage (red)
                                },
                                'width': function(ele) {
                                    // Map complexity to size
                                    const complexity = ele.data('complexity');
                                    return 20 + Math.min(complexity * 2, 50);
                                },
                                'height': function(ele) {
                                    // Map complexity to size
                                    const complexity = ele.data('complexity');
                                    return 20 + Math.min(complexity * 2, 50);
                                },
                                'font-size': '12px',
                                'color': function(ele) {
                                    // Different text colors for different types
                                    const type = ele.data('type');
                                    if (type === 'function') return '#FF79C6'; // Pink for functions
                                    if (type === 'class') return '#8BE9FD';    // Cyan for classes
                                    if (type === 'method') return '#50FA7B';   // Green for methods
                                    return '#F8F8F2';                          // White for modules
                                },
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'text-outline-width': 2,
                                'text-outline-color': '#000000',
                                'border-width': 2,
                                'border-color': '#000000'
                            }
                        },
                        {
                            selector: 'node[type="class"]',
                            style: {
                                'shape': 'rectangle',
                                'background-color': '#4B7BEC'
                            }
                        },
                        {
                            selector: 'node[type="method"]',
                            style: {
                                'shape': 'round-rectangle'
                            }
                        },
                        {
                            selector: 'node[type="module"]',
                            style: {
                                'shape': 'hexagon'
                            }
                        },
                        {
                            selector: 'edge',
                            style: {
                                'width': 2,
                                'line-color': function(ele) {
                                    // Different colors for different relation types
                                    const relation = ele.data('relation');
                                    if (relation === 'calls') return '#3DDC84';
                                    if (relation === 'imports') return '#FFC107';
                                    return '#AAAAAA';
                                },
                                'target-arrow-shape': 'triangle',
                                'target-arrow-color': function(ele) {
                                    // Match arrow color to line color
                                    const relation = ele.data('relation');
                                    if (relation === 'calls') return '#3DDC84';
                                    if (relation === 'imports') return '#FFC107';
                                    return '#AAAAAA';
                                },
                                'curve-style': 'bezier',
                                'opacity': 0.8
                            }
                        },
                        {
                            selector: 'edge[relation="calls"]',
                            style: {
                                'line-style': 'solid'
                            }
                        },
                        {
                            selector: 'edge[relation="imports"]',
                            style: {
                                'line-style': 'dashed'
                            }
                        },
                        {
                            selector: 'node[complexity >= 15][coverage <= 50]',
                            style: {
                                'border-width': 3,
                                'border-color': '#FF5555',
                                'border-style': 'dashed'
                            }
                        }
                    ]
                });
                
                console.log('Cytoscape instance created');
                
                // Node tap handler
                cy.on('tap', 'node', function(evt) {
                    const node = evt.target;
                    const data = node.data();
                    
                    // Format tooltip content
                    let content = `
                        <strong>${data.label}</strong> (${data.type})<br>
                        <hr style="margin: 5px 0; border-color: #3DDC84">
                        <strong>Complexity:</strong> ${data.complexity}<br>
                        <strong>Test Coverage:</strong> ${data.coverage}%<br>
                        <strong>Code Churn:</strong> ${data.churn} commits<br>
                    `;
                    
                    // Position and show tooltip
                    tooltip.innerHTML = content;
                    tooltip.style.display = 'block';
                    
                    const position = node.renderedPosition();
                    const nodeWidth = node.renderedWidth();
                    
                    tooltip.style.left = (position.x + nodeWidth/2 + 10) + 'px';
                    tooltip.style.top = (position.y - 30) + 'px';
                });
                
                // Hide tooltip when clicking elsewhere
                cy.on('tap', function(evt) {
                    if (evt.target === cy) {
                        tooltip.style.display = 'none';
                    }
                });
                
                // Run layout with more aggressive settings
                const layout = cy.layout({
                    name: 'cose',
                    animate: false,
                    nodeDimensionsIncludeLabels: true,
                    randomize: true,
                    refresh: 20,
                    fit: true,
                    padding: 30,
                    componentSpacing: 100,
                    nodeRepulsion: 800000,
                    nodeOverlap: 20,
                    idealEdgeLength: 100,
                    edgeElasticity: 100,
                    nestingFactor: 5,
                    gravity: 80,
                    numIter: 1000,
                    initialTemp: 200,
                    coolingFactor: 0.95,
                    minTemp: 1.0
                });
                
                layout.run();
                
                console.log('Layout run');
                
                // Make sure graph is visible
                setTimeout(() => {
                    cy.fit();
                    cy.zoom(cy.zoom() * 0.7);
                    cy.center();
                    console.log('Graph centered');
                }, 500);
                
            } catch (error) {
                console.error('Error initializing graph:', error);
            }
        }, 300);
    });
    </script>
</body>
</html>
''',
}

# Code for rendering templates and other flask routes
# (All the other functions from the original app would go here)

# Custom render_template function
def render_template(template_name, **context):
    """Render a template with the given context."""
    from flask import Response
    if template_name not in TEMPLATES:
        return f"Template {template_name} not found", 404
    
    template = TEMPLATES[template_name]
    
    # Replace CSS placeholder
    template = template.replace('{{css}}', CSS)
    
    # Handle special case for graph_json (to make it safe for use in JavaScript)
    if 'graph_json' in context:
        # Safely encode JSON for embedding in JavaScript
        graph_json_value = context['graph_json'].replace("'", "\\'").replace('\n', '\\n')
        template = template.replace("'{{ graph_json|safe }}'", graph_json_value)
    
    # More template processing as needed...
    
    return Response(template, mimetype='text/html')

@app.route('/')
def index():
    """Render the dashboard homepage."""
    # Create a realistic mock graph that resembles a Python application
    mock_graph = {
        "nodes": [
            # Core modules
            {"data": {"id": "app.main", "label": "main", "complexity": 6, "coverage": 85, "churn": 15, "type": "function"}},
            {"data": {"id": "app.config", "label": "config", "complexity": 4, "coverage": 90, "churn": 8, "type": "module"}},
            {"data": {"id": "app.routes", "label": "routes", "complexity": 7, "coverage": 75, "churn": 12, "type": "module"}},
            
            # API module
            {"data": {"id": "app.api.endpoints", "label": "endpoints", "complexity": 9, "coverage": 80, "churn": 18, "type": "module"}},
            {"data": {"id": "app.api.handlers", "label": "handlers", "complexity": 12, "coverage": 65, "churn": 20, "type": "module"}},
            {"data": {"id": "app.api.validators", "label": "validators", "complexity": 8, "coverage": 70, "churn": 12, "type": "module"}},
            
            # Database related
            {"data": {"id": "app.db.models", "label": "models", "complexity": 5, "coverage": 95, "churn": 10, "type": "module"}},
            {"data": {"id": "app.db.schema", "label": "schema", "complexity": 4, "coverage": 90, "churn": 6, "type": "module"}},
            {"data": {"id": "app.db.queries", "label": "queries", "complexity": 11, "coverage": 60, "churn": 22, "type": "module"}},
            {"data": {"id": "app.db.connection", "label": "connection", "complexity": 7, "coverage": 85, "churn": 9, "type": "module"}},
            
            # Auth module
            {"data": {"id": "app.auth.Auth", "label": "Auth", "complexity": 10, "coverage": 75, "churn": 14, "type": "class"}},
            {"data": {"id": "app.auth.Auth.login", "label": "login", "complexity": 14, "coverage": 50, "churn": 18, "type": "method"}},
            {"data": {"id": "app.auth.Auth.validate", "label": "validate", "complexity": 18, "coverage": 45, "churn": 15, "type": "method"}},
            {"data": {"id": "app.auth.Auth.logout", "label": "logout", "complexity": 3, "coverage": 95, "churn": 5, "type": "method"}},
            {"data": {"id": "app.auth.permissions", "label": "permissions", "complexity": 9, "coverage": 70, "churn": 13, "type": "module"}},
            
            # Utils
            {"data": {"id": "app.utils.formatters", "label": "formatters", "complexity": 6, "coverage": 80, "churn": 9, "type": "module"}},
            {"data": {"id": "app.utils.helpers", "label": "helpers", "complexity": 5, "coverage": 85, "churn": 11, "type": "module"}},
            {"data": {"id": "app.utils.logger", "label": "logger", "complexity": 3, "coverage": 90, "churn": 7, "type": "module"}},
            
            # Problem areas - high complexity, low coverage
            {"data": {"id": "app.services.processor", "label": "processor", "complexity": 20, "coverage": 35, "churn": 25, "type": "module"}},
            {"data": {"id": "app.services.analyzer", "label": "analyzer", "complexity": 17, "coverage": 40, "churn": 22, "type": "module"}},
            {"data": {"id": "app.services.DataHandler", "label": "DataHandler", "complexity": 15, "coverage": 45, "churn": 19, "type": "class"}},
            {"data": {"id": "app.services.DataHandler.process", "label": "process", "complexity": 25, "coverage": 30, "churn": 28, "type": "method"}},
            {"data": {"id": "app.services.DataHandler.transform", "label": "transform", "complexity": 22, "coverage": 35, "churn": 24, "type": "method"}},
            {"data": {"id": "app.services.DataHandler.validate", "label": "validate", "complexity": 16, "coverage": 50, "churn": 20, "type": "method"}}
        ],
        "edges": [
            # Main app connections
            {"data": {"source": "app.main", "target": "app.config", "relation": "imports"}},
            {"data": {"source": "app.main", "target": "app.routes", "relation": "imports"}},
            {"data": {"source": "app.main", "target": "app.utils.logger", "relation": "imports"}},
            {"data": {"source": "app.routes", "target": "app.api.endpoints", "relation": "imports"}},
            {"data": {"source": "app.routes", "target": "app.auth.Auth", "relation": "imports"}},
            
            # API connections
            {"data": {"source": "app.api.endpoints", "target": "app.api.handlers", "relation": "calls"}},
            {"data": {"source": "app.api.handlers", "target": "app.api.validators", "relation": "calls"}},
            {"data": {"source": "app.api.handlers", "target": "app.services.processor", "relation": "calls"}},
            {"data": {"source": "app.api.handlers", "target": "app.auth.Auth.validate", "relation": "calls"}},
            {"data": {"source": "app.api.validators", "target": "app.utils.formatters", "relation": "calls"}},
            
            # Database relationships
            {"data": {"source": "app.api.handlers", "target": "app.db.queries", "relation": "calls"}},
            {"data": {"source": "app.db.queries", "target": "app.db.connection", "relation": "calls"}},
            {"data": {"source": "app.db.queries", "target": "app.db.models", "relation": "imports"}},
            {"data": {"source": "app.db.models", "target": "app.db.schema", "relation": "imports"}},
            
            # Auth module relationships
            {"data": {"source": "app.auth.Auth.login", "target": "app.db.queries", "relation": "calls"}},
            {"data": {"source": "app.auth.Auth.validate", "target": "app.auth.permissions", "relation": "calls"}},
            {"data": {"source": "app.auth.permissions", "target": "app.db.models", "relation": "imports"}},
            
            # Service module relationships - problem area
            {"data": {"source": "app.services.processor", "target": "app.services.analyzer", "relation": "calls"}},
            {"data": {"source": "app.services.processor", "target": "app.services.DataHandler", "relation": "calls"}},
            {"data": {"source": "app.services.DataHandler.process", "target": "app.services.DataHandler.transform", "relation": "calls"}},
            {"data": {"source": "app.services.DataHandler.transform", "target": "app.services.DataHandler.validate", "relation": "calls"}},
            {"data": {"source": "app.services.DataHandler.process", "target": "app.utils.logger", "relation": "calls"}},
            {"data": {"source": "app.services.analyzer", "target": "app.utils.helpers", "relation": "calls"}},
            
            # Utils relationships
            {"data": {"source": "app.utils.formatters", "target": "app.utils.helpers", "relation": "calls"}},
            {"data": {"source": "app.routes", "target": "app.utils.formatters", "relation": "calls"}},
            {"data": {"source": "app.utils.logger", "target": "app.utils.formatters", "relation": "calls"}},
            
            # Additional connections to show complex dependencies
            {"data": {"source": "app.services.analyzer", "target": "app.db.queries", "relation": "calls"}},
            {"data": {"source": "app.api.endpoints", "target": "app.utils.helpers", "relation": "calls"}},
            {"data": {"source": "app.services.DataHandler.validate", "target": "app.api.validators", "relation": "calls"}}
        ]
    }
    
    graph_json = json.dumps(mock_graph)
    return render_template('index.html', graph_json=graph_json)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)