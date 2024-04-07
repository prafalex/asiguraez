import jwt
from functools import wraps
from flask import request, jsonify, current_app


def jwt_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None
        if 'access-token' in request.headers:
            token = request.headers.get('access-token')
        if not token:
            return jsonify({'message' : 'Token is not in the header!'}), 401
        try:
            secret_key = current_app.config.get('SECRET_KEY')
            payload = jwt.decode(token,secret_key , algorithms=['HS256'])
            if(payload.get('role')=='admin'):
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Access not granted'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
    return wrapper
