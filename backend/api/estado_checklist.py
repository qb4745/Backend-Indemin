import requests
import json
from flask import Blueprint, jsonify, request, g
from flask_cors import CORS, cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required

estado_checklist_bp = Blueprint("estado_checklist_bp", __name__)
CORS(
    estado_checklist_bp,
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ],
    supports_credentials=True,
)


@estado_checklist_bp.route("/realizar_checklist", methods=["POST"])
@cross_origin(
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ],
    headers=["Content-Type", "Authorization"],
)
@token_required
def realizar_checklist():
    try:
        data = request.json
        id_checklist = data.get("id_checklist")
        id_usuario = g.current_user  # Obtener el usuario del token
        fecha_realizacion = data.get("fecha_realizacion")
        comentarios = data.get("comentarios", "")
        estados_tareas = data.get("estados_tareas")

        if (
            not id_checklist
            or not id_usuario
            or not fecha_realizacion
            or not estados_tareas
        ):
            return jsonify({"message": "Faltan datos requeridos"}), 400

        checklist_realizado_data = {
            "id_checklist": id_checklist,
            "id_usuario": id_usuario,
            "fecha_realizacion": fecha_realizacion,
            "comentarios": comentarios,
        }

        response = requests.post(
            SUPABASE_URL + "checklists_realizados",
            headers=HEADERS,
            data=json.dumps(checklist_realizado_data),
        )
        if response.status_code != 201:
            print("Error al crear la realización del checklist:", response.text)
            return (
                jsonify({"message": "Error al crear la realización del checklist"}),
                500,
            )

        try:
            response_data = response.json()
            id_checklist_realizado = response_data.get("id_checklist_realizado")
        except json.JSONDecodeError:
            print("Respuesta vacía al crear la realización del checklist.")
            id_checklist_realizado = None

        if not id_checklist_realizado:
            response = requests.get(
                SUPABASE_URL
                + f"checklists_realizados?id_checklist=eq.{id_checklist}&id_usuario=eq.{id_usuario}&fecha_realizacion=eq.{fecha_realizacion}",
                headers=HEADERS,
            )
            if response.status_code != 200 or not response.json():
                print("No se pudo obtener el ID del checklist realizado.")
                return (
                    jsonify(
                        {"message": "No se pudo obtener el ID del checklist realizado"}
                    ),
                    500,
                )
            id_checklist_realizado = response.json()[0]["id_checklist_realizado"]

        for estado_tarea in estados_tareas:
            estado_tarea_data = {
                "id_tarea": estado_tarea["id_tarea"],
                "status": estado_tarea["estado"],
                "id_checklist_realizado": id_checklist_realizado,
            }
            print("Enviando datos de estado de tarea:", estado_tarea_data)
            response = requests.post(
                SUPABASE_URL + "tarea_estado",
                headers=HEADERS,
                data=json.dumps(estado_tarea_data),
            )
            print("Respuesta del servidor:", response.status_code, response.text)
            if response.status_code != 201:
                print("Error al guardar el estado de las tareas:", response.text)
                return (
                    jsonify({"message": "Error al guardar el estado de las tareas"}),
                    500,
                )

        return jsonify({"message": "Checklist realizado y guardado exitosamente"}), 201

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


@estado_checklist_bp.route("/checklists_realizados", methods=["GET"])
@cross_origin(
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ]
)
@token_required
def obtener_checklists_realizados():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        filter = request.args.get("filter", "")

        offset = (page - 1) * size
        response = requests.get(
            f"{SUPABASE_URL}checklists_realizados?offset={offset}&limit={size}",
            headers=HEADERS,
        )
        if response.status_code != 200:
            return (
                jsonify({"message": "Error al obtener los checklists realizados"}),
                500,
            )

        checklists_realizados = response.json()
        total_items_response = requests.get(
            f"{SUPABASE_URL}checklists_realizados?select=count", headers=HEADERS
        )
        total_items = total_items_response.json()[0]["count"]
        total_pages = (total_items + size - 1) // size

        for checklist in checklists_realizados:
            user_response = requests.get(
                SUPABASE_URL + f'usuario?id_usuario=eq.{checklist["id_usuario"]}',
                headers=HEADERS,
            )
            if user_response.status_code == 200:
                checklist["usuario"] = user_response.json()[0]["email"]

            checklist_id = checklist["id_checklist"]
            checklist_maquina_response = requests.get(
                SUPABASE_URL + f"checklists_maquinas?id_checklist=eq.{checklist_id}",
                headers=HEADERS,
            )
            if (
                checklist_maquina_response.status_code == 200
                and checklist_maquina_response.json()
            ):
                id_maquina = checklist_maquina_response.json()[0]["id_maquina"]
                maquina_response = requests.get(
                    SUPABASE_URL + f"maquinas?id_maquina=eq.{id_maquina}",
                    headers=HEADERS,
                )
                if maquina_response.status_code == 200:
                    maquina_data = maquina_response.json()[0]
                    checklist["codigo_interno"] = maquina_data["codigo_interno"]
                    faena_response = requests.get(
                        SUPABASE_URL + f'faenas?id_faena=eq.{maquina_data["id_faena"]}',
                        headers=HEADERS,
                    )
                    if faena_response.status_code == 200:
                        checklist["faena"] = faena_response.json()[0]["nombre"]

        return jsonify({"items": checklists_realizados, "totalPages": total_pages}), 200
    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500
