import json
import requests
import logging
from flask_cors import cross_origin
from flask import Blueprint, jsonify, request
from config import SUPABASE_URL, HEADERS
from api.faenas import crear_faena  # Importa la función para crear faenas

crear_maquinas_bp = Blueprint('crear_maquinas_bp', __name__)

# Configurar el registro de eventos
formatter = logging.Formatter('%(asctime)s - %(levellevel)s - %(message)s')
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
maquinas_logger = logging.getLogger(__name__)
maquinas_logger.addHandler(handler)
maquinas_logger.setLevel(logging.DEBUG)

@crear_maquinas_bp.route('/crear-maquinas', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'])
def crear_maquinas():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        data = request.json
        codigo_interno = data.get('codigo_interno')
        id_tipo_maquina = data.get('id_tipo_maquina')
        marca = data.get('marca')
        modelo = data.get('modelo')
        id_faena = data.get('id_faena')
        
        # Verifica si se proporcionó un ID de faena válido
        if id_faena is None or id_faena == 0:
            # Si no se proporcionó un ID de faena o es inválido, crea una faena automáticamente
            id_faena = crear_faena()
            if id_faena is None:
                return jsonify({'error': 'No se pudo crear la faena automáticamente'}), 500
        
        # Crea el cuerpo de datos para la solicitud a Supabase, sin incluir `id_maquina`
        maquina_data = {
            'codigo_interno': codigo_interno,
            'id_tipo_maquina': id_tipo_maquina,
            'marca': marca,
            'modelo': modelo,
            'id_faena': id_faena
        }

        maquinas_logger.debug(f"Datos de la máquina a enviar: {maquina_data}")
        
        # Realiza la solicitud POST a Supabase para crear la máquina
        url = f'{SUPABASE_URL}/maquinas'
        response = requests.post(url, headers=HEADERS, data=json.dumps(maquina_data))
        maquinas_logger.debug(f"Respuesta de Supabase al crear máquina: {response.status_code} - {response.text}")
        
        if response.status_code == 201:
            nueva_maquina = response.json()
            return jsonify(nueva_maquina), 201
        else:
            error_message = f"Error al crear máquina. Código de respuesta: {response.status_code}. Detalles: {response.text}"
            maquinas_logger.error(error_message)
            return jsonify({'error': 'No se pudo crear la máquina'}), response.status_code
    
    except Exception as e:
        maquinas_logger.error(f"Excepción creando máquina: {str(e)}")
        return jsonify({'error': 'Error en el servidor'}), 500
