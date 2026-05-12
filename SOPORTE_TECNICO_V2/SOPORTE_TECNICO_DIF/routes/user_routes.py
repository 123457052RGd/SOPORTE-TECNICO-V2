"""
Rutas para usuarios finales - MySQL
FIXES:
  - api_notificaciones: filtra oculta=0 (igual que admin) para usuarios
  - marcar_notificaciones_leidas: commit=True ya estaba, ahora también devuelve conteo correcto
  - NUEVO: endpoint ocultar notificación para usuarios (igual que admin)
  - Notificaciones: usuarios SOLO ven las suyas (WHERE id_usuario = session.user_id)
    Los técnicos/admins ven las suyas por el mismo mecanismo — cada uno tiene sus filas propias
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify, current_app, make_response)
from routes.auth_routes import login_required
from dao.ticket_dao import TicketDAO, HistorialDAO
from dao.equipo_dao import EquipoDAO
from dao.usuario_dao import UsuarioDAO
from dao.catalogo_dao import CatalogoDAO
from models.models import Ticket
import os

user_bp = Blueprint('user', __name__)


def _color_prioridad(prioridad):
    return {
        'Baja':    '#43a047',
        'Media':   '#fb8c00',
        'Alta':    '#e53935',
        'Critica': '#6a1b9a',
        'Crítica': '#6a1b9a',
    }.get(prioridad, '#888888')


def _color_estado(estado):
    return {
        'Abierto':    '#fb8c00',
        'En Proceso': '#0288d1',
        'Resuelto':   '#43a047',
        'Cerrado':    '#757575',
    }.get(estado, '#888888')


def _preparar_tickets(tickets):
    resultado = []
    for t in tickets:
        if not isinstance(t, dict):
            t = dict(t)
        if t.get('fecha_creacion') and not isinstance(t['fecha_creacion'], str):
            t['fecha_creacion'] = str(t['fecha_creacion'])
        t['color_prioridad'] = _color_prioridad(t.get('prioridad', ''))
        t['color_estado']    = _color_estado(t.get('estado', ''))
        resultado.append(t)
    return resultado


# ──────────────────────────────────────────────
# DASHBOARD USUARIO
# ──────────────────────────────────────────────
@user_bp.route('/dashboard')
@login_required
def dashboard():
    tickets_raw       = TicketDAO.obtener_por_usuario(session['user_id'])
    tickets           = _preparar_tickets(tickets_raw)
    total_tickets     = len(tickets)
    tickets_abiertos  = len([t for t in tickets if t.get('estado') == 'Abierto'])
    tickets_proceso   = len([t for t in tickets if t.get('estado') == 'En Proceso'])
    tickets_resueltos = len([t for t in tickets if t.get('estado') in ['Resuelto', 'Cerrado']])
    equipos_usuario   = EquipoDAO.obtener_por_usuario(session['user_id'])

    if session.pop('primer_login', False):
        flash(
            '¡Bienvenido! Por seguridad, te recomendamos cambiar tu contraseña '
            'desde tu perfil lo antes posible.',
            'primer_login'
        )

    return render_template(
        'user/dashboard.html',
        tickets=tickets,
        total_tickets=total_tickets,
        tickets_abiertos=tickets_abiertos,
        tickets_proceso=tickets_proceso,
        tickets_resueltos=tickets_resueltos,
        equipos=equipos_usuario,
        total_equipos=len(equipos_usuario),
    )


# ──────────────────────────────────────────────
# NUEVO TICKET
# ──────────────────────────────────────────────
@user_bp.route('/nuevo-ticket', methods=['GET', 'POST'])
@login_required
def nuevo_ticket():
    if request.method == 'POST':
        titulo           = request.form.get('titulo', '').strip()
        descripcion      = request.form.get('descripcion', '').strip()
        id_tipo_problema = request.form.get('id_tipo_problema')
        prioridad        = request.form.get('id_prioridad')
        id_equipo        = request.form.get('id_equipo') or None

        mapa_prioridad = {'1': 'Baja', '2': 'Media', '3': 'Alta', '4': 'Crítica'}
        if prioridad in mapa_prioridad:
            prioridad = mapa_prioridad[prioridad]
        if prioridad not in ('Baja', 'Media', 'Alta', 'Crítica', 'Critica'):
            prioridad = 'Media'

        if not titulo or not descripcion:
            flash('El título y la descripción son obligatorios.', 'warning')
        else:
            ticket = Ticket(
                id_usuario=session['user_id'],
                id_equipo=id_equipo,
                id_tipo_problema=id_tipo_problema,
                titulo=titulo,
                descripcion=descripcion,
                id_prioridad=prioridad,
            )
            ticket.prioridad = prioridad
            id_nuevo = TicketDAO.crear_ticket(ticket)

            if id_nuevo:
                HistorialDAO.agregar_registro(
                    id_nuevo, session['user_id'],
                    'Ticket creado', 'Registrado por el usuario'
                )
                try:
                    ticket_info = TicketDAO.obtener_por_id(id_nuevo)
                    email_notif = current_app.extensions.get('email_notif')
                    if email_notif and ticket_info:
                        email_notif.enviar_ticket_creado(ticket_info, session.get('email'))
                except Exception as e:
                    current_app.logger.warning(f'[Email] {e}')

                flash('Ticket creado exitosamente', 'success')
                return redirect(url_for('user.ver_ticket', id_ticket=id_nuevo))
            else:
                flash('Error al crear el ticket. Intenta de nuevo.', 'danger')

    try:
        tipos_problema = CatalogoDAO.obtener_tipos_problema()
    except Exception:
        tipos_problema = []

    try:
        prioridades = CatalogoDAO.obtener_prioridades()
    except Exception:
        prioridades = [
            {'id': 1, 'nombre': 'Baja'},
            {'id': 2, 'nombre': 'Media'},
            {'id': 3, 'nombre': 'Alta'},
            {'id': 4, 'nombre': 'Crítica'},
        ]

    equipos = EquipoDAO.obtener_por_usuario(session['user_id'])

    return render_template(
        'user/nuevo_ticket.html',
        tipos_problema=tipos_problema,
        prioridades=prioridades,
        equipos=equipos,
    )


# ──────────────────────────────────────────────
# VER TICKET
# ──────────────────────────────────────────────
@user_bp.route('/ticket/<int:id_ticket>')
@login_required
def ver_ticket(id_ticket):
    ticket_raw = TicketDAO.obtener_por_id(id_ticket)
    if not ticket_raw:
        flash('Ticket no encontrado', 'danger')
        return redirect(url_for('user.dashboard'))

    ticket = dict(ticket_raw) if not isinstance(ticket_raw, dict) else ticket_raw

    if (ticket.get('id_usuario') != session['user_id']
            and session.get('rol') not in ('admin', 'tecnico', 'jefe')):
        flash('No tienes permiso para ver este ticket', 'danger')
        return redirect(url_for('user.dashboard'))

    if ticket.get('fecha_creacion') and not isinstance(ticket['fecha_creacion'], str):
        ticket['fecha_creacion'] = str(ticket['fecha_creacion'])
    ticket['color_prioridad'] = _color_prioridad(ticket.get('prioridad', ''))
    ticket['color_estado']    = _color_estado(ticket.get('estado', ''))
    historial = HistorialDAO.obtener_por_ticket(id_ticket)

    return render_template('user/ver_ticket.html', ticket=ticket, historial=historial)


# ──────────────────────────────────────────────
# DESCARGAR PDF DEL TICKET
# ──────────────────────────────────────────────
@user_bp.route('/ticket/<int:id_ticket>/pdf')
@login_required
def descargar_ticket_pdf(id_ticket):
    ticket_raw = TicketDAO.obtener_por_id(id_ticket)
    if not ticket_raw:
        flash('Ticket no encontrado', 'danger')
        return redirect(url_for('user.dashboard'))

    ticket = dict(ticket_raw) if not isinstance(ticket_raw, dict) else ticket_raw
    if (ticket.get('id_usuario') != session['user_id']
            and session.get('rol') not in ('admin', 'tecnico', 'jefe')):
        flash('No tienes permiso', 'danger')
        return redirect(url_for('user.dashboard'))

    if ticket.get('fecha_creacion') and not isinstance(ticket['fecha_creacion'], str):
        ticket['fecha_creacion'] = str(ticket['fecha_creacion'])
    ticket['color_prioridad'] = _color_prioridad(ticket.get('prioridad', ''))
    ticket['color_estado']    = _color_estado(ticket.get('estado', ''))
    historial = HistorialDAO.obtener_por_ticket(id_ticket)

    html_str = render_template('user/ticket_pdf.html', ticket=ticket, historial=historial)

    # Intentar weasyprint primero
    try:
        from weasyprint import HTML as WP_HTML
        pdf_bytes = WP_HTML(string=html_str, base_url=request.host_url).write_pdf()
        response  = make_response(pdf_bytes)
        response.headers['Content-Type']        = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=ticket_{ticket["folio"]}.pdf'
        return response
    except Exception:
        pass

    # Fallback: pdfkit (wkhtmltopdf)
    try:
        import pdfkit, tempfile, os
        options = {
            'encoding': 'UTF-8',
            'quiet': '',
            'no-outline': None,
            'margin-top': '10mm', 'margin-bottom': '10mm',
            'margin-left': '12mm', 'margin-right': '12mm',
        }
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        pdfkit.from_string(html_str, tmp_path, options=options)
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        os.unlink(tmp_path)
        response = make_response(pdf_bytes)
        response.headers['Content-Type']        = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=ticket_{ticket["folio"]}.pdf'
        return response
    except Exception as e:
        current_app.logger.error(f'[PDF] Error generando PDF: {e}')
        flash(f'No se pudo generar el PDF: {e}', 'danger')
        return redirect(url_for('user.ver_ticket', id_ticket=id_ticket))


# ──────────────────────────────────────────────
# MIS TICKETS
# ──────────────────────────────────────────────
@user_bp.route('/mis-tickets')
@login_required
def mis_tickets():
    tickets = _preparar_tickets(TicketDAO.obtener_por_usuario(session['user_id']))
    return render_template('user/mis_tickets.html', tickets=tickets)


# ──────────────────────────────────────────────
# PERFIL
# ──────────────────────────────────────────────
@user_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    from werkzeug.utils import secure_filename
    ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    if request.method == 'POST':
        nombre        = request.form.get('nombre', '').strip()
        apellido      = request.form.get('apellido', '').strip()
        email         = request.form.get('email', '').strip().lower()
        telefono      = request.form.get('telefono', '').strip()
        area          = request.form.get('area', '').strip()
        password_new  = request.form.get('password_new', '').strip()
        password_conf = request.form.get('password_confirm', '').strip()

        if password_new and password_new != password_conf:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('user.perfil'))
        if password_new and len(password_new) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'warning')
            return redirect(url_for('user.perfil'))

        foto_filename = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                ext = foto.filename.rsplit('.', 1)[-1].lower()
                if ext in ALLOWED:
                    filename = secure_filename(f"perfil_{session['user_id']}.{ext}")
                    carpeta  = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
                    os.makedirs(carpeta, exist_ok=True)
                    foto.save(os.path.join(carpeta, filename))
                    foto_filename = filename
                else:
                    flash('Formato de imagen no permitido (usa PNG, JPG, WEBP, GIF)', 'warning')
                    return redirect(url_for('user.perfil'))

        datos = {
            'nombre':       nombre,
            'apellido':     apellido,
            'email':        email,
            'telefono':     telefono or None,
            'area':         area,
            'password_new': password_new or None,
            'foto':         foto_filename,
        }

        ok = UsuarioDAO.actualizar_usuario_completo(
            session['user_id'], datos, session.get('rol', 'usuario')
        )

        if ok is True:
            if nombre:
                session['nombre'] = f"{nombre} {apellido}".strip()
            if email:
                session['email'] = email
            if foto_filename:
                session['foto'] = foto_filename
            if password_new:
                try:
                    from dao.base_dao import BaseDAO as _BD
                    _BD.execute_query(
                        "UPDATE usuarios SET primer_login = 0 WHERE id = %s",
                        (session['user_id'],), commit=True
                    )
                except Exception:
                    pass
                session.pop('primer_login', None)
            session.modified = True
            flash('Perfil actualizado correctamente.', 'success')
        elif ok == 'email_duplicado':
            flash('Ese correo ya está en uso por otro usuario', 'danger')
        else:
            flash('Error al actualizar el perfil', 'danger')

        return redirect(url_for('user.perfil'))

    usuario = UsuarioDAO.obtener_por_id(session['user_id'])
    return render_template('user/perfil.html', usuario=usuario)


# ──────────────────────────────────────────────
# BORRAR FOTO DE PERFIL
# ──────────────────────────────────────────────
@user_bp.route('/perfil/borrar-foto', methods=['POST'])
@login_required
def borrar_foto():
    import os
    from dao.base_dao import BaseDAO
    usuario = UsuarioDAO.obtener_por_id(session['user_id'])
    if usuario and usuario.get('foto'):
        try:
            ruta = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), usuario['foto'])
            if os.path.exists(ruta):
                os.remove(ruta)
        except Exception:
            pass
        BaseDAO.execute_query(
            'UPDATE usuarios SET foto = NULL WHERE id = %s',
            (session['user_id'],), commit=True
        )
        session.pop('foto', None)
        session.modified = True
        flash('Foto de perfil eliminada.', 'success')
    return redirect(url_for('user.perfil'))


# ──────────────────────────────────────────────
# API: SUGERENCIAS POR TIPO DE PROBLEMA
# ──────────────────────────────────────────────
@user_bp.route('/api/sugerencias/<int:id_tipo>')
@login_required
def api_sugerencias(id_tipo):
    try:
        sugerencias = CatalogoDAO.obtener_sugerencias_por_tipo(id_tipo)
        return jsonify(sugerencias)
    except Exception as e:
        current_app.logger.warning(f'[Sugerencias] {e}')
        return jsonify([])


# ──────────────────────────────────────────────
# API: TIPOS DE PROBLEMA
# ──────────────────────────────────────────────
@user_bp.route('/api/tipos-problema', methods=['GET'])
@login_required
def api_tipos_problema_lista():
    try:
        tipos = CatalogoDAO.obtener_tipos_problema()
        return jsonify(tipos)
    except Exception as e:
        current_app.logger.warning(f'[TiposProblema GET] {e}')
        return jsonify([])


@user_bp.route('/api/tipos-problema', methods=['POST'])
@login_required
def api_tipos_problema_crear():
    try:
        from dao.base_dao import BaseDAO
        data        = request.get_json(force=True) or {}
        nombre      = (data.get('nombre') or '').strip()
        descripcion = (data.get('descripcion') or '').strip()
        categoria   = (data.get('categoria') or 'General').strip()

        if not nombre:
            return jsonify({'ok': False, 'error': 'El nombre es obligatorio'}), 400

        existente = BaseDAO.execute_query(
            'SELECT id_tipo, nombre FROM tipos_problema WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s))',
            (nombre,), fetch_one=True
        )
        if existente:
            return jsonify({'ok': True, 'id_tipo': existente['id_tipo'],
                            'nombre': existente['nombre'], 'existia': True})

        nuevo_id = BaseDAO.execute_query(
            'INSERT INTO tipos_problema (nombre, descripcion, categoria) VALUES (%s, %s, %s)',
            (nombre, descripcion or nombre, categoria),
            commit=True
        )
        if nuevo_id:
            return jsonify({'ok': True, 'id_tipo': nuevo_id,
                            'nombre': nombre, 'categoria': categoria})
        return jsonify({'ok': False, 'error': 'No se pudo guardar'}), 500

    except Exception as e:
        current_app.logger.error(f'[TiposProblema POST] {e}')
        return jsonify({'ok': False, 'error': str(e)}), 500


# ──────────────────────────────────────────────
# API: NOTIFICACIONES (polling cada 30s)
# REGLA: usuarios solo ven las suyas (id_usuario = session.user_id)
#        técnicos/admins también solo ven las suyas — cada acción crea
#        filas individuales por técnico en ticket_dao._notif
# ──────────────────────────────────────────────
@user_bp.route('/api/notificaciones')
@login_required
def api_notificaciones():
    try:
        from dao.base_dao import BaseDAO
        rows = BaseDAO.execute_query(
            """SELECT id_notificacion, tipo, titulo, mensaje, leida, url_accion,
                      DATE_FORMAT(fecha_creacion, '%d/%m/%Y %H:%i') AS fecha_fmt
               FROM notificaciones
               WHERE id_usuario = %s
                 AND (oculta IS NULL OR oculta = 0)
                 AND (tipo_destinatario IS NULL OR tipo_destinatario = 'usuario')
               ORDER BY fecha_creacion DESC
               LIMIT 5""",
            (session['user_id'],),
            fetch_all=True
        ) or []
        no_leidas = sum(1 for r in rows if not r.get('leida'))
        return jsonify({'notificaciones': rows, 'no_leidas': no_leidas})
    except Exception:
        return jsonify({'notificaciones': [], 'no_leidas': 0})


@user_bp.route('/api/notificaciones/marcar-leidas', methods=['POST'])
@login_required
def marcar_notificaciones_leidas():
    """FIX: commit=True garantiza que el UPDATE se persiste."""
    try:
        from dao.base_dao import BaseDAO
        BaseDAO.execute_query(
            "UPDATE notificaciones SET leida = 1 WHERE id_usuario = %s AND leida = 0",
            (session['user_id'],),
            commit=True
        )
    except Exception:
        pass
    return jsonify({'ok': True})


@user_bp.route('/api/notificaciones/<int:id_notif>/ocultar', methods=['POST'])
@login_required
def ocultar_notificacion(id_notif):
    """
    Oculta la notificación del panel sin borrarla de BD.
    El historial de notificaciones seguirá mostrándola.
    """
    try:
        from dao.base_dao import BaseDAO
        BaseDAO.execute_query(
            "UPDATE notificaciones SET oculta = 1 WHERE id_notificacion = %s AND id_usuario = %s",
            (id_notif, session['user_id']),
            commit=True
        )
    except Exception:
        pass
    return jsonify({'ok': True})


@user_bp.route('/api/notificaciones/borrar-todas', methods=['POST'])
@login_required
def borrar_todas_notificaciones():
    """Borra permanentemente todas las notificaciones del usuario."""
    from dao.base_dao import BaseDAO
    BaseDAO.execute_query(
        "DELETE FROM notificaciones WHERE id_usuario = %s",
        (session['user_id'],), commit=True
    )
    return jsonify({'ok': True})


# ──────────────────────────────────────────────
# HISTORIAL DE NOTIFICACIONES (USUARIO)
# ──────────────────────────────────────────────
@user_bp.route('/notificaciones/historial')
@login_required
def historial_notificaciones():
    from dao.base_dao import BaseDAO
    user_id     = session['user_id']
    filtro_dia  = request.args.get('dia',  '')
    filtro_mes  = request.args.get('mes',  '')
    filtro_anio = request.args.get('anio', '')
    filtro_tipo = request.args.get('tipo', '')

    where  = ["id_usuario = %s", "(tipo_destinatario IS NULL OR tipo_destinatario = 'usuario')"]
    params = [user_id]
    if filtro_dia:  where.append("DAY(fecha_creacion) = %s");   params.append(filtro_dia)
    if filtro_mes:  where.append("MONTH(fecha_creacion) = %s"); params.append(filtro_mes)
    if filtro_anio: where.append("YEAR(fecha_creacion) = %s");  params.append(filtro_anio)
    if filtro_tipo: where.append("tipo = %s");                  params.append(filtro_tipo)

    # Historial muestra TODO (incluso ocultas) para que el usuario vea su historial completo
    sql = f"""SELECT id_notificacion, tipo, titulo, mensaje, leida, url_accion,
                     DATE_FORMAT(fecha_creacion, '%d/%m/%Y %H:%i') AS fecha_fmt
              FROM notificaciones
              WHERE {' AND '.join(where)}
              ORDER BY fecha_creacion DESC"""

    todas = BaseDAO.execute_query(sql, tuple(params), fetch_all=True) or []

    anios_row = BaseDAO.execute_query(
        "SELECT DISTINCT YEAR(fecha_creacion) AS a FROM notificaciones WHERE id_usuario = %s ORDER BY a DESC",
        (user_id,), fetch_all=True
    ) or []
    anios = [r['a'] for r in anios_row]
    tipos = ['nuevo_ticket', 'asignacion', 'resolucion', 'actualizacion', 'vencido', 'info']

    return render_template('user/historial_notificaciones.html',
                           notificaciones=todas, anios=anios, tipos=tipos,
                           filtro_dia=filtro_dia, filtro_mes=filtro_mes,
                           filtro_anio=filtro_anio, filtro_tipo=filtro_tipo,
                           total=len(todas))