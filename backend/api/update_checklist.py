from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS
import requests

update_checklist_bp = Blueprint('update_checklist_bp', __name__)

@update_checklist_bp.route('/checklists', methods=['GET'])
@cross_origin(origin='http://localhost:8100')
def get_checklists():
    try:
        codigo_interno = request.args.get('codigo_interno')
        print(f"Fetching checklists for codigo_interno: {codigo_interno}")
        
        # Obtener la máquina con el código interno
        response = requests.get(f"{SUPABASE_URL}maquinas?codigo_interno=eq.{codigo_interno}", headers=HEADERS)
        print("Machine fetch response status:", response.status_code)
        print("Machine fetch response text:", response.text)
        
        if response.status_code != 200 or not response.json():
            return jsonify({'error': 'Máquina no encontrada'}), 404
        
        maquina = response.json()[0]
        id_maquina = maquina['id_maquina']
        
        # Obtener los checklists asociados a esta máquina
        response = requests.get(f"{SUPABASE_URL}checklists_maquinas?id_maquina=eq.{id_maquina}", headers=HEADERS)
        print("Checklist-maquina fetch response status:", response.status_code)
        print("Checklist-maquina fetch response text:", response.text)
        
        if response.status_code != 200:
            return jsonify({'error': 'No se pudieron obtener los checklists asociados'}), 500
        
        checklists_maquinas = response.json()
        checklist_ids = [cm['id_checklist'] for cm in checklists_maquinas]
        
        # Obtener los detalles de los checklists, incluyendo componentes y tareas
        checklists = []
        for checklist_id in checklist_ids:
            response = requests.get(f"{SUPABASE_URL}checklists?id_checklist=eq.{checklist_id}", headers=HEADERS)
            if response.status_code == 200 and response.json():
                checklist = response.json()[0]
                # Obtener componentes del checklist
                response_componentes = requests.get(f"{SUPABASE_URL}componentes?id_checklist=eq.{checklist_id}", headers=HEADERS)
                if response_componentes.status_code == 200 and response_componentes.json():
                    componentes = response_componentes.json()
                    for componente in componentes:
                        componente_id = componente['id_componente']
                        # Obtener tareas del componente
                        response_tareas = requests.get(f"{SUPABASE_URL}tareas?id_componente=eq.{componente_id}", headers=HEADERS)
                        if response_tareas.status_code == 200 and response_tareas.json():
                            componente['tasks'] = response_tareas.json()
                        else:
                            componente['tasks'] = []
                    checklist['componentes'] = componentes
                else:
                    checklist['componentes'] = []
                checklists.append(checklist)
            else:
                print(f"Error fetching details for checklist ID: {checklist_id}")

        print("Final checklists data:", checklists)
        return jsonify(checklists), 200
    except requests.exceptions.RequestException as e:
        print("RequestException:", str(e))
        return jsonify({'error': 'Error en la solicitud', 'details': str(e)}), 500
    except ValueError as e:
        print("ValueError:", str(e))
        return jsonify({'error': 'Error al parsear la respuesta', 'details': str(e)}), 500
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor', 'details': str(e)}), 500
