from flask import Flask
from flask_cors import CORS
from api.usuario import usuario_bp
from api.checklist import checklist_bp
from api.maquinas import maquinas_bp 
from api.update_checklist import update_checklist_bp
from api.edit_checklist import edit_checklist_bp

app = Flask(__name__)

# Configuración de CORS con métodos permitidos
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:8100", "methods": ["GET", "POST", "PATCH", "DELETE"]}})

app.register_blueprint(usuario_bp, url_prefix='/api')
app.register_blueprint(checklist_bp, url_prefix='/api')
app.register_blueprint(maquinas_bp, url_prefix='/api')
app.register_blueprint(update_checklist_bp, url_prefix='/api')
app.register_blueprint(edit_checklist_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
