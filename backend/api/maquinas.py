import requests
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from config import SUPABASE_URL, HEADERS

maquinas_bp = Blueprint('maquinas_bp', __name__)

@maquinas_bp.route('/maquinas', methods=['GET'])
@cross_origin(origins=['http://localhost:8100', 'http://127.0.0.1:5500', 'https://alvarofenero.github.io'])
def get_maquinas():
    try:
        codigo_interno = request.args.get('codigo_interno', '')
        response = requests.get(SUPABASE_URL + 'maquinas', headers=HEADERS)
        print("Machine fetch response status:", response.status_code)
        print("Machine fetch response text:", response.text)
        if response.status_code != 200:
            return jsonify({'error': 'No se pudieron obtener las máquinas'}), 500

        maquinas = response.json()
        
        # Filtramos las máquinas por el código interno
        maquinas_filtradas = [maquina for maquina in maquinas if codigo_interno.lower() in maquina['codigo_interno'].lower()]
        
        return jsonify(maquinas_filtradas), 200
    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'error': 'Error en el servidor'}), 500
