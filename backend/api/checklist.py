import requests
import json
import datetime
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

checklist_bp = Blueprint('checklist_bp', __name__)

@checklist_bp.route('/create_checklist', methods=['POST'])
@cross_origin(origin='http://localhost:8100')
def create_checklist():
    try:
        data = request.json
        print("Received data:", data)

        nombre = data.get('nombre')
        id_tipo_maquina = data.get('id_tipo_maquina')
        codigo_interno = data.get('codigo_interno')
        componentes = data.get('componentes')
        timestamp = datetime.datetime.now().isoformat()

        if not nombre or not id_tipo_maquina or not codigo_interno:
            print("Missing required fields: nombre, id_tipo_maquina, or codigo_interno")
            return jsonify({'error': 'Faltan datos necesarios'}), 400

        # Obtener la máquina por el código interno
        print("Querying machine with codigo_interno:", codigo_interno)
        response = requests.get(SUPABASE_URL + 'maquinas?codigo_interno=eq.' + codigo_interno, headers=HEADERS)
        print("Machine fetch response status:", response.status_code)
        print("Machine fetch response text:", response.text)
        if response.status_code != 200 or not response.json():
            return jsonify({'error': 'Máquina no encontrada'}), 404

        maquina = response.json()[0]
        id_maquina = maquina['id_maquina']

        # Verificar si la máquina con el ID ya tiene un checklist asignado
        response = requests.get(SUPABASE_URL + 'checklists_maquinas?id_maquina=eq.' + str(id_maquina), headers=HEADERS)
        if response.status_code == 200 and response.json():
            print("Machine already has an assigned checklist")
            return jsonify({'error': 'La máquina con el código interno especificado ya tiene un checklist asignado'}), 400

        # Crear el checklist con un timestamp para asegurar unicidad
        checklist_data = {
            'nombre': f"{nombre}_{timestamp}",
            'id_tipo_maquina': id_tipo_maquina
        }
        print("Creating checklist with data:", checklist_data)
        response = requests.post(SUPABASE_URL + 'checklists', headers=HEADERS, data=json.dumps(checklist_data))
        print("Checklist creation response status:", response.status_code)
        print("Checklist creation response text:", response.text)
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
            print("Checklist ID missing in response")
            return jsonify({'error': 'No se pudo obtener el ID del checklist'}), 500

        # Asignar el checklist a la máquina
        checklist_maquina_data = {
            'id_maquina': id_maquina,
            'id_checklist': checklist_id
        }
        response = requests.post(SUPABASE_URL + 'checklists_maquinas', headers=HEADERS, data=json.dumps(checklist_maquina_data))
        print("Checklist assignment response status:", response.status_code)
        print("Checklist assignment response text:", response.text)
        if response.status_code != 201:
            print("Could not assign checklist to the machine")
            return jsonify({'error': 'No se pudo asignar el checklist a la máquina'}), 500

        # Crear componentes y tareas
        for componente in componentes:
            componente_data = {
                'nombre': componente['nombre'],
                'id_checklist': checklist_id
            }
            print("Creating component with data:", componente_data)
            response = requests.post(SUPABASE_URL + 'componentes', headers=HEADERS, data=json.dumps(componente_data))
            print("Component creation response status:", response.status_code)
            print("Component creation response text:", response.text)
            if response.status_code != 201:
                print("Could not create component")
                return jsonify({'error': 'No se pudo crear el componente'}), 500

            # Manejar posible respuesta vacía para la creación de componentes
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
                print("Component ID missing in response")
                return jsonify({'error': 'No se pudo obtener el ID del componente'}), 500

            for tarea in componente['tasks']:
                tarea_data = {
                    'nombre': tarea['nombre'],
                    'frecuencia': tarea.get('frecuencia', ''),
                    'id_componente': componente_id
                }
                print("Creating task with data:", tarea_data)
                response = requests.post(SUPABASE_URL + 'tareas', headers=HEADERS, data=json.dumps(tarea_data))
                print("Task creation response status:", response.status_code)
                print("Task creation response text:", response.text)
                if response.status_code != 201:
                    print("Could not create task")
                    return jsonify({'error': 'No se pudo crear la tarea'}), 500

        return jsonify({'message': 'Checklist creado y asignado exitosamente'}), 201

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
