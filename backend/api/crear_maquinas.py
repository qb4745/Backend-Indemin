import json
import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS
from api.faenas import crear_faena  # Importa la función para crear faenas

crear_maquinas_bp = Blueprint('crear_maquinas_bp', __name__)

@crear_maquinas_bp.route('/crear-maquinas', methods=['POST'])
@cross_origin(origins='http://localhost:8100')
def crear_maquinas():
    try:
        data = request.json
        id_maquina = data.get('id_maquina')
        codigo_interno = data.get('codigo_interno')
        id_tipo_maquina = data.get('id_tipo_maquina')
        id_marca = data.get('id_marca')
        modelo = data.get('modelo')
        id_faena = data.get('id_faena')
        
        # Verifica si se proporcionó un ID de faena válido
        if id_faena is None:
            # Si no se proporcionó un ID de faena, crea una faena automáticamente
            id_faena = crear_faena()
            if id_faena is None:
                return jsonify({'error': 'No se pudo crear la faena automáticamente'}), 500
        
        # Crea el cuerpo de datos para la solicitud a Supabase
        data = {
            'id_maquina': id_maquina,
            'codigo_interno': codigo_interno,
            'id_tipo_maquina': id_tipo_maquina,
            'id_marca': id_marca,
            'modelo': modelo,
            'id_faena': id_faena
        }
        
        # Realiza la solicitud POST a Supabase para crear la máquina
        response = requests.post(SUPABASE_URL + 'maquinas', headers=HEADERS, data=json.dumps(data))
        print("Machine creation response status:", response.status_code)
        print("Machine creation response text:", response.text)
        
        # Verifica si la solicitud fue exitosa (código 201 para creación exitosa)
        if response.status_code == 201:
            nueva_maquina = response.json()
            return jsonify(nueva_maquina), 201
        else:
            return jsonify({'error': 'No se pudo crear la máquina'}), response.status_code
    
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
