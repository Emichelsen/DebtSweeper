#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Standalone Flask dashboard for DebtSweeper with embedded templates and CSS.

Provides a web interface for visualizing debt scores and managing fixes.
Everything is embedded in this single file for easy deployment.
"""

import os
import json
import tempfile
import zipfile
import ast
import subprocess
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from flask import Flask, request, jsonify, send_file, redirect, url_for

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# CSS styles as string
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
                <div class="mt-3">
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
        // Parse the graph data from the template
        const graphData = JSON.parse('{{ graph_json|safe }}');
        
        // Create a tooltip element
        const tooltip = document.createElement('div');
        tooltip.className = 'cy-tooltip';
        tooltip.style.display = 'none';
        document.body.appendChild(tooltip);
        
        // Initialize Cytoscape
        const cy = cytoscape({
            container: document.getElementById('debt-graph'),
            elements: [...graphData.nodes, ...graphData.edges],
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'background-color': function(ele) {
                            // Map coverage to color (green to red)
                            const coverage = ele.data('coverage');
                            if (coverage >= 80) return '#3DDC84'; // High coverage (green)
                            if (coverage >= 50) return '#FFC107'; // Medium coverage (yellow)
                            return '#E84118';                     // Low coverage (red)
                        },
                        'width': function(ele) {
                            // Map complexity to size
                            const complexity = ele.data('complexity');
                            return 20 + Math.min(complexity * 2, 50); // Base size + complexity factor (capped)
                        },
                        'height': function(ele) {
                            // Map complexity to size
                            const complexity = ele.data('complexity');
                            return 20 + Math.min(complexity * 2, 50); // Base size + complexity factor (capped)
                        },
                        'font-size': '10px',
                        'color': '#FFFFFF',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'text-outline-width': 1,
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
                        'curve-style': 'bezier'
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
                }
            ],
            layout: {
                name: 'cose',
                nodeDimensionsIncludeLabels: true,
                animate: false,
                fit: true,
                padding: 50
            }
        });
        
        // Add tap handler for nodes (show tooltip with details)
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            
            // Format the tooltip content
            let content = `
                <strong>${data.label}</strong> (${data.type})<br>
                <hr style="margin: 5px 0; border-color: var(--primary-color)">
                <strong>Complexity:</strong> ${data.complexity}<br>
                <strong>Test Coverage:</strong> ${data.coverage}%<br>
                <strong>Code Churn:</strong> ${data.churn} commits<br>
            `;
            
            // Position and show the tooltip
            tooltip.innerHTML = content;
            tooltip.style.display = 'block';
            
            // Position near the node but not directly on top
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
        
        // Add responsive features
        cy.userZoomingEnabled(true);
        cy.userPanningEnabled(true);
        cy.boxSelectionEnabled(true);
        
        // Add double tap to zoom on mobile
        let tappedBefore;
        let tappedTimeout;
        
        cy.on('tap', function(event) {
            if (tappedTimeout && tappedBefore) {
                clearTimeout(tappedTimeout);
                if (event.target === tappedBefore) {
                    // Zoom in to the tapped position
                    cy.animate({
                        zoom: cy.zoom() * 1.5,
                        center: { x: event.position.x, y: event.position.y }
                    }, {
                        duration: 300
                    });
                }
                tappedBefore = null;
            } else {
                tappedTimeout = setTimeout(function() { tappedBefore = null; }, 300);
                tappedBefore = event.target;
            }
        });
    });
    </script>
</body>
</html>
''',
    
    'scan.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repository Scan - DebtSweeper</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
    {{css}}
    .progress-container {
        display: none;
    }
    .results-container {
        display: none;
    }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span>&lt;</span>DebtSweeper<span>&gt;</span></a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/scan">Scan</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <h1 class="mb-4">Scan Repository</h1>
        
        <!-- Upload Form -->
        <div class="upload-container">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Upload a Repository</h5>
                    <p class="card-text">Select a ZIP file containing your Python repository. Max size: 100MB.</p>
                    
                    <form id="scan-form" enctype="multipart/form-data">
                        <div class="mb-3">
                            <label for="repo-zip" class="form-label">Repository ZIP</label>
                            <input type="file" class="form-control" id="repo-zip" name="repo_zip" accept=".zip" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Scan Repository</button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Progress Indicator -->
        <div class="progress-container mt-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Scanning Repository</h5>
                    <p class="card-text">Please wait while we analyze your codebase...</p>
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 100%"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Results Display -->
        <div class="results-container mt-4">
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Scan Results</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h6 class="card-subtitle mb-2 text-muted">Repository Debt Score</h6>
                                    <h2 id="repo-score" class="display-4 text-primary">0.0</h2>
                                    <p class="card-text"><small class="text-muted">Lower is better (0-1 scale)</small></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h6 class="card-subtitle mb-2 text-muted">Total Debt Items</h6>
                                    <h2 id="total-debt-items" class="display-4 text-primary">0</h2>
                                    <p class="card-text"><small class="text-muted">Issues detected</small></p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 mb-3">
                            <div class="card h-100">
                                <div class="card-body text-center">
                                    <h6 class="card-subtitle mb-2 text-muted">Total Lines of Code</h6>
                                    <h2 id="total-loc" class="display-4 text-primary">0</h2>
                                    <p class="card-text"><small class="text-muted">Python code</small></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Debt By Type</h5>
                </div>
                <div class="card-body">
                    <div id="debt-by-type" class="row">
                        <!-- Will be populated by JavaScript -->
                    </div>
                </div>
            </div>

            <div class="card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Debt Knowledge Graph</h5>
                </div>
                <div class="card-body">
                    <p class="mb-3">
                        Interactive visualization of code dependencies and technical debt:
                    </p>
                    <div id="debt-graph" style="width: 100%; height: 500px; background-color: rgba(0, 0, 0, 0.6); border: 1px solid var(--primary-color); border-radius: 10px; overflow: hidden; box-shadow: var(--box-shadow);"></div>
                    <div class="mt-3">
                        <small class="text-muted">
                            <strong>Node size</strong>: Complexity | 
                            <strong>Node color</strong>: Test coverage (green = high, yellow = medium, red = low) | 
                            <strong>Edge type</strong>: Solid green = function calls, dashed yellow = imports
                        </small>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <a href="#" class="btn btn-success w-100 mb-2">Generate All Fixes</a>
                        </div>
                        <div class="col-md-6">
                            <a href="#" class="btn btn-outline-primary w-100 mb-2">View Files</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="py-4 mt-5">
        <div class="container text-center">
            <p>DebtSweeper &copy; 2025 - <span class="creator">A product by Eduardo Michelsen</span></p>
        </div>
    </footer>

    <!-- Bootstrap JS and dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Cytoscape.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
    
    <!-- Page-specific JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('scan-form');
            const uploadContainer = document.querySelector('.upload-container');
            const progressContainer = document.querySelector('.progress-container');
            const resultsContainer = document.querySelector('.results-container');
            
            // Create tooltip element for the graph
            const tooltip = document.createElement('div');
            tooltip.className = 'cy-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background-color: #000;
                border: 1px solid #3DDC84;
                color: #fff;
                padding: 12px;
                border-radius: 5px;
                z-index: 1000;
                font-size: 14px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                max-width: 300px;
                pointer-events: none;
                display: none;
            `;
            document.body.appendChild(tooltip);
            
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Show progress indicator
                uploadContainer.style.display = 'none';
                progressContainer.style.display = 'block';
                
                // Prepare form data
                const formData = new FormData(form);
                
                // Send AJAX request
                fetch('/scan', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    // Hide progress indicator
                    progressContainer.style.display = 'none';
                    
                    // Update results
                    document.getElementById('repo-score').textContent = data.repo_score.toFixed(2);
                    document.getElementById('total-debt-items').textContent = data.total_debt_items;
                    document.getElementById('total-loc').textContent = data.total_loc.toLocaleString();
                    
                    // Update debt by type
                    const debtByTypeContainer = document.getElementById('debt-by-type');
                    debtByTypeContainer.innerHTML = '';
                    
                    for (const [type, count] of Object.entries(data.items_by_type)) {
                        const debtTypeHTML = `
                            <div class="col-md-4 mb-3">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <h5 class="card-title">${formatDebtType(type)}</h5>
                                        <p class="card-text">${count} issues</p>
                                    </div>
                                </div>
                            </div>
                        `;
                        debtByTypeContainer.innerHTML += debtTypeHTML;
                    }
                    
                    // Initialize debt graph with Cytoscape.js
                    if (data.graph_data && data.graph_data.nodes) {
                        initializeDebtGraph(data.graph_data);
                    }
                    
                    // Show results
                    resultsContainer.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while scanning the repository. Please try again.');
                    
                    // Reset UI
                    progressContainer.style.display = 'none';
                    uploadContainer.style.display = 'block';
                });
            });
            
            // Helper function to format debt type
            function formatDebtType(type) {
                return type.split('_')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
            }
            
            // Initialize the debt graph visualization
            function initializeDebtGraph(graphData) {
                const graphContainer = document.getElementById('debt-graph');
                if (!graphContainer) return;
                
                // Initialize Cytoscape
                const cy = cytoscape({
                    container: graphContainer,
                    elements: [...graphData.nodes, ...graphData.edges],
                    style: [
                        {
                            selector: 'node',
                            style: {
                                'label': 'data(label)',
                                'background-color': function(ele) {
                                    // Map coverage to color (green to red)
                                    const coverage = ele.data('coverage');
                                    if (coverage >= 80) return '#3DDC84'; // High coverage (green)
                                    if (coverage >= 50) return '#FFC107'; // Medium coverage (yellow)
                                    return '#E84118';                     // Low coverage (red)
                                },
                                'width': function(ele) {
                                    // Map complexity to size
                                    const complexity = ele.data('complexity');
                                    return 20 + Math.min(complexity * 2, 50); // Base size + complexity factor (capped)
                                },
                                'height': function(ele) {
                                    // Map complexity to size
                                    const complexity = ele.data('complexity');
                                    return 20 + Math.min(complexity * 2, 50); // Base size + complexity factor (capped)
                                },
                                'font-size': '10px',
                                'color': '#FFFFFF',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'text-outline-width': 1,
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
                                'curve-style': 'bezier'
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
                        }
                    ],
                    layout: {
                        name: 'cose',
                        nodeDimensionsIncludeLabels: true,
                        animate: false,
                        fit: true,
                        padding: 50
                    }
                });
                
                // Add tap handler for nodes (show tooltip with details)
                cy.on('tap', 'node', function(evt) {
                    const node = evt.target;
                    const data = node.data();
                    
                    // Format the tooltip content
                    let content = `
                        <strong>${data.label}</strong> (${data.type})<br>
                        <hr style="margin: 5px 0; border-color: #3DDC84">
                        <strong>Complexity:</strong> ${data.complexity}<br>
                        <strong>Test Coverage:</strong> ${data.coverage}%<br>
                        <strong>Code Churn:</strong> ${data.churn} commits<br>
                    `;
                    
                    // Position and show the tooltip
                    tooltip.innerHTML = content;
                    tooltip.style.display = 'block';
                    
                    // Position near the node but not directly on top
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
                
                // Add responsive features
                cy.userZoomingEnabled(true);
                cy.userPanningEnabled(true);
                cy.boxSelectionEnabled(true);
            }
        });
    </script>
</body>
</html>
''',
    
    'file.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ file_path }} - DebtSweeper</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Prism.js for syntax highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-tomorrow.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
    {{css}}
    .debt-item {
        cursor: pointer;
        border-left: 4px solid var(--danger-color);
        transition: background-color 0.2s;
    }
    .debt-item:hover {
        background-color: rgba(232, 65, 24, 0.1);
    }
    pre {
        max-height: 400px;
        overflow-y: auto;
    }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><span>&lt;</span>DebtSweeper<span>&gt;</span></a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/scan">Scan</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/scan">Scan Results</a></li>
                <li class="breadcrumb-item active">{{ file_path }}</li>
            </ol>
        </nav>

        <div class="row mb-4">
            <div class="col-md-8">
                <h1>{{ file_path.split('/')[-1] }}</h1>
                <p class="text-muted">{{ file_path }}</p>
            </div>
            <div class="col-md-4 text-end">
                <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#suggestFixesModal">Suggest Fixes</button>
            </div>
        </div>

        <div class="row mb-4">
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h6 class="card-subtitle mb-2 text-muted">Debt Score</h6>
                        <h2 class="display-4 text-primary">{{ "%.2f"|format(file_score.debt_score) }}</h2>
                        <p class="card-text"><small class="text-muted">Lower is better (0-1 scale)</small></p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h6 class="card-subtitle mb-2 text-muted">Debt Items</h6>
                        <h2 class="display-4 text-primary">{{ debt_items|length }}</h2>
                        <p class="card-text"><small class="text-muted">Issues detected</small></p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card h-100">
                    <div class="card-body text-center">
                        <h6 class="card-subtitle mb-2 text-muted">Lines of Code</h6>
                        <h2 class="display-4 text-primary">{{ loc }}</h2>
                        <p class="card-text"><small class="text-muted">Python code</small></p>
                    </div>
                </div>
            </div>
        </div>

        {% if debt_items %}
        <div class="card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">Debt Items</h5>
            </div>
            <div class="card-body">
                <div class="list-group">
                    {% for item in debt_items %}
                    <div class="list-group-item debt-item" data-debt-id="{{ loop.index0 }}">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">{{ item.debt_type.replace('_', ' ').title() }}</h5>
                            <span class="badge bg-danger">Severity: {{ "%.2f"|format(item.severity) }}</span>
                        </div>
                        <p class="mb-1">{{ item.message }}</p>
                        <small>Lines {{ item.line_start }}-{{ item.line_end }}</small>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% else %}
        <div class="alert alert-success">
            <h4 class="alert-heading">No Debt Found!</h4>
            <p>This file doesn't have any detected technical debt. Great job!</p>
        </div>
        {% endif %}

        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">File Content</h5>
            </div>
            <div class="card-body">
                <pre><code class="language-python">{{ file_content|default('File content not available') }}</code></pre>
            </div>
        </div>
    </div>

    <!-- Suggest Fixes Modal -->
    <div class="modal fade" id="suggestFixesModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Suggest Fixes</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form id="suggest-fixes-form" action="/suggest/{{ file_path }}" method="post">
                        <p>Select the debt items you want to fix:</p>
                        
                        <div class="list-group mb-3">
                            {% for item in debt_items %}
                            <label class="list-group-item">
                                <input class="form-check-input me-1" type="checkbox" name="debt_item_ids" value="{{ loop.index0 }}">
                                <div>
                                    <strong>{{ item.debt_type.replace('_', ' ').title() }}</strong>
                                    <p class="mb-1">{{ item.message }}</p>
                                    <small>Lines {{ item.line_start }}-{{ item.line_end }}</small>
                                </div>
                            </label>
                            {% endfor %}
                        </div>
                        
                        <div class="alert alert-info">
                            <p class="mb-0">DebtSweeper will analyze the selected items and generate refactoring suggestions.</p>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="submit" form="suggest-fixes-form" class="btn btn-primary">Generate Suggestions</button>
                </div>
            </div>
        </div>
    </div>

    <footer class="py-4 mt-5">
        <div class="container text-center">
            <p>DebtSweeper &copy; 2025 - <span class="creator">A product by Eduardo Michelsen</span></p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Prism.js for syntax highlighting -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/autoloader/prism-autoloader.min.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Handle form submission via AJAX
            const suggestForm = document.getElementById('suggest-fixes-form');
            
            suggestForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Collect form data
                const formData = new FormData(suggestForm);
                
                // Submit via fetch
                fetch(suggestForm.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('suggestFixesModal'));
                    modal.hide();
                    
                    // Show success message
                    alert(data.message);
                    
                    // Optional: Redirect to patch download
                    if (data.patch_url) {
                        window.location.href = data.patch_url;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while generating fix suggestions.');
                });
            });
            
            // Highlight debt items in code
            const debtItems = document.querySelectorAll('.debt-item');
            
            debtItems.forEach(item => {
                item.addEventListener('click', function() {
                    const debtId = this.dataset.debtId;
                    // TODO: Implement code highlighting based on line numbers
                    console.log('Clicked on debt item', debtId);
                });
            });
        });
    </script>
</body>
</html>
'''
}

# Mock implementations for Debt Sweeper modules
class DebtScorer:
    def score_file(self, file_path, debt_items, loc):
        return FileScore(file_path, debt_items, loc)
    
    def score_repo(self, repo_path, file_scores):
        return RepoScore(repo_path, file_scores)

class FileScore:
    def __init__(self, file_path, debt_items, loc):
        self.file_path = file_path
        self.debt_items = debt_items
        self.loc = loc
        self.debt_score = 0.5  # Mock score for demo

class RepoScore:
    def __init__(self, repo_path, file_scores):
        self.repo_path = repo_path
        self.file_scores = file_scores
        self.debt_score = 0.6  # Mock score for demo
        self.total_debt_items = 42  # Mock count for demo
        self.total_loc = 10000  # Mock LOC for demo
        self.items_by_type = {
            "long_function": 12,
            "high_complexity": 8,
            "code_duplication": 5,
            "unused_imports": 7,
            "poor_naming": 10
        }

def analyze_file(path):
    """Mock implementation of debt analysis."""
    return [
        {
            "debt_type": "long_function",
            "message": "Function is too long (50 lines)",
            "line_start": 10,
            "line_end": 60,
            "severity": 0.8
        },
        {
            "debt_type": "high_complexity",
            "message": "Function has high cyclomatic complexity (15)",
            "line_start": 25,
            "line_end": 40,
            "severity": 0.7
        }
    ]

class LLMOrchestrator:
    pass

class RefactorSuggestion:
    pass

class PatchGenerator:
    pass

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
    
    # Replace template variables
    for key, value in context.items():
        if isinstance(value, (int, float, str, bool)):
            template = template.replace('{{ ' + key + ' }}', str(value))
            template = template.replace('{{' + key + '}}', str(value))
        # For more complex objects, you'd need Jinja2-like processing
        
    # Simple implementation of some Jinja2 syntax
    # Handle {% if ... %} ... {% else %} ... {% endif %}
    # This is a very basic implementation that only works for simple cases
    if 'debt_items' in context:
        if len(context['debt_items']) > 0:
            template = template.replace('{% if debt_items %}', '')
            template = template.replace('{% else %}', '<!--')
            template = template.replace('{% endif %}', '-->')
        else:
            template = template.replace('{% if debt_items %}', '<!--')
            template = template.replace('{% else %}', '-->')
            template = template.replace('{% endif %}', '')
    
    # Simple loop handling for debt items
    if 'debt_items' in context and '{% for item in debt_items %}' in template:
        debt_items_html = ''
        for idx, item in enumerate(context['debt_items']):
            loop_item = template.split('{% for item in debt_items %}')[1].split('{% endfor %}')[0]
            
            # Replace loop variables
            loop_item = loop_item.replace('{{ loop.index0 }}', str(idx))
            loop_item = loop_item.replace('{{ item.debt_type.replace(\'_\', \' \').title() }}', 
                                          item['debt_type'].replace('_', ' ').title())
            loop_item = loop_item.replace('{{ "%.2f"|format(item.severity) }}', f"{item['severity']:.2f}")
            loop_item = loop_item.replace('{{ item.message }}', item['message'])
            loop_item = loop_item.replace('{{ item.line_start }}', str(item['line_start']))
            loop_item = loop_item.replace('{{ item.line_end }}', str(item['line_end']))
            
            debt_items_html += loop_item
        
        template = template.replace(
            template.split('{% for item in debt_items %}')[0] + 
            '{% for item in debt_items %}' + 
            template.split('{% for item in debt_items %}')[1].split('{% endfor %}')[0] + 
            '{% endfor %}',
            template.split('{% for item in debt_items %}')[0] + debt_items_html
        )
    
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


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    """Handle repository scanning and display results."""
    if request.method == 'POST':
        # Check if a zip file was uploaded
        if 'repo_zip' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        repo_zip = request.files['repo_zip']
        if repo_zip.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save the zip file
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(repo_zip.filename))
        repo_zip.save(zip_path)
        
        # Extract the zip file
        extract_path = os.path.join(app.config['UPLOAD_FOLDER'], 'repo')
        os.makedirs(extract_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        
        # Scan the repository
        repo_score, graph_json = scan_repository(extract_path)
        
        # Return results as JSON
        return jsonify({
            'repo_score': repo_score.debt_score,
            'total_debt_items': repo_score.total_debt_items,
            'total_loc': repo_score.total_loc,
            'items_by_type': repo_score.items_by_type,
            'graph_data': graph_json,
            # Add more data as needed
        })
    
    # GET request - show upload form
    return render_template('scan.html')


@app.route('/file/<path:file_path>')
def view_file(file_path):
    """View details for a specific file."""
    # Convert path to absolute path within extracted repo
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], 'repo', file_path)
    
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Analyze the file
    debt_items = analyze_file(full_path)
    
    # Count lines of code
    with open(full_path, 'r') as f:
        loc = sum(1 for _ in f)
    
    # Score the file
    file_score = scorer.score_file(file_path, debt_items, loc)
    
    # Read file content for display
    try:
        with open(full_path, 'r') as f:
            file_content = f.read()
    except:
        file_content = "Unable to read file content"
    
    # Render template with file details
    return render_template(
        'file.html',
        file_path=file_path,
        file_score=file_score,
        debt_items=debt_items,
        loc=loc,
        file_content=file_content
    )


@app.route('/suggest/<path:file_path>', methods=['POST'])
def suggest_fixes(file_path):
    """Generate fix suggestions for a file."""
    # Convert path to absolute path within extracted repo
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], 'repo', file_path)
    
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Get debt item IDs to fix from the form
    debt_item_ids = request.form.getlist('debt_item_ids', type=int)
    
    if not debt_item_ids:
        return jsonify({'error': 'No debt items selected'}), 400
    
    # TODO: Implement actual fix generation
    # This is a placeholder
    
    return jsonify({
        'message': f'Generated fixes for {len(debt_item_ids)} debt items in {file_path}',
        'patch_url': url_for('download_patch', file_path=file_path)
    })


@app.route('/patch/<path:file_path>')
def download_patch(file_path):
    """Download a patch file for fixes."""
    # Convert path to absolute path within extracted repo
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], 'repo', file_path)
    
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # TODO: Implement actual patch generation and download
    # This is a placeholder
    
    patch_content = f"""diff --git a/{file_path} b/{file_path}
--- a/{file_path}
+++ b/{file_path}
@@ -1,5 +1,5 @@
-# Example patch
+# Example patched content
 """
    
    # Create a temporary patch file
    with tempfile.NamedTemporaryFile(suffix='.patch', delete=False) as temp:
        temp.write(patch_content.encode('utf-8'))
        temp_path = temp.name
    
    return send_file(
        temp_path,
        as_attachment=True,
        download_name=f"{os.path.basename(file_path)}.patch",
        mimetype='text/plain'
    )


class CodeGraphBuilder:
    """Builds a code dependency graph from Python files."""
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.graph = nx.DiGraph()
        self.function_map = {}  # Maps function IDs to their full path
        self.file_map = {}      # Maps file paths to their modules
        
    def build_graph(self):
        """Builds the graph by analyzing Python files."""
        python_files = self._find_python_files()
        
        # First pass: collect all function definitions
        for file_path in python_files:
            self._analyze_file_definitions(file_path)
        
        # Second pass: analyze function calls and imports
        for file_path in python_files:
            self._analyze_file_calls(file_path)
            
        # Add metrics to nodes
        self._add_complexity_metrics()
        self._add_churn_metrics()
        self._add_coverage_metrics()
        
        return self.graph
    
    def _find_python_files(self):
        """Find all Python files in the repository."""
        python_files = []
        exclude_patterns = ["**/.git/**", "**/venv/**", "**/__pycache__/**", "**/node_modules/**"]
        
        for root, dirs, files in os.walk(self.repo_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(Path(os.path.join(root, d)).match(pattern) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                if file_path.endswith('.py') and not any(Path(file_path).match(pattern) for pattern in exclude_patterns):
                    python_files.append(file_path)
        
        return python_files
    
    def _analyze_file_definitions(self, file_path):
        """Analyze file to extract function definitions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate module name from file path
            rel_path = os.path.relpath(file_path, self.repo_path)
            module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            self.file_map[file_path] = module_name
            
            # Parse the file
            tree = ast.parse(content, filename=file_path)
            
            # Extract function definitions
            visitor = FunctionDefVisitor(file_path, module_name)
            visitor.visit(tree)
            
            # Add functions to graph
            for func_id, func_data in visitor.functions.items():
                self.graph.add_node(func_id, **func_data)
                self.function_map[func_id] = file_path
                
        except Exception as e:
            print(f"Error analyzing definitions in {file_path}: {str(e)}")
    
    def _analyze_file_calls(self, file_path):
        """Analyze file to extract function calls and imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            module_name = self.file_map.get(file_path, '')
            
            # Parse the file
            tree = ast.parse(content, filename=file_path)
            
            # Extract function calls
            visitor = FunctionCallVisitor(file_path, module_name, self.function_map)
            visitor.visit(tree)
            
            # Add edges to graph for function calls
            for caller, callee in visitor.calls:
                if caller in self.graph and callee in self.graph:
                    self.graph.add_edge(caller, callee, relation="calls")
            
            # Add edges for imports
            for importer, importee in visitor.imports:
                if importer in self.graph and importee in self.graph:
                    self.graph.add_edge(importer, importee, relation="imports")
                
        except Exception as e:
            print(f"Error analyzing calls in {file_path}: {str(e)}")
    
    def _add_complexity_metrics(self):
        """Add cyclomatic complexity metrics to graph nodes."""
        # In a real implementation, use tools like radon or directly compute McCabe complexity
        # For this example, we'll use random values
        import random
        for node in self.graph.nodes:
            self.graph.nodes[node]['complexity'] = random.randint(1, 20)
    
    def _add_churn_metrics(self):
        """Add code churn metrics based on git history."""
        # In a real implementation, use GitPython or subprocess to run git log
        # For this example, we'll use random values
        import random
        for node in self.graph.nodes:
            self.graph.nodes[node]['churn'] = random.randint(0, 30)
    
    def _add_coverage_metrics(self):
        """Add test coverage metrics to graph nodes."""
        # In a real implementation, integrate with Coverage.py
        # For this example, we'll use random values
        import random
        for node in self.graph.nodes:
            self.graph.nodes[node]['coverage'] = random.randint(0, 100)
    
    def export_cytoscape_json(self):
        """Export the graph in Cytoscape.js format."""
        nodes = []
        edges = []
        
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            nodes.append({
                "data": {
                    "id": node_id,
                    "label": node_data.get("name", node_id.split(".")[-1]),
                    "complexity": node_data.get("complexity", 0),
                    "coverage": node_data.get("coverage", 0),
                    "churn": node_data.get("churn", 0),
                    "type": node_data.get("type", "function"),
                    "file": node_data.get("file", "")
                }
            })
        
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "data": {
                    "source": source,
                    "target": target,
                    "relation": data.get("relation", "unknown")
                }
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }


class FunctionDefVisitor(ast.NodeVisitor):
    """AST visitor to extract function definitions."""
    
    def __init__(self, file_path, module_name):
        self.file_path = file_path
        self.module_name = module_name
        self.current_class = None
        self.functions = {}
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Add class as a node
        class_id = f"{self.module_name}.{node.name}"
        self.functions[class_id] = {
            "name": node.name,
            "type": "class",
            "file": self.file_path,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        }
        
        # Visit all the methods
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        # Construct function ID
        if self.current_class:
            func_id = f"{self.module_name}.{self.current_class}.{node.name}"
        else:
            func_id = f"{self.module_name}.{node.name}"
        
        # Store function information
        self.functions[func_id] = {
            "name": node.name,
            "type": "method" if self.current_class else "function",
            "file": self.file_path,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
        }
        
        # Continue visiting children
        self.generic_visit(node)


class FunctionCallVisitor(ast.NodeVisitor):
    """AST visitor to extract function calls and imports."""
    
    def __init__(self, file_path, module_name, function_map):
        self.file_path = file_path
        self.module_name = module_name
        self.function_map = function_map
        self.current_class = None
        self.current_function = None
        self.calls = []
        self.imports = []
    
    def visit_ClassDef(self, node):
        """Visit class definition."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Visit all the methods
        self.generic_visit(node)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit function definition."""
        old_function = self.current_function
        
        # Construct function ID
        if self.current_class:
            self.current_function = f"{self.module_name}.{self.current_class}.{node.name}"
        else:
            self.current_function = f"{self.module_name}.{node.name}"
        
        # Visit the function body to find calls
        self.generic_visit(node)
        
        self.current_function = old_function
    
    def visit_Call(self, node):
        """Visit function call."""
        if self.current_function:
            callee = None
            
            # Handle simple name calls
            if isinstance(node.func, ast.Name):
                # Direct function call like "func()"
                # In a real implementation, you'd need to resolve this with scope analysis
                callee = f"{self.module_name}.{node.func.id}"
            
            # Handle attribute calls
            elif isinstance(node.func, ast.Attribute):
                # Method call like "obj.method()"
                # This is a simplification - proper resolution would be more complex
                if isinstance(node.func.value, ast.Name):
                    # Try to resolve some common patterns
                    if node.func.value.id == 'self' and self.current_class:
                        callee = f"{self.module_name}.{self.current_class}.{node.func.attr}"
                    else:
                        # This is a best guess - would need proper resolution in a real impl
                        callee = f"{node.func.value.id}.{node.func.attr}"
            
            # Add the call relation if we identified the callee
            if callee and callee in self.function_map:
                self.calls.append((self.current_function, callee))
        
        # Continue looking for nested calls
        self.generic_visit(node)
    
    def visit_Import(self, node):
        """Visit import statement."""
        if self.current_function:
            for name in node.names:
                # Simplified import handling - would need proper resolution
                if name.name in self.function_map:
                    self.imports.append((self.current_function, name.name))
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from-import statement."""
        if self.current_function:
            module = node.module or ""
            for name in node.names:
                # Simplified - would need proper resolution
                import_name = f"{module}.{name.name}"
                if import_name in self.function_map:
                    self.imports.append((self.current_function, import_name))
        
        self.generic_visit(node)


def scan_repository(repo_path):
    """Scan a repository for technical debt and return scores and graph."""
    # Find Python files
    python_files = []
    exclude_patterns = ["**/.git/**", "**/venv/**", "**/__pycache__/**", "**/node_modules/**"]
    
    for root, dirs, files in os.walk(repo_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(Path(os.path.join(root, d)).match(pattern) for pattern in exclude_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.py') and not any(Path(file_path).match(pattern) for pattern in exclude_patterns):
                python_files.append(file_path)
    
    # Analyze files
    file_scores = {}
    for file_path in python_files:
        try:
            # Count lines of code
            with open(file_path, 'r') as f:
                loc = sum(1 for _ in f)
            
            # Analyze for debt
            debt_items = analyze_file(file_path)
            
            # Score the file
            file_score = scorer.score_file(file_path, debt_items, loc)
            file_scores[file_path] = file_score
        
        except Exception as e:
            # Log the error and continue
            print(f"Error analyzing {file_path}: {str(e)}")
    
    # Score the repository
    repo_score = scorer.score_repo(repo_path, file_scores)
    
    # Build code graph
    graph_builder = CodeGraphBuilder(repo_path)
    graph_builder.build_graph()
    graph_json = graph_builder.export_cytoscape_json()
    
    return repo_score, graph_json


# Initialize core components
scorer = DebtScorer()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)