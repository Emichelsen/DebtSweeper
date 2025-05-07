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

from flask import Flask, request, render_template, jsonify, send_file, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Create a simpler version for deployment
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Add HTML templates as strings
TEMPLATES = {
    'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, 
  user-scalable=no">
    <title>DebtSweeper Dashboard</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
        /* DebtSweeper High-Tech Theme */
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
            rgba(61, 220, 132, 0.03) 2px,
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
    </style>
</head>
<body class="overflow-x-hidden">
    <div class="hero text-center">
      <div style="max-width: 100%; overflow: hidden; padding: 0 10px;">
          <h1 style="font-size: calc(1.5rem + 1.5vw); font-weight: 700; letter-spacing: 1px; position: relative; color: 
  #FFFFFF; text-shadow: 0 0 4px rgba(255, 255, 255, 0.24); word-break: break-word; white-space: normal;">
              <span style="color: #3DDC84; text-shadow: 0 0 8px rgba(61, 220, 132, 0.41);">&lt;</span>DebtSweeper<span 
  style="color: #3DDC84; text-shadow: 0 0 8px rgba(61, 220, 132, 0.41);">&gt;</span>
          </h1>
          <p class="lead">Automated technical debt detection and remediation</p>
      </div>
    </div
  

    <div class="container py-4">
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

        <div class="row">
            <div class="col-12">
                <h2>How It Works</h2>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">1</div>
                    <div class="ms-3">Upload your Python codebase as a zip file.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">2</div>
                    <div class="ms-3">DebtSweeper analyzes code structure and patterns to identify technical debt.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">3</div>
                    <div class="ms-3">Review debt items and their severity scores in an interactive dashboard.</div>
                </div>
                <div class="d-flex align-items-center mb-3">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">4</div>
                    <div class="ms-3">Select debt items to fix and get AI-generated refactoring suggestions.</div>
                </div>
                <div class="d-flex align-items-center">
                    <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">5</div>
                    <div class="ms-3">Apply patches to your codebase manually or through GitHub PRs.</div>
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
</body>
</html>''',
    'scan.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, 
  user-scalable=no">
    <title>Repository Scan - DebtSweeper</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
        /* DebtSweeper High-Tech Theme */
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
            rgba(61, 220, 132, 0.03) 2px,
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
        
        .progress-container {
            display: none;
        }
        .results-container {
            display: none;
        }
    </style>
</head>
<body class="overflow-x-hidden">
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
                <div class="card-header text-white">
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
                <div class="card-header text-white">
                    <h5 class="mb-0">Debt By Type</h5>
                </div>
                <div class="card-body">
                    <div id="debt-by-type" class="row">
                        <!-- Will be populated by JavaScript -->
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header text-white">
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
    
    <!-- Page-specific JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('scan-form');
            const uploadContainer = document.querySelector('.upload-container');
            const progressContainer = document.querySelector('.progress-container');
            const resultsContainer = document.querySelector('.results-container');
            
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
        });
    </script>
</body>
</html>''',
    'file.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, 
  user-scalable=no">
    <title>{{ file_path }} - DebtSweeper</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
    <!-- Prism.js for syntax highlighting -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/themes/prism-tomorrow.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <style>
        /* DebtSweeper High-Tech Theme */
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
            rgba(61, 220, 132, 0.03) 2px,
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

        /* iPhone-specific fixes */
  @media only screen and (max-width: 428px) {
    /* Container padding */
    .container {
      padding-left: 10px !important;
      padding-right: 10px !important;
      width: 100% !important;
      max-width: 100% !important;
    }

    /* Fix for oversized elements */
    .row {
      margin-left: -5px !important;
      margin-right: -5px !important;
    }

    .col-md-4, .col-md-6, .col-md-8, .col-md-12 {
      padding-left: 5px !important;
      padding-right: 5px !important;
    }

    /* Text adjustments */
    .logo-text {
      font-size: 2rem !important;
      word-break: keep-all;
    }

    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.5rem !important; }
    h5 { font-size: 1.1rem !important; }
    p { font-size: 0.9rem !important; }

    /* Card fixes */
    .card {
      overflow: hidden;
      width: 100% !important;
    }

    /* Force proper width */
    body, html {
      width: 100% !important;
      overflow-x: hidden !important;
    }

    /* Prevent horizontal scrolling */
    .overflow-x-hidden {
      overflow-x: hidden !important;
    }

    /* Better button sizing for touch */
    .btn {
      display: block !important;
      width: 100% !important;
      margin-bottom: 10px !important;
    }
  }

  /* Fix iOS Safari 100vh issue */
  @supports (-webkit-touch-callout: none) {
    .min-vh-100 {
      min-height: -webkit-fill-available;
    }
  }
    </style>
</head>
<body class="overflow-x-hidden">
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
            <div class="card-header text-white">
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
            <div class="card-header text-white">
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
</html>'''
}

# Mock classes for demonstration purposes
class DebtScorer:
    def score_file(self, file_path, debt_items, loc):
        class FileScore:
            def __init__(self):
                self.debt_score = 0.3
        return FileScore()
        
    def score_repo(self, repo_path, file_scores):
        class RepoScore:
            def __init__(self):
                self.debt_score = 0.4
                self.total_debt_items = 15
                self.total_loc = 1200
                self.items_by_type = {
                    'long_function': 5,
                    'high_complexity': 7,
                    'code_duplication': 3
                }
        return RepoScore()

# Initialize core components
scorer = DebtScorer()

@app.route('/')
def index():
    """Render the dashboard homepage."""
    return TEMPLATES['index.html']

@app.route('/static/style.css')
def serve_static_css():
    return TEMPLATES['style.css'] if 'style.css' in TEMPLATES else ''

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
    return TEMPLATES['scan.html']

@app.route('/file/<path:file_path>')
def view_file(file_path):
    """View details for a specific file."""
    # For demo purposes, provide mock data
    debt_items = [
        {
            'debt_type': 'long_function',
            'severity': 0.7,
            'message': 'Function is too long (50 lines)',
            'line_start': 10,
            'line_end': 60
        },
        {
            'debt_type': 'high_complexity',
            'severity': 0.8,
            'message': 'Function has high cyclomatic complexity (15)',
            'line_start': 25,
            'line_end': 40
        }
    ]
    
    # Score the file
    file_score = scorer.score_file(file_path, debt_items, 100)
    
    # Render template with file details and replace template variables
    template = TEMPLATES['file.html']
    template = template.replace('{{ file_path }}', file_path)
    template = template.replace('{{ file_path.split(\'/\')[-1] }}', file_path.split('/')[-1])
    template = template.replace('{{ "%.2f"|format(file_score.debt_score) }}', '0.30')
    template = template.replace('{{ debt_items|length }}', str(len(debt_items)))
    template = template.replace('{{ loc }}', '100')
    
    # Replace loop for debt items
    debt_items_html = ''
    for i, item in enumerate(debt_items):
        debt_item_html = f'''
        <div class="list-group-item debt-item" data-debt-id="{i}">
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">{item['debt_type'].replace('_', ' ').title()}</h5>
                <span class="badge bg-danger">Severity: {item['severity']:.2f}</span>
            </div>
            <p class="mb-1">{item['message']}</p>
            <small>Lines {item['line_start']}-{item['line_end']}</small>
        </div>
        '''
        debt_items_html += debt_item_html
    
    template = template.replace('{% for item in debt_items %}', '')
    template = template.replace('{% endfor %}', '')
    template = template.replace('<div class="list-group-item debt-item" data-debt-id="{{ loop.index0 }}">...</div>', debt_items_html)
    
    # Replace conditional logic
    if debt_items:
        template = template.replace('{% if debt_items %}', '')
        template = template.replace('{% else %}', '<!--')
        template = template.replace('{% endif %}', '-->')
    else:
        template = template.replace('{% if debt_items %}', '<!--')
        template = template.replace('{% else %}', '-->')
        template = template.replace('{% endif %}', '')
    
    # Replace file content
    template = template.replace('{{ file_content|default(\'File content not available\') }}', 'def example_function():\n    # This is a sample function\n    print("Hello World")\n    return True')
    
    return template

@app.route('/suggest/<path:file_path>', methods=['POST'])
def suggest_fixes(file_path):
    """Generate fix suggestions for a file."""
    # For demo purposes, just return a success message
    return jsonify({
        'message': f'Generated fixes for selected debt items in {file_path}',
        'patch_url': url_for('download_patch', file_path=file_path)
    })

@app.route('/patch/<path:file_path>')
def download_patch(file_path):
    """Download a patch file for fixes."""
    # Simple mockup patch
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

if __name__ == '__main__':
    # Use port 10000 for render.com
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
