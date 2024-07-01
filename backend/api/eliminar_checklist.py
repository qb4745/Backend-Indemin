import requests
import logging
from flask import Blueprint, jsonify, request, g
from flask_cors import CORS, cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required

eliminar_checklist_bp = Blueprint('eliminar_checklist_bp', __name__)

CORS(eliminar_checklist_bp, origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'], supports_credentials=True)

@eliminar_checklist_bp.route('/eliminar_checklist', methods=['DELETE'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'], headers=['Content-Type', 'Authorization'])
@token_required
def delete_checklist():
    try:
        codigo_interno = request.args.get('codigo_interno')
        if not codigo_interno:
            return jsonify({'error': 'Código interno es requerido'}), 400

        # Obtener la máquina por el código interno
        response = requests.get(SUPABASE_URL + 'maquinas?codigo_interno=eq.' + codigo_interno, headers=HEADERS)
        if response.status_code != 200 or not response.json():
            return jsonify({'error': 'Máquina no encontrada'}), 404

        maquina = response.json()[0]
        id_maquina = maquina['id_maquina']

        # Obtener el checklist asignado a la máquina
        response = requests.get(SUPABASE_URL + 'checklists_maquinas?id_maquina=eq.' + str(id_maquina), headers=HEADERS)
        if response.status_code != 200 or not response.json():
            return jsonify({'error': 'Checklist no encontrado para la máquina especificada'}), 404

        checklist_maquina = response.json()[0]
        checklist_id = checklist_maquina['id_checklist']

        # Obtener todos los componentes del checklist
        response = requests.get(SUPABASE_URL + 'componentes?id_checklist=eq.' + str(checklist_id), headers=HEADERS)
        if response.status_code != 200:
            return jsonify({'error': 'Error obteniendo componentes del checklist'}), 500

        componentes = response.json()

        # Eliminar todas las tareas de cada componente
        for componente in componentes:
            componente_id = componente['id_componente']
            response = requests.get(SUPABASE_URL + 'tareas?id_componente=eq.' + str(componente_id), headers=HEADERS)
            if response.status_code != 200:
                return jsonify({'error': 'Error obteniendo tareas del componente'}), 500

            tareas = response.json()
            for tarea in tareas:
                tarea_id = tarea['id_tarea']
                response = requests.delete(SUPABASE_URL + 'tareas?id_tarea=eq.' + str(tarea_id), headers=HEADERS)
                if response.status_code != 204:
                    return jsonify({'error': 'Error eliminando tarea'}), 500

            # Eliminar el componente
            response = requests.delete(SUPABASE_URL + 'componentes?id_componente=eq.' + str(componente_id), headers=HEADERS)
            if response.status_code != 204:
                return jsonify({'error': 'Error eliminando componente'}), 500

        # Eliminar la asignación del checklist a la máquina
        response = requests.delete(SUPABASE_URL + 'checklists_maquinas?id_checklist=eq.' + str(checklist_id), headers=HEADERS)
        if response.status_code != 204:
            return jsonify({'error': 'Error eliminando asignación del checklist a la máquina'}), 500

        # Eliminar el checklist
        response = requests.delete(SUPABASE_URL + 'checklists?id_checklist=eq.' + str(checklist_id), headers=HEADERS)
        if response.status_code != 204:
            return jsonify({'error': 'Error eliminando checklist'}), 500

        return jsonify({'message': 'Checklist y sus componentes y tareas eliminados exitosamente'}), 200

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
