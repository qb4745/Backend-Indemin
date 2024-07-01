import requests
import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

logging.basicConfig(level=logging.DEBUG)

update_status_bp = Blueprint('update_status_bp', __name__)

@update_status_bp.route('/update_task_status/<int:task_id>', methods=['PATCH'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'])
def update_status(task_id):
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'El campo "status" es requerido'}), 400
        
        # Construir la URL para actualizar el estado de la tarea en Supabase
        url = f"{SUPABASE_URL}tarea_estado?id_tarea=eq.{task_id}"
        
        # Payload con los datos a actualizar (solo el campo 'status' en este caso)
        payload = {
            "status": new_status
        }

        # Realizar la solicitud PATCH a Supabase
        response = requests.patch(url, json=payload, headers=HEADERS)

        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            return jsonify({'message': f'Estado de la tarea {task_id} actualizado correctamente a {new_status}'}), 200
        else:
            return jsonify({'error': f'Error al actualizar el estado de la tarea {task_id}'}), response.status_code

    except Exception as e:
        logging.exception("Exception occurred")
        return jsonify({'error': 'Error en el servidor'}), 500

