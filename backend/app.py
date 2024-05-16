from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/usuario', methods=['GET', 'POST'])
@cross_origin(origin='http://localhost:8100') # Permitir solicitudes desde http://localhost:8100
def usuario():
    # Lógica de la ruta...
    return jsonify({'message': 'OK'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)