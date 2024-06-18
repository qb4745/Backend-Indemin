import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

usuario_bp = Blueprint('usuario_bp', __name__)

@usuario_bp.route('/usuario', methods=['POST'])
@cross_origin(origins='http://localhost:8100', headers=['Content-Type', 'Authorization'])
def usuario():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    response = requests.get(SUPABASE_URL + 'usuario?email=eq.' + email + '&password=eq.' + password, headers=HEADERS)
    if response.status_code == 200:
        user_data = response.json()
        if len(user_data) == 1:
            user = user_data[0]
            return jsonify({
                'message': 'Usuario logueado correctamente',
                'user': {
                    'id_usuario': user['id_usuario'],
                    'email': user['email'],
                    'tipo_usuario': user.get('tipo_usuario', 'user')  # Asegúrate de manejar el caso cuando 'tipo_usuario' sea NULL
                }
            }), 200
        else:
            return jsonify({'message': 'Credenciales inválidas'}), 401
    else:    
        return jsonify({'message': 'Error en el servidor'}), 500
