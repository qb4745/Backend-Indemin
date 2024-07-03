import requests
import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

logging.basicConfig(level=logging.DEBUG)

comentario_tarea_bp = Blueprint('comentario_tarea_bp', __name__)

@comentario_tarea_bp.route('/save_task_comment/<int:task_id>', methods=['PATCH'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'])
def comentario_tarea(task_id):
    try:
        data = request.get_json()
        new_comment = data.get('comment')

        if not new_comment:
            return jsonify({'error': 'El campo "comment" es requerido'}), 400
        
        # Construir la URL para actualizar el comentario de la tarea en Supabase
        url = f"{SUPABASE_URL}tarea_estado?id_tarea=eq.{task_id}"
        
        # Payload con el comentario a actualizar
        payload = {
            "comment": new_comment
        }

        # Realizar la solicitud PATCH a Supabase
        response = requests.patch(url, json=payload, headers=HEADERS)

        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            return jsonify({'message': f'Comentario de la tarea {task_id} actualizado correctamente'}), 200
        else:
            return jsonify({'error': f'Error al actualizar el comentario de la tarea {task_id}'}), response.status_code

    except Exception as e:
        logging.exception("Exception occurred")
        return jsonify({'error': 'Error en el servidor'}), 500
