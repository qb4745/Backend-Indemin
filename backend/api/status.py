import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

status_bp = Blueprint('status_bp', __name__)

@status_bp.route('/status', methods=['GET'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500'], headers=['Content-Type', 'Authorization'])
def get_status():
    try:
        url = f"{SUPABASE_URL}tarea_estado"
        print(f"Making GET request to {url}")

        response = requests.get(url, headers=HEADERS)
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code != 200:
            return jsonify({'error': 'No se pudieron obtener los estados de tarea'}), 500
        
        estados_tarea = response.json()
        return jsonify(estados_tarea), 200

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500

