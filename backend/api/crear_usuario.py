import requests
import json
from flask import Blueprint, jsonify, request, g
from flask_cors import CORS, cross_origin
from config import SUPABASE_URL, HEADERS
from auth import token_required

crear_usuario_bp = Blueprint("crear_usuario_bp", __name__)

CORS(
    crear_usuario_bp,
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ],
    supports_credentials=True,
)


# Crear usuario
@crear_usuario_bp.route("/crear_usuario", methods=["POST"])
@cross_origin(
    origins=[
        "https://localhost",
        "http://localhost:8100",
        "http://127.0.0.1:5500",
        "https://alvarofenero.github.io",
    ],
    headers=["Content-Type", "Authorization"],
)
def crear_usuario():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        tipo_usuario = data.get("tipo_usuario", "user")  # 'user' por defecto

        if not email or not password:
            return jsonify({"message": "Email y contraseña son requeridos"}), 400

        # Crear usuario en la base de datos
        usuario_data = {
            "email": email,
            "password": password,
            "tipo_usuario": tipo_usuario,
        }

        response = requests.post(
            SUPABASE_URL + "usuario", headers=HEADERS, data=json.dumps(usuario_data)
        )
        if response.status_code == 201:
            return jsonify({"message": "Usuario creado exitosamente"}), 201
        else:
            return jsonify({"message": "Error al crear el usuario"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


# Obtener lista de usuarios
@crear_usuario_bp.route("/usuarios", methods=["GET"])
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
def obtener_usuarios(current_user):
    try:
        response = requests.get(SUPABASE_URL + "usuario", headers=HEADERS)
        if response.status_code == 200:
            usuarios = response.json()
            return jsonify(usuarios), 200
        else:
            return jsonify({"message": "Error al obtener la lista de usuarios"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


# Editar permisos de usuario
@crear_usuario_bp.route("/editar_permisos/<int:id_usuario>", methods=["PATCH"])
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
def editar_permisos(current_user, id_usuario):
    try:
        data = request.json
        tipo_usuario = data.get("tipo_usuario")

        if not tipo_usuario:
            return jsonify({"message": "Tipo de usuario es requerido"}), 400

        # Actualizar permisos del usuario
        usuario_data = {"tipo_usuario": tipo_usuario}

        response = requests.patch(
            SUPABASE_URL + "usuario?id_usuario=eq." + str(id_usuario),
            headers=HEADERS,
            data=json.dumps(usuario_data),
        )
        if response.status_code == 204:
            return (
                jsonify({"message": "Permisos de usuario actualizados exitosamente"}),
                200,
            )
        else:
            return jsonify({"message": "Error al actualizar permisos de usuario"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


# Eliminar usuario
@crear_usuario_bp.route("/eliminar_usuario/<int:id_usuario>", methods=["DELETE"])
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
def eliminar_usuario(current_user, id_usuario):
    try:
        response = requests.delete(
            SUPABASE_URL + "usuario?id_usuario=eq." + str(id_usuario), headers=HEADERS
        )
        if response.status_code == 204:
            return jsonify({"message": "Usuario eliminado exitosamente"}), 200
        else:
            return jsonify({"message": "Error al eliminar usuario"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


# Cambio de contraseña
@crear_usuario_bp.route("/cambiar_contraseña/<int:id_usuario>", methods=["PATCH"])
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
def cambiar_contraseña(current_user, id_usuario):
    try:
        data = request.json
        nueva_contraseña = data.get("nueva_contraseña")

        if not nueva_contraseña:
            return jsonify({"message": "Nueva contraseña es requerida"}), 400

        # Actualizar contraseña del usuario
        usuario_data = {"password": nueva_contraseña}

        response = requests.patch(
            SUPABASE_URL + "usuario?id_usuario=eq." + str(id_usuario),
            headers=HEADERS,
            data=json.dumps(usuario_data),
        )
        if response.status_code == 204:
            return jsonify({"message": "Contraseña actualizada exitosamente"}), 200
        else:
            return jsonify({"message": "Error al actualizar contraseña"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


# Cambio de correo
@crear_usuario_bp.route("/cambiar_correo/<int:id_usuario>", methods=["PATCH"])
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
def cambiar_correo(current_user, id_usuario):
    try:
        data = request.json
        nuevo_correo = data.get("nuevo_correo")

        if not nuevo_correo:
            return jsonify({"message": "Nuevo correo es requerido"}), 400

        # Actualizar correo del usuario
        usuario_data = {"email": nuevo_correo}

        response = requests.patch(
            SUPABASE_URL + "usuario?id_usuario=eq." + str(id_usuario),
            headers=HEADERS,
            data=json.dumps(usuario_data),
        )
        if response.status_code == 204:
            return jsonify({"message": "Correo actualizado exitosamente"}), 200
        else:
            return jsonify({"message": "Error al actualizar correo"}), 500

    except Exception as e:
        print("Excepción atrapada:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500
