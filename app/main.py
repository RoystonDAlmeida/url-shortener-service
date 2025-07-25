import time
from flask import Flask, jsonify, request, redirect, url_for, abort
from .models import url_store, store_lock
from .utils import generate_short_code, is_valid_url

app = Flask(__name__)

@app.route('/')
def health_check():
    """
    @Description:
        Health check endpoint for the URL Shortener API.
        Returns a JSON response indicating the service is running and healthy.
    @Returns:
        JSON: {"status": "healthy", "service": "URL Shortener API"}
    """

    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    """
    @Description:
        API health check endpoint for monitoring.
        Returns a JSON response indicating the API is running.
    @Returns:
        JSON: {"status": "ok", "message": "URL Shortener API is running"}
    """
    
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/debug/mappings')
def debug_mappings():
    """
    @Description:
        Endpoint for debugging URL mappings.     Returns a JSON response containing the current URL mappings.
    @Returns:
        JSON: Current URL mappings.
    """
    
    with store_lock:
        return jsonify(url_store)
    
@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """
    @Description:
        Shorten a valid long URL by generating a unique short code and storing the mapping.
        Validates input, handles errors, and returns the short code and short URL.
    @Returns:
        JSON: {"short_code": str, "short_url": str} on success, or error JSON on failure.
    """

    if not request.is_json:
        # If the request is not JSON, return a 415 Unsupported Media Type
        return jsonify({"error": "Content-Type must be application/json"}), 415

    # Parse the incoming JSON request body(silent = True as Flask should not raise error if request data is empty)
    data = request.get_json(silent=True)

    if not data:
        # If the request body is empty, return a 400 Bad Request
        return jsonify({"error": "'url' parameter is required in request body"}), 400
    
    if 'url' not in data:
        return jsonify({"error": "'url' parameter is required in request body"}), 400

    long_url = data['url']
    if not is_valid_url(long_url):
        # Validate the URL using is_valid_url custom validator
        return jsonify({"error": "Invalid URL"}), 400

    # Attempt to generate a unique short code up to 10 times
    for _ in range(10):
        code = generate_short_code()  # Generate a random 6-character code
        with store_lock:  # Ensure thread-safe access to url_store
            if code not in url_store:  # Check if the code is unique
                url_store[code] = {
                    'url': long_url,           
                    'clicks': 0,               
                    'created_at': time.strftime('%Y-%m-%dT%H:%M:%S')
                }
                break  # Exit loop once a unique code is stored
    
    else:
        # If unable to generate a unique code after 10 tries, return error
        return jsonify({"error": "Could not generate unique code"}), 500
    
    # Build the full short URL and return JSON response
    short_url = request.host_url.rstrip('/') + '/' + code
    return jsonify({"short_code": code, "short_url": short_url})

@app.route('/api/<short_code>')
def redirect_short_url(short_code):
    """
    @Description:
        Redirects to the original long URL associated with the short code.
    @Args:
        short_code (str): The short code to redirect to the original long URL.
    @Returns:
        Redirect: Redirects to the original long URL.
        JSON: {"error": "Not found"} on failure.
    """

    with store_lock:
        entry = url_store.get(short_code)   # Get the long URL associated with the short code
        if not entry:
            # Short URL does not exist
            return jsonify({"error": "Short code not found"}), 404
        
        # Increment the click count
        entry['clicks'] += 1
        url = entry['url']
    
    # Redirect to "url"
    return redirect(url, code=302)

@app.route('/api/stats/<short_code>')
def stats(short_code):
    """
    @Description:
        Retrieve statistics for a specific short code.
    @Args:
        short_code (str): The short code to retrieve statistics for.
    @Returns:
        JSON: {"url": str, "clicks": int, "created_at": str} on success, or error JSON on failure.
    """

    with store_lock:
        entry = url_store.get(short_code)
        if not entry:
            return jsonify({"error": "Short code not found"}), 404
        
        return jsonify({
            "url": entry['url'],
            "clicks": entry['clicks'],
            "created_at": entry['created_at']
        })

@app.errorhandler(415)
def handle_415(e):
    """
    @Description: 
        Return a JSON error response for 415 Unsupported Media Type errors.
        Ensures clients always receive a JSON error instead of the default HTML page
        when Content-Type is not application/json.
    """

    return jsonify({"error": "Content-Type must be application/json"}), 415

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)   # Enable reloading on file changes