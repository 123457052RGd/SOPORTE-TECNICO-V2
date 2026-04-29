"""
Sistema de Gestion de Soporte Tecnico por Tickets - DIF El Marques
Flask + MySQL Workbench + bcrypt (werkzeug)
Desarrollado por: ING Diego Rubio
"""
from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_mail import Mail
from dotenv import load_dotenv
from datetime import timedelta
from config.database_mysql import test_connection
from routes.auth_routes  import auth_bp
from routes.user_routes  import user_bp
from routes.admin_routes import admin_bp
from utils.email_notificaciones import EmailNotificaciones
load_dotenv()
import os


ROLES_ADMIN = ('admin', 'tecnico', 'jefe')

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dif-soporte-tecnico-2026')

app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

# ── Mail --------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.office365.com')
app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USE_SSL']        = False
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# ── Uploads ───────────────────────────────────────────────────
app.config['UPLOAD_FOLDER']      = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'informatica@difelmarques.gob.mx')
email_notif = EmailNotificaciones(mail, admin_email=ADMIN_EMAIL)
app.extensions['email_notif'] = email_notif

if test_connection():
    print("✅ Conexion a MySQL exitosa")
else:
    print("❌ No se pudo conectar a MySQL.")

# ── Blueprints ────────────────────────────────────────────────
app.register_blueprint(auth_bp,  url_prefix='/auth')
app.register_blueprint(user_bp,  url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')


# ── Ruta principal ────────────────────────────────────────────
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('rol') in ROLES_ADMIN:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))


# ── Health check ──────────────────────────────────────────────
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'sistema': 'ITIL Helpdesk DIF'}), 200


# ── Test email ────────────────────────────────────────────────
@app.route('/test-email')
def test_email():
    try:
        ticket_prueba = {
            'folio': 'TEST-0001', 'titulo': 'Prueba del sistema DIF',
            'estado': 'Abierto', 'nombre_usuario': 'Usuario Prueba',
            'area_usuario': 'Informatica', 'prioridad': 'Alta',
            'nombre_tecnico': 'Tecnico DIF'
        }
        email_notif.enviar_ticket_creado(ticket_prueba, ADMIN_EMAIL)
        return f'✅ Email enviado correctamente a {ADMIN_EMAIL}'
    except Exception as e:
        return f'❌ Error: {str(e)}'


# ── Manejo de sesión expirada ─────────────────────────────────
@app.before_request
def verificar_sesion():
    from flask import request
    rutas_publicas = ('auth.login', 'auth.register', 'static', 'index', 'health')
    if request.endpoint in rutas_publicas:
        return
    # Deja que los blueprints manejen su propia auth


# ── Context processor global ──────────────────────────────────
@app.context_processor
def inject_user():
    """Inyecta datos del usuario en todos los templates"""
    return {
        'session_user_id':   session.get('user_id'),
        'session_user_name': session.get('nombre'),
        'session_rol':       session.get('rol'),
        'session_area':      session.get('area'),
    }


# ── Errores ───────────────────────────────────────────────────
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)