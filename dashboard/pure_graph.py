#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    """Super-simplified implementation with just Cytoscape and a graph."""
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pure Graph</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background: #000; }
        #cy { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; }
        #title { position: absolute; top: 10px; left: 10px; color: white; font-family: Arial; z-index: 10; }
        #log { position: absolute; bottom: 10px; left: 10px; color: lime; font-family: monospace; z-index: 10; 
               background: rgba(0,0,0,0.7); padding: 10px; max-height: 200px; overflow-y: auto; width: 500px; }
    </style>
</head>
<body>
    <h1 id="title">DebtSweeper Knowledge Graph</h1>
    <div id="cy"></div>
    <div id="log">Loading...</div>

    <script>
    // Simple logging function
    function log(msg) {
        const logEl = document.getElementById('log');
        logEl.innerHTML += "<br>" + new Date().toLocaleTimeString() + ": " + msg;
        console.log(msg);
    }

    // Wait for DOM to load
    document.addEventListener('DOMContentLoaded', function() {
        log("DOM loaded");
        
        // Hard-coded demo data - extremely simplified
        const elements = [
            // Nodes
            { data: { id: 'a', label: 'Module A', size: 40, color: '#3DDC84' } },
            { data: { id: 'b', label: 'Class B', size: 30, color: '#FFC107' } },
            { data: { id: 'c', label: 'Function C', size: 20, color: '#e84118' } },
            { data: { id: 'd', label: 'Method D', size: 25, color: '#3DDC84' } },
            { data: { id: 'e', label: 'Module E', size: 35, color: '#FFC107' } },
            
            // Edges
            { data: { id: 'ab', source: 'a', target: 'b' } },
            { data: { id: 'ac', source: 'a', target: 'c' } },
            { data: { id: 'bd', source: 'b', target: 'd' } },
            { data: { id: 'cd', source: 'c', target: 'd' } },
            { data: { id: 'de', source: 'd', target: 'e' } }
        ];
        
        log("Data prepared: " + elements.length + " elements");
        
        try {
            // Initialize Cytoscape
            log("Initializing graph...");
            const cy = cytoscape({
                container: document.getElementById('cy'),
                elements: elements,
                style: [
                    {
                        selector: 'node',
                        style: {
                            'label': 'data(label)',
                            'background-color': 'data(color)',
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': '#000',
                            'font-size': '16px'
                        }
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 3,
                            'line-color': '#aaa',
                            'curve-style': 'bezier',
                            'target-arrow-shape': 'triangle',
                            'target-arrow-color': '#aaa'
                        }
                    }
                ]
            });
            
            log("Graph initialized");
            
            // Apply a simple layout
            cy.layout({
                name: 'circle',
                padding: 30
            }).run();
            
            log("Layout complete");
            
            // Add basic click handler
            cy.on('tap', 'node', function(evt) {
                const node = evt.target;
                log("Clicked: " + node.data('label'));
            });
            
            log("Graph ready!");
        } catch (error) {
            log("ERROR: " + error.message);
            console.error(error);
        }
    });
    </script>
</body>
</html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)