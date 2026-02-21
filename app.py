from flask import Flask
from flask_cors import CORS
import os
from auth_routes import auth_bp
from admin_routes import admin_bp
from business_routes import biz_bp

app = Flask(__name__)
# Configura o CORS conforme seu código original
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5500"}})
app.secret_key = os.environ.get("SECRET_KEY")

# Registrando os Blueprints (Módulos)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(biz_bp)

if __name__ == '__main__':
    app.run(debug=True)