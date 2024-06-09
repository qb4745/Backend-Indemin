import requests
import json
import datetime
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

edit_checklist_bp = Blueprint('edit_checklist_bp', __name__)

@edit_checklist_bp.route('/edit_checklist/<int:id>', methods=['PATCH'])
@cross_origin(origin='http://localhost:8100')
def edit_checklist(id):
    try:
        data = request.json
        print("Received data:", data)

        nombre = data.get('nombre')
        id_tipo_maquina = data.get('id_tipo_maquina')
        componentes = data.get('componentes')

        # Actualizar el checklist con el ID proporcionado
        checklist_data = {}
        if nombre:
            checklist_data['nombre'] = nombre
        if id_tipo_maquina:
            checklist_data['id_tipo_maquina'] = id_tipo_maquina

        if checklist_data:
            response = requests.patch(f"{SUPABASE_URL}/checklists/{id}", headers=HEADERS, data=json.dumps(checklist_data))
            if response.status_code != 200:
                return jsonify({'error': 'No se pudo actualizar el checklist'}), 500

        # Actualizar los componentes y tareas asociadas
        if componentes:
            for componente in componentes:
                componente_id = componente.get('id_componente')
                componente_nombre = componente.get('nombre')
                if componente_id:
                    # Actualizar el nombre del componente
                    componente_data = {'nombre': componente_nombre}
                    response = requests.patch(f"{SUPABASE_URL}/componentes/{componente_id}", headers=HEADERS, data=json.dumps(componente_data))
                    if response.status_code != 200:
                        return jsonify({'error': f'No se pudo actualizar el componente con ID {componente_id}'}), 500
                else:
                    # Si no hay ID, se agrega un nuevo componente
                    response = requests.post(f"{SUPABASE_URL}/componentes", headers=HEADERS, data=json.dumps({'nombre': componente_nombre}))
                    if response.status_code != 201:
                        return jsonify({'error': 'No se pudo crear un nuevo componente'}), 500
                    componente_id = response.json().get('id_componente')

                # Actualizar las tareas asociadas al componente
                tareas = componente.get('tareas', [])
                if tareas:
                    for tarea in tareas:
                        tarea_id = tarea.get('id_tarea')
                        tarea_nombre = tarea.get('nombre')
                        if tarea_id:
                            # Actualizar el nombre de la tarea
                            tarea_data = {'nombre': tarea_nombre}
                            response = requests.patch(f"{SUPABASE_URL}/tareas/{tarea_id}", headers=HEADERS, data=json.dumps(tarea_data))
                            if response.status_code != 200:
                                return jsonify({'error': f'No se pudo actualizar la tarea con ID {tarea_id}'}), 500
                        else:
                            # Si no hay ID, se agrega una nueva tarea
                            response = requests.post(f"{SUPABASE_URL}/tareas", headers=HEADERS, data=json.dumps({'nombre': tarea_nombre, 'id_componente': componente_id}))
                            if response.status_code != 201:
                                return jsonify({'error': 'No se pudo crear una nueva tarea'}), 500

        return jsonify({'message': 'Checklist actualizado exitosamente'}), 200

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
