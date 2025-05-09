#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified WSGI application that serves a static HTML page with the graph.
Designed to work with Passenger WSGI on SiteGround.
"""

import os
from flask import Flask, send_from_directory

# Create Flask app
app = Flask(__name__)

# Path to the static directory
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/graph')
def graph():
    """Serve the graph page."""
    return send_from_directory(STATIC_DIR, 'graph.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory(STATIC_DIR, path)

# WSGI application
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)