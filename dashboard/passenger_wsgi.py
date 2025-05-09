#!/usr/bin/python
"""
Absolute minimal passenger_wsgi.py file.
"""

def application(environ, start_response):
    """WSGI application function."""
    status = '200 OK'
    output = b'Hello, World! If you can see this, passenger_wsgi.py is working.'
    
    response_headers = [('Content-type', 'text/plain'),
                       ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    
    return [output]