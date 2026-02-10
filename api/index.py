import os
import sys
import traceback

print("Starting Vercel function...")

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"Python path: {sys.path}")
print(f"Current dir: {current_dir}")
print(f"Parent dir: {parent_dir}")

try:
    from flask import Flask, request, jsonify, make_response, send_from_directory
    from flask_cors import CORS
    print("Flask imports successful")
except Exception as e:
    print(f"Flask import error: {e}")
    traceback.print_exc()
    raise

try:
    # Import your Flask app
    from app import create_app
    print("create_app import successful")
except Exception as e:
    print(f"create_app import error: {e}")
    traceback.print_exc()
    raise

try:
    # Create the Flask app instance
    flask_app = create_app()
    print("Flask app created successfully")
except Exception as e:
    print(f"create_app() error: {e}")
    traceback.print_exc()
    raise

# Enable CORS for all routes
CORS(flask_app)

def handler(request):
    """Vercel serverless function handler"""
    print(f"Handling request: {request.method} {request.path}")
    
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
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Error: {error_msg}")
        
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
