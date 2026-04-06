"""
Sistema de Gestión de Soporte Técnico por Tickets - DIF El Marques
Flask + MySQL Workbench + bcrypt (werkzeug)
"""
from flask import Flask, render_template, redirect, url_for, session
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Base de datos MySQL
from config.database_mysql import test_connection

# Blueprints
from routes.auth_routes  import auth_bp
from routes.user_routes  import user_bp
from routes.admin_routes import admin_bp

# Utilidades
from utils.email_notificaciones import EmailNotificaciones

# ──────────────────────────────────────────────
# Crear aplicación Flask
# ──────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dif-soporte-tecnico-2026')

# ──────────────────────────────────────────────
# Configuración de correo (Office 365)
# ──────────────────────────────────────────────
app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.office365.com')
app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USE_SSL']        = False
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# ──────────────────────────────────────────────
# Configuración de uploads
# ──────────────────────────────────────────────
app.config['UPLOAD_FOLDER']      = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# ──────────────────────────────────────────────
# Sistema de notificaciones por email
# ──────────────────────────────────────────────
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'informatica@difelmarques.gob.mx')
email_notif = EmailNotificaciones(mail, admin_email=ADMIN_EMAIL)
app.extensions['email_notif'] = email_notif

# ──────────────────────────────────────────────
# Verificar conexión MySQL al arrancar
# ──────────────────────────────────────────────
if test_connection():
    print("✅ Conexión a MySQL exitosa")
else:
    print(" ❌ No se pudo conectar a MySQL. Verifica que MySQL Workbench esté corriendo.")

# ──────────────────────────────────────────────
# Registrar Blueprints
# ──────────────────────────────────────────────
app.register_blueprint(auth_bp,  url_prefix='/auth')
app.register_blueprint(user_bp,  url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')

# ──────────────────────────────────────────────
# Ruta principal → redirige según rol
# ──────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('rol') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

# ──────────────────────────────────────────────
# Ruta de prueba de correo
# ──────────────────────────────────────────────
@app.route('/test-email')
def test_email():
    try:
        ticket_prueba = {
            'folio':        'TEST-0001',
            'titulo':       'Prueba del sistema DIF',
            'estado':       'Abierto',
            'nombre_usuario': 'Usuario Prueba',
            'area_usuario': 'Informática',
            'prioridad':    'Alta',
            'nombre_tecnico': 'Técnico DIF'
        }
        email_notif.enviar_ticket_creado(ticket_prueba, ADMIN_EMAIL)
        return f'✅ Email enviado correctamente a {ADMIN_EMAIL}'
    except Exception as e:
        return f'❌ Error: {str(e)}'

# ──────────────────────────────────────────────
# Manejo de errores
# ──────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ──────────────────────────────────────────────
# Ejecutar servidor
# ──────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
