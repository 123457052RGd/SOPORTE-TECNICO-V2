"""
Rutas de autenticación - Flask + MySQL + bcrypt (werkzeug)
NOTA: primer_login se detecta por password = 'TEMPORAL' en sesión,
      sin consulta extra a BD (evita error si la columna no existe).
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from dao.usuario_dao import UsuarioDAO

auth_bp = Blueprint('auth', __name__)

ROLES_ADMIN = ('admin', 'tecnico', 'jefe')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para continuar', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
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


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
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
            perfil = UsuarioDAO.obtener_por_id(usuario["id_usuario"], rol=usuario.get("rol_nombre"))

            session.permanent  = True
            session['user_id'] = usuario['id_usuario']
            session['nombre']  = usuario['nombre_completo']
            session['email']   = usuario['email']
            session['rol']     = usuario['rol_nombre']
            session['foto']    = perfil['foto'] if perfil and perfil.get('foto') else None

            # ── Detectar primer login por columna primer_login (si existe) ──
            # Si la columna no existe en BD, se ignora silenciosamente
            try:
                from dao.base_dao import BaseDAO
                flag = BaseDAO.execute_query(
                    """SELECT primer_login FROM tecnicos WHERE id_tecnico = %s
                       UNION ALL
                       SELECT primer_login FROM usuarios WHERE id = %s
                       LIMIT 1""",
                    (usuario['id_usuario'], usuario['id_usuario']),
                    fetch_one=True
                )
                if flag and flag.get('primer_login'):
                    session['primer_login'] = True
            except Exception:
                # Columna no existe aún — no hay problema, se ignora
                pass

            flash(f'¡Bienvenido, {usuario["nombre_completo"]}!', 'success')

            if usuario['rol_nombre'] in ROLES_ADMIN:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        flash('El registro público está deshabilitado. Contacte al administrador.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')