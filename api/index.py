import os
import sys
from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import your Flask app
from app import create_app

# Create the Flask app instance
flask_app = create_app()

# Enable CORS for all routes
CORS(flask_app)

def handler(request):
    """Vercel serverless function handler"""
    # Handle OPTIONS requests for CORS
    if request.method == 'OPTIONS':
        response = make_response('')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        # Create a test request context
        with flask_app.test_request_context(
            path=request.path,
            method=request.method,
            headers=request.headers,
            data=request.get_data(),
            query_string=request.query
        ):
            # Get the response from the Flask app
            response = flask_app.full_dispatch_request()
            
            # Convert Flask response to Vercel response format
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        # Handle errors gracefully
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': jsonify({
                'error': str(e),
                'status': 'error',
                'message': 'Internal server error'
            })
        }
