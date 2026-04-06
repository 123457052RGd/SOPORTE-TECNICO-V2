"""
Rutas de autenticación - Flask + MySQL + bcrypt (werkzeug)
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from dao.usuario_dao import UsuarioDAO

auth_bp = Blueprint('auth', __name__)

# Roles que tienen acceso al panel de administración
ROLES_ADMIN = ('admin', 'tecnico', 'jefe')


# ──────────────────────────────────────────────
# Decoradores de autenticación
# ──────────────────────────────────────────────

def login_required(f):
    """Requiere que el usuario esté autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Requiere rol de administrador, técnico o jefe"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('rol') not in ROLES_ADMIN:
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ──────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if 'user_id' in session:
        if session.get('rol') in ROLES_ADMIN:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email y contraseña son requeridos', 'warning')
            return render_template('auth/login.html')

        usuario = UsuarioDAO.validar_credenciales(email, password)

        if usuario:
            session.permanent  = True
            session['user_id'] = usuario['id_usuario']
            session['nombre']  = usuario['nombre_completo']
            session['email']   = usuario['email']
            session['rol']     = usuario['rol_nombre']

            flash(f'¡Bienvenido {usuario["nombre_completo"]}!', 'success')

            if usuario['rol_nombre'] in ROLES_ADMIN:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro deshabilitado — solo el admin crea usuarios"""
    if request.method == 'POST':
        flash('El registro público está deshabilitado. Contacte al administrador.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')