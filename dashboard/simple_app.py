import os
from flask import Flask, render_template, send_from_directory, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Dashboard homepage with Debt Knowledge Graph."""
    return render_template('index.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    """Handle repository scanning and display results."""
    if request.method == 'POST':
        # For demo purposes, just return mock data
        return jsonify({
            'repo_score': 0.4,
            'total_debt_items': 15,
            'total_loc': 1200,
            'items_by_type': {
                'long_function': 5,
                'high_complexity': 7,
                'code_duplication': 3
            }
        })

    # GET request - show upload form
    return render_template('scan.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Use port provided by environment variable or default to 5051
    port = int(os.environ.get("PORT", 5051))
    app.run(host='0.0.0.0', port=port, debug=True)