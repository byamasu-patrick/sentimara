"""
This module defines a decorator function 'token_required' for Flask routes to enforce JWT (JSON Web Token) authentication. The decorator checks for a valid JWT in the request headers and decodes it to verify the user's authentication status. If the token is missing or invalid, it returns an appropriate response. This ensures that only requests with valid tokens can access certain routes in the Flask application.
"""

from functools import wraps

import jwt
from flask import jsonify, request

from app import SECRET_KEY


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # get the token and verify it if the token is valid
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        else:
            return jsonify({'success': False, 'result': None, 'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # printing the decoded data from the token
            print(str(data))

        except Exception as e:
            # print the error message for debugging
            print(str(e))
            return jsonify({'success': False, 'result': None, 'error': 'Invalid token'}), 403
        return f(*args, **kwargs)

    return decorated
