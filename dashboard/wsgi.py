"""
WSGI entry point for Render.com
"""
from render_app import app

# This is the WSGI entry point that Render.com will look for
application = app