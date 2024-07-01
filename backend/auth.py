from functools import wraps
from flask import request, jsonify, g
import jwt
from config import JWT_SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token es requerido!'}), 401

        try:
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            g.current_user = data.get('id_usuario')  # Extraer el campo correcto del token
            if not g.current_user:
                raise jwt.InvalidTokenError('User ID not found in token')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token ha expirado!'}), 401
        except jwt.InvalidTokenError as e:
            print(f'Error al decodificar el token: {str(e)}')
            return jsonify({'message': 'Token es inválido!'}), 401

        return f(*args, **kwargs)

    return decorated
