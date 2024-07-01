import requests
import json
import datetime
from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required

checklist_bp = Blueprint('checklist_bp', __name__)

@checklist_bp.route('/create_checklist', methods=['POST'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'])
@token_required
def create_checklist():
    try:
        data = request.json
        nombre = data.get('nombre')
        id_tipo_maquina = data.get('id_tipo_maquina')
        codigo_interno = data.get('codigo_interno')
        componentes = data.get('componentes')
        id_usuario = g.current_user  # Obtener el usuario del token
        timestamp = datetime.datetime.now().isoformat()

        if not nombre or not id_tipo_maquina or not codigo_interno:
            return jsonify({'error': 'Faltan datos necesarios'}), 400

        # Obtener la máquina por el código interno
        response = requests.get(SUPABASE_URL + 'maquinas?codigo_interno=eq.' + codigo_interno, headers=HEADERS)
        if response.status_code != 200 or not response.json():
            return jsonify({'error': 'Máquina no encontrada'}), 404

        maquina = response.json()[0]
        id_maquina = maquina['id_maquina']

        # Verificar si la máquina con el ID ya tiene un checklist asignado
        response = requests.get(SUPABASE_URL + 'checklists_maquinas?id_maquina=eq.' + str(id_maquina), headers=HEADERS)
        if response.status_code == 200 and response.json():
            return jsonify({'error': 'La máquina con el código interno especificado ya tiene un checklist asignado'}), 400

        # Crear el checklist con un timestamp para asegurar unicidad
        checklist_data = {
            'nombre': f"{nombre}_{timestamp}",
            'id_tipo_maquina': id_tipo_maquina,
            'id_usuario': id_usuario  # Agregar el usuario aquí
        }
        response = requests.post(SUPABASE_URL + 'checklists', headers=HEADERS, data=json.dumps(checklist_data))
        if response.status_code != 201:
            return jsonify({'error': 'No se pudo crear el checklist'}), 500

        # Manejar posible respuesta vacía
        if not response.text.strip():
            print("Empty response text from checklist creation. Fetching created checklist...")
            # Realizar una solicitud de seguimiento para obtener el checklist recién creado
            response = requests.get(SUPABASE_URL + f'checklists?nombre=eq.{checklist_data["nombre"]}', headers=HEADERS)
            if response.status_code != 200 or not response.json():
                print("Could not fetch the created checklist")
                return jsonify({'error': 'No se pudo obtener el checklist recién creado'}), 500
            checklist = response.json()[0]
        else:
            try:
                checklist = response.json()
            except ValueError:
                print("Error parsing JSON response from checklist creation")
                return jsonify({'error': 'No se pudo obtener la respuesta del checklist creado'}), 500

        checklist_id = checklist.get('id_checklist')
        if not checklist_id:
            return jsonify({'error': 'No se pudo obtener el ID del checklist'}), 500

        # Asignar el checklist a la máquina
        checklist_maquina_data = {
            'id_maquina': id_maquina,
            'id_checklist': checklist_id
        }
        response = requests.post(SUPABASE_URL + 'checklists_maquinas', headers=HEADERS, data=json.dumps(checklist_maquina_data))
        if response.status_code != 201:
            return jsonify({'error': 'No se pudo asignar el checklist a la máquina'}), 500

        # Crear componentes y tareas
        for componente in componentes:
            componente_data = {
                'nombre': componente['nombre'],
                'id_checklist': checklist_id
            }
            response = requests.post(SUPABASE_URL + 'componentes', headers=HEADERS, data=json.dumps(componente_data))
            if response.status_code != 201:
                return jsonify({'error': 'No se pudo crear el componente'}), 500

            # Manejar posible respuesta vacía al crear componente
            if not response.text.strip():
                print("Empty response text from component creation. Fetching created component...")
                response = requests.get(SUPABASE_URL + f'componentes?nombre=eq.{componente_data["nombre"]}', headers=HEADERS)
                if response.status_code != 200 or not response.json():
                    print("Could not fetch the created component")
                    return jsonify({'error': 'No se pudo obtener el componente recién creado'}), 500
                componente_resp = response.json()[0]
            else:
                try:
                    componente_resp = response.json()
                except ValueError:
                    print("Error parsing JSON response from component creation")
                    return jsonify({'error': 'No se pudo obtener la respuesta del componente creado'}), 500

            componente_id = componente_resp.get('id_componente')
            if not componente_id:
                return jsonify({'error': 'No se pudo obtener el ID del componente'}), 500

            for tarea in componente['tasks']:
                tarea_data = {
                    'nombre': tarea['nombre'],
                    'frecuencia': tarea.get('frecuencia', ''),
                    'id_componente': componente_id
                }
                response = requests.post(SUPABASE_URL + 'tareas', headers=HEADERS, data=json.dumps(tarea_data))
                if response.status_code != 201:
                    return jsonify({'error': 'No se pudo crear la tarea'}), 500

                # Manejar posible respuesta vacía al crear tarea
                if not response.text.strip():
                    print("Empty response text from task creation. Fetching created task...")
                    response = requests.get(SUPABASE_URL + f'tareas?nombre=eq.{tarea_data["nombre"]}&id_componente=eq.{componente_id}', headers=HEADERS)
                    if response.status_code != 200 or not response.json():
                        print("Could not fetch the created task")
                        return jsonify({'error': 'No se pudo obtener la tarea recién creada'}), 500
                    tarea_resp = response.json()[0]
                else:
                    try:
                        tarea_resp = response.json()
                    except ValueError:
                        print("Error parsing JSON response from task creation")
                        return jsonify({'error': 'No se pudo obtener la respuesta de la tarea creada'}), 500

        return jsonify({'message': 'Checklist creado y asignado exitosamente'}), 201

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
