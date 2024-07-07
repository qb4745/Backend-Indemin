import requests
import json
import datetime
from flask import Blueprint, jsonify, request, g
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required

checklist_bp = Blueprint("checklist_bp", __name__)


@checklist_bp.route("/create_checklist", methods=["POST"])
@cross_origin(
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ]
)
@token_required
def create_checklist():
    try:
        data = request.json
        nombre = data.get("nombre")
        id_tipo_maquina = data.get("id_tipo_maquina")
        codigo_interno = data.get("codigo_interno")
        componentes = data.get("componentes")
        id_usuario = g.current_user
        timestamp = datetime.datetime.now().isoformat()

        if not nombre or not id_tipo_maquina or not codigo_interno:
            return jsonify({"error": "Faltan datos necesarios"}), 400

        maquina = get_maquina_by_codigo_interno(codigo_interno)
        if not maquina:
            return jsonify({"error": "Máquina no encontrada"}), 404

        id_maquina = maquina["id_maquina"]
        if has_checklist(id_maquina):
            return jsonify({"error": "La máquina ya tiene un checklist asignado"}), 400

        checklist = create_checklist_entry(
            nombre, id_tipo_maquina, id_usuario, timestamp
        )
        if not checklist:
            return jsonify({"error": "No se pudo crear el checklist"}), 500

        checklist_id = checklist.get("id_checklist")
        if not checklist_id:
            return jsonify({"error": "No se pudo obtener el ID del checklist"}), 500

        if not assign_checklist_to_maquina(id_maquina, checklist_id):
            return (
                jsonify({"error": "No se pudo asignar el checklist a la máquina"}),
                500,
            )

        for componente in componentes:
            componente_resp = create_componente(componente, checklist_id)
            if not componente_resp:
                return jsonify({"error": "No se pudo crear el componente"}), 500

            componente_id = componente_resp.get("id_componente")
            if not componente_id:
                return (
                    jsonify({"error": "No se pudo obtener el ID del componente"}),
                    500,
                )

            for tarea in componente["tasks"]:
                if not create_tarea(tarea, componente_id):
                    return jsonify({"error": "No se pudo crear la tarea"}), 500

        return jsonify({"message": "Checklist creado y asignado exitosamente"}), 201

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"error": "Error en el servidor"}), 500


def get_maquina_by_codigo_interno(codigo_interno):
    response = requests.get(
        SUPABASE_URL + "maquinas?codigo_interno=eq." + codigo_interno, headers=HEADERS
    )
    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None


def has_checklist(id_maquina):
    response = requests.get(
        SUPABASE_URL + "checklists_maquinas?id_maquina=eq." + str(id_maquina),
        headers=HEADERS,
    )
    return response.status_code == 200 and response.json()


def create_checklist_entry(nombre, id_tipo_maquina, id_usuario, timestamp):
    checklist_data = {
        "nombre": f"{nombre}_{timestamp}",
        "id_tipo_maquina": id_tipo_maquina,
        "id_usuario": id_usuario,
    }
    response = requests.post(
        SUPABASE_URL + "checklists", headers=HEADERS, data=json.dumps(checklist_data)
    )
    if response.status_code == 201:
        return response.json()
    return fetch_created_item("checklists", checklist_data["nombre"])


def assign_checklist_to_maquina(id_maquina, checklist_id):
    checklist_maquina_data = {"id_maquina": id_maquina, "id_checklist": checklist_id}
    response = requests.post(
        SUPABASE_URL + "checklists_maquinas",
        headers=HEADERS,
        data=json.dumps(checklist_maquina_data),
    )
    return response.status_code == 201


def create_componente(componente, checklist_id):
    componente_data = {"nombre": componente["nombre"], "id_checklist": checklist_id}
    response = requests.post(
        SUPABASE_URL + "componentes", headers=HEADERS, data=json.dumps(componente_data)
    )
    if response.status_code == 201:
        return response.json()
    return fetch_created_item("componentes", componente_data["nombre"])


def create_tarea(tarea, componente_id):
    tarea_data = {
        "nombre": tarea["nombre"],
        "frecuencia": tarea.get("frecuencia", ""),
        "id_componente": componente_id,
    }
    response = requests.post(
        SUPABASE_URL + "tareas", headers=HEADERS, data=json.dumps(tarea_data)
    )
    if response.status_code == 201:
        return True
    return fetch_created_item("tareas", tarea_data["nombre"], componente_id)


def fetch_created_item(table, name, componente_id=None):
    url = f"{SUPABASE_URL}{table}?nombre=eq.{name}"
    if componente_id:
        url += f"&id_componente=eq.{componente_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200 and response.json():
        return response.json()[0]
    return None
