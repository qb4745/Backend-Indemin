import requests
import logging
from flask import Blueprint, jsonify, request, g
from flask_cors import CORS, cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required  # Importar el middleware token_required

logging.basicConfig(level=logging.DEBUG)

edit_checklist_bp = Blueprint('edit_checklist_bp', __name__)
CORS(edit_checklist_bp, origins=['http://localhost:8100', 'http://127.0.0.1:5500'], supports_credentials=True)

@edit_checklist_bp.route('/edit_checklist/<int:id>', methods=['PATCH', 'OPTIONS'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'], headers=['Content-Type', 'Authorization'])
@token_required  # Añadir el decorador token_required
def edit_checklist(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 204  # Responder sin contenido para solicitudes OPTIONS, 'https://alvarofenero.github.io'

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
            checklist_data = {}
            if nombre:
                checklist_data['nombre'] = nombre
            if id_tipo_maquina:
                checklist_data['id_tipo_maquina'] = id_tipo_maquina

            update_checklist(id, checklist_data)

        # Obtener componentes existentes para este checklist
        existing_componentes_response = requests.get(f"{SUPABASE_URL}componentes?id_checklist=eq.{id}", headers=HEADERS)
        existing_componentes_response.raise_for_status()
        existing_componentes = existing_componentes_response.json()

        # Crear un diccionario de componentes existentes para fácil acceso
        existing_componentes_dict = {componente['id_componente']: componente for componente in existing_componentes}

        # Actualizar componentes y tareas asociadas
        if componentes:
            for componente in componentes:
                if componente['id_componente'] == 0:
                    create_componente(id, componente)
                else:
                    update_componente(componente)
                    if componente['id_componente'] in existing_componentes_dict:
                        del existing_componentes_dict[componente['id_componente']]

        # Eliminar componentes que ya no están en la lista
        for componente_id in existing_componentes_dict:
            delete_componente(componente_id)

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
        logging.debug(f"Tarea actualizada exitosamente.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error actualizando tarea: {e}")
        raise

def create_tarea(tarea_data):
    url = f"{SUPABASE_URL}tareas"
    headers = HEADERS
    if 'id_componente' not in tarea_data or tarea_data['id_componente'] == 0:
        raise ValueError("id_componente is missing or invalid in tarea_data")
    if 'frecuencia' not in tarea_data:
        tarea_data['frecuencia'] = 'diario'
    tarea_data.pop('id_tarea', None)

    logging.debug(f"Datos de la tarea enviados: {tarea_data}")
    try:
        response = requests.post(url, json=tarea_data, headers=headers)
        response.raise_for_status()
        logging.debug(f"Respuesta de crear tarea: {response.status_code}, {response.text}")
        if response.status_code == 201 and response.text.strip():
            logging.debug(f"Tarea creada exitosamente: {response.json()}")
        else:
            logging.debug(f"Tarea creada exitosamente con respuesta vacía.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creando tarea: {e}")
        raise

def delete_tarea(task_id):
    url = f"{SUPABASE_URL}tareas?id_tarea=eq.{task_id}"
    headers = HEADERS
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        logging.debug(f"Tarea eliminada exitosamente: {task_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error eliminando tarea: {e}")
        raise

def update_checklist(checklist_id, checklist_data):
    url = f"{SUPABASE_URL}checklists?id_checklist=eq.{checklist_id}"
    headers = HEADERS
    try:
        response = requests.patch(url, json=checklist_data, headers=headers)
        response.raise_for_status()
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
        logging.debug(f"Componente actualizado exitosamente.")
        
        existing_tasks_response = requests.get(f"{SUPABASE_URL}tareas?id_componente=eq.{componente_id}", headers=headers)
        existing_tasks_response.raise_for_status()
        existing_tasks = existing_tasks_response.json()

        existing_tasks_dict = {task['id_tarea']: task for task in existing_tasks}

        for task in componente_data.get('tasks', []):
            if task['id_tarea'] == 0:
                task['id_componente'] = componente_id
                create_tarea(task)
            else:
                if task['id_tarea'] in existing_tasks_dict:
                    update_tarea(task)
                    del existing_tasks_dict[task['id_tarea']]
                else:
                    task['id_tarea'] = componente_id
                    create_tarea(task)

        for task_id in existing_tasks_dict:
            delete_tarea(task_id)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error actualizando componente: {e}")
        raise

def create_componente(checklist_id, componente_data):
    componente_data['id_checklist'] = checklist_id
    url = f"{SUPABASE_URL}componentes"
    headers = HEADERS

    new_componente_data = {
        'nombre': componente_data['nombre'],
        'id_checklist': checklist_id
    }

    try:
        response = requests.post(url, json=new_componente_data, headers=headers)
        response.raise_for_status()
        logging.debug(f"Respuesta de crear componente: {response.status_code}, {response.text}")
        if response.status_code == 201 and response.text.strip():
            logging.debug(f"Componente creado exitosamente: {response.json()}")
            componente_id = response.json()['id_componente']
        else:
            logging.debug(f"Componente creado exitosamente con respuesta vacía.")
            componente_id = obtener_id_componente(componente_data['nombre'], checklist_id)

        for task in componente_data.get('tasks', []):
            task['id_componente'] = componente_id
            create_tarea(task)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error creando componente: {e}")
        raise

def obtener_id_componente(nombre, checklist_id):
    url = f"{SUPABASE_URL}componentes?nombre=eq.{nombre}&id_checklist=eq.{checklist_id}"
    headers = HEADERS
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        componentes = response.json()
        if componentes:
            return componentes[0]['id_componente']
        else:
            raise ValueError("No se pudo obtener el ID del componente creado")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obteniendo el ID del componente: {e}")
        raise

def delete_componente(componente_id):
    url_tareas = f"{SUPABASE_URL}tareas?id_componente=eq.{componente_id}"
    headers = HEADERS
    try:
        # Primero, obtener todas las tareas asociadas a este componente
        response_tareas = requests.get(url_tareas, headers=headers)
        response_tareas.raise_for_status()
        tareas = response_tareas.json()

        # Eliminar todas las tareas asociadas
        for tarea in tareas:
            delete_tarea(tarea['id_tarea'])
        
        # Ahora, eliminar el componente
        url_componente = f"{SUPABASE_URL}componentes?id_componente=eq.{componente_id}"
        response_componente = requests.delete(url_componente, headers=headers)
        response_componente.raise_for_status()
        logging.debug(f"Componente eliminado exitosamente: {componente_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error eliminando componente: {e}")
        raise
