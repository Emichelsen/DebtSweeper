#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Super simple Flask app that just serves static pages.
Uses a completely static graph.html that will definitely work.
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page with link to static graph."""
    return render_template('static_graph.html')

@app.route('/scan')
def scan():
    """Placeholder scan page."""
    return render_template('scan.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)