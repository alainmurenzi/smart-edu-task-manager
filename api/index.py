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
        # Set up the request context properly
        with flask_app.request_context(request):
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
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error: {error_msg}")  # Log to Vercel logs
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': f'''
            <!DOCTYPE html>
            <html>
            <head><title>Server Error</title></head>
            <body>
                <h1>500 - Internal Server Error</h1>
                <p>{str(e)}</p>
                <details>
                    <summary>Traceback</summary>
                    <pre>{traceback.format_exc()}</pre>
                </details>
            </body>
            </html>
            '''
        }
