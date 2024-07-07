import json
import requests
import logging
from flask_cors import cross_origin
from flask import Blueprint, jsonify
from config import SUPABASE_URL, HEADERS

faenas_bp = Blueprint("faenas_bp", __name__)

# Configurar el registro de eventos
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("app.log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
faenas_logger = logging.getLogger(__name__)
faenas_logger.addHandler(handler)
faenas_logger.setLevel(logging.DEBUG)


def crear_faena():
    try:
        # Lógica para crear una faena automáticamente
        nueva_faena = {"nombre": "Faena Automática"}

        # Realiza la solicitud POST a Supabase para crear la faena
        response = requests.post(
            f"{SUPABASE_URL}/faenas", headers=HEADERS, data=json.dumps(nueva_faena)
        )

        # Verifica el estado de la respuesta y los datos de la respuesta
        faenas_logger.debug(
            f"Solicitud a Supabase: {response.request.method} {response.request.url} - Headers: {response.request.headers} - Data: {response.request.body}"
        )
        faenas_logger.debug(
            f"Respuesta de Supabase: {response.status_code} - {response.text}"
        )

        if response.status_code == 201:
            if response.text.strip():  # Verifica si la respuesta no está vacía
                faena_creada = response.json()
                faenas_logger.info(f"Faena creada con ID: {faena_creada['id']}")
                return faena_creada["id"]
            else:
                faenas_logger.error(
                    "La respuesta de Supabase está vacía pero el estado es 201."
                )
                return None
        else:
            error_message = f"Error al crear faena. Código de respuesta: {response.status_code}. Detalles: {response.text}"
            faenas_logger.error(error_message)
            return None

    except json.JSONDecodeError as e:
        faenas_logger.error(
            f"Error al decodificar JSON: {str(e)} - Respuesta: {response.text}"
        )
        return None
    except Exception as e:
        faenas_logger.error(f"Excepción creando faena: {str(e)}")
        return None


@faenas_bp.route("/crear-faena", methods=["POST"])
@cross_origin(
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ],
    headers=["Content-Type", "Authorization"],
)
def crear_faena_endpoint():
    try:
        id_faena = crear_faena()
        if id_faena is not None:
            return jsonify({"id_faena": id_faena}), 201
        else:
            return jsonify({"error": "No se pudo crear la faena automáticamente"}), 500

    except Exception as e:
        faenas_logger.error(f"Excepción en endpoint crear_faena_endpoint: {str(e)}")
        return jsonify({"error": "Error en el servidor"}), 500
