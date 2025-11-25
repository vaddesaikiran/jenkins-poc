import json
from flask import jsonify  # Flask is auto-included in Cloud Functions runtime

def multiply(a, b):
    """Core logic: Multiplies two numbers."""
    return a * b

def multiply_http(request):
    """HTTP entry point: Expects JSON payload like {'a': 5, 'b': 10}."""
    try:
        # Parse request data (e.g., from POST body)
        request_json = request.get_json(silent=True)
        if not request_json or 'a' not in request_json or 'b' not in request_json:
            return jsonify({'error': 'Missing "a" or "b" in JSON payload'}), 400
        
        a = float(request_json['a'])
        b = float(request_json['b'])
        result = multiply(a, b)
        
        return jsonify({
            'result': result,
            'inputs': {'a': a, 'b': b}
        }), 200
    
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400

# For local testing (unchanged)
if __name__ == "__main__":
    print("Result:", multiply(5, 10))