#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask dashboard for DebtSweeper.

Provides a web interface for visualizing debt scores and managing fixes.
"""

import os
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from debtsweeper.analyzer import analyze_file
from debtsweeper.scorer import DebtScorer, FileScore, RepoScore
from debtsweeper.orchestrator import LLMOrchestrator, RefactorSuggestion
from debtsweeper.patches import PatchGenerator


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Initialize core components
scorer = DebtScorer()


@app.route('/')
def index():
    """Render the dashboard homepage."""
    return render_template('index.html')


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
        repo_score = scan_repository(extract_path)
        
        # Return results as JSON
        return jsonify({
            'repo_score': repo_score.debt_score,
            'total_debt_items': repo_score.total_debt_items,
            'total_loc': repo_score.total_loc,
            'items_by_type': repo_score.items_by_type,
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
    
    # Render template with file details
    return render_template(
        'file.html',
        file_path=file_path,
        file_score=file_score,
        debt_items=debt_items,
        loc=loc
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


def scan_repository(repo_path):
    """Scan a repository for technical debt and return scores."""
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
    
    return repo_score


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
