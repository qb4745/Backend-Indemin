import requests
import logging
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

logging.basicConfig(level=logging.DEBUG)

edit_checklist_bp = Blueprint('edit_checklist_bp', __name__)

@edit_checklist_bp.route('/edit_checklist/<int:id>', methods=['PATCH'])
@cross_origin(origins='http://localhost:8100')
def edit_checklist(id):
    try:
        data = request.json
        logging.debug(f"Received data: {data}")

        nombre = data.get('nombre')
        id_tipo_maquina = data.get('id_tipo_maquina')
        componentes = data.get('componentes')

        if not (nombre or id_tipo_maquina or componentes):
            return jsonify({'error': 'No se proporcionaron datos para actualizar'}), 400

        # Actualizar checklist si hay datos relevantes
        if nombre or id_tipo_maquina:
            checklist_data = {
                'id_checklist': id,
                'nombre': nombre,
                'id_tipo_maquina': id_tipo_maquina
            }
            update_checklist(checklist_data)

        # Actualizar componentes y tareas asociadas
        if componentes:
            for componente in componentes:
                update_componente(componente)

        return jsonify({'message': 'Checklist actualizado exitosamente'}), 200

    except Exception as e:
        logging.exception("Exception occurred")
        return jsonify({'error': 'Error en el servidor'}), 500


def update_tarea(tarea_data):
    tarea_id = tarea_data['id_tarea']
    url = f"{SUPABASE_URL}tareas?id_tarea=eq.{tarea_id}"
    headers = HEADERS
    try:
        response = requests.patch(url, json=tarea_data, headers=headers)
        response.raise_for_status()
        if response.status_code == 204:
            logging.debug(f"Tarea actualizada exitosamente: No se devolvieron contenidos.")
        else:
            logging.debug(f"Tarea actualizada exitosamente.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error actualizando tarea: {e}")
        raise


def update_checklist(checklist_data):
    checklist_id = checklist_data['id_checklist']
    url = f"{SUPABASE_URL}checklists?id_checklist=eq.{checklist_id}"
    headers = HEADERS
    try:
        response = requests.patch(url, json=checklist_data, headers=headers)
        response.raise_for_status()
        if response.status_code == 204:
            logging.debug(f"Checklist actualizado exitosamente: No se devolvieron contenidos.")
        else:
            logging.debug(f"Checklist actualizado exitosamente.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error actualizando checklist: {e}")
        raise


def update_componente(componente_data):
    componente_id = componente_data['id_componente']
    url = f"{SUPABASE_URL}componentes?id_componente=eq.{componente_id}"
    headers = HEADERS
    try:
        response = requests.patch(url, json={'nombre': componente_data['nombre']}, headers=headers)
        response.raise_for_status()
        if response.status_code == 204:
            logging.debug(f"Componente actualizado exitosamente: No se devolvieron contenidos.")
        else:
            logging.debug(f"Componente actualizado exitosamente.")
        
        # Actualizar tareas asociadas al componente
        tasks = componente_data.get('tasks', [])
        for task in tasks:
            update_tarea(task)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error actualizando componente: {e}")
        raise

