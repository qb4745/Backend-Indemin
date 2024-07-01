from flask import Flask
from flask_cors import CORS
import logging
from config import JWT_SECRET_KEY  # Importar JWT_SECRET_KEY correctamente
from api.usuario import usuario_bp
from api.checklist import checklist_bp
from api.maquinas import maquinas_bp
from api.crear_maquinas import crear_maquinas_bp
from api.update_checklist import update_checklist_bp
from api.edit_checklist import edit_checklist_bp
from api.faenas import faenas_bp
from api.status import status_bp
from api.update_status import update_status_bp
from api.eliminar_checklist import eliminar_checklist_bp
from api.crear_usuario import crear_usuario_bp
from api.estado_checklist import estado_checklist_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = JWT_SECRET_KEY  # Configurar el secreto JWT directamente desde config.py

# Configuración de CORS para permitir solicitudes desde localhost:8100 y 127.0.0.1:5000
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8100", "http://127.0.0.1:5500", "https://alvarofenero.github.io"]}})

# Configurar el registro básico
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Registrar los blueprints existentes
app.register_blueprint(usuario_bp, url_prefix='/api')
app.register_blueprint(checklist_bp, url_prefix='/api')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(crear_maquinas_bp, url_prefix='/api')
app.register_blueprint(update_checklist_bp, url_prefix='/api')
app.register_blueprint(edit_checklist_bp, url_prefix='/api')
app.register_blueprint(faenas_bp, url_prefix='/api')
app.register_blueprint(status_bp, url_prefix='/api')
app.register_blueprint(update_status_bp, url_prefix='/api')
app.register_blueprint(eliminar_checklist_bp, url_prefix='/api')
app.register_blueprint(crear_usuario_bp, url_prefix='/api')
app.register_blueprint(estado_checklist_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
