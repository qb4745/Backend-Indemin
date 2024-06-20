import requests
import jwt
import datetime
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS, JWT_SECRET_KEY

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/usuario', methods=['POST'])

@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500'], headers=['Content-Type', 'Authorization'])
def usuario():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email y contraseña son requeridos'}), 400

        # Supongamos que las contraseñas en la base de datos no están hasheadas
        response = requests.get(SUPABASE_URL + 'usuario?email=eq.' + email + '&password=eq.' + password, headers=HEADERS)
        if response.status_code == 200:
            user_data = response.json()
            if len(user_data) == 1:
                user = user_data[0]
                token = jwt.encode({
                    'id_usuario': user['id_usuario'],
                    'email': user['email'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                }, JWT_SECRET_KEY, algorithm='HS256')

                return jsonify({
                    'message': 'Usuario logueado correctamente',
                    'token': token,
                    'user': {
                        'id_usuario': user['id_usuario'],
                        'email': user['email'],
                        'tipo_usuario': user.get('tipo_usuario', 'user')
                    }
                }), 200
            else:
                return jsonify({'message': 'Credenciales inválidas'}), 401
        else:
            print('Error en la respuesta del servidor:', response.text)
            return jsonify({'message': 'Error en el servidor'}), 500

    except Exception as e:
        print('Excepción atrapada:', str(e))
        return jsonify({'message': 'Error en el servidor'}), 500

from functools import wraps

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
            current_user = {
                'id_usuario': data['id_usuario'],
                'email': data['email']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token ha expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token es inválido!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@usuario_bp.route('/protected', methods=['GET'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500'], headers=['Content-Type', 'Authorization'])
@token_required
def protected_route(current_user):
    return jsonify({'message': 'Ruta protegida', 'user': current_user})