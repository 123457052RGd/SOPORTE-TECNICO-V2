"""
Rutas para usuarios finales - MySQL
BD: equipos_dif
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from routes.auth_routes import login_required
from dao.ticket_dao import TicketDAO, HistorialDAO
from dao.equipo_dao import EquipoDAO
from dao.usuario_dao import UsuarioDAO
from models.models import Ticket
import os

user_bp = Blueprint('user', __name__)


# ─────────────────────────────────────────────────────────────
#  HELPERS DE COLOR
# ─────────────────────────────────────────────────────────────
def _color_prioridad(prioridad):
    return {
        'Baja':     '#43a047',
        'Media':    '#fb8c00',
        'Alta':     '#e53935',
        'Crítica':  '#6a1b9a',
    }.get(prioridad, '#888888')


def _color_estado(estado):
    return {
        'Abierto':    '#fb8c00',
        'En Proceso': '#0288d1',
        'Resuelto':   '#43a047',
        'Cerrado':    '#757575',
    }.get(estado, '#888888')


def _preparar_tickets(tickets):
    """
    Recibe la lista de tickets del DAO y agrega los campos
    color_prioridad, color_estado y normaliza fecha_creacion a string.
    """
    resultado = []
    for t in tickets:
        # Si viene como objeto Row o similar, convertir a dict
        if not isinstance(t, dict):
            t = dict(t)

        # Normalizar fecha a string ISO  "YYYY-MM-DD HH:MM:SS"
        if t.get('fecha_creacion') and not isinstance(t['fecha_creacion'], str):
            t['fecha_creacion'] = str(t['fecha_creacion'])

        t['color_prioridad'] = _color_prioridad(t.get('prioridad', ''))
        t['color_estado']    = _color_estado(t.get('estado', ''))
        resultado.append(t)
    return resultado


# ─────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────
@user_bp.route('/dashboard')
@login_required
def dashboard():
    tickets_raw = TicketDAO.obtener_por_usuario(session['user_id'])
    tickets     = _preparar_tickets(tickets_raw)

    total_tickets     = len(tickets)
    tickets_abiertos  = len([t for t in tickets if t.get('estado') == 'Abierto'])
    tickets_proceso   = len([t for t in tickets if t.get('estado') == 'En Proceso'])
    tickets_resueltos = len([t for t in tickets if t.get('estado') in ['Resuelto', 'Cerrado']])

    equipos_usuario = EquipoDAO.obtener_por_usuario(session['user_id'])
    total_equipos   = len(equipos_usuario)

    return render_template('user/dashboard.html',
                           tickets=tickets,
                           total_tickets=total_tickets,
                           tickets_abiertos=tickets_abiertos,
                           tickets_proceso=tickets_proceso,
                           tickets_resueltos=tickets_resueltos,
                           equipos=equipos_usuario,
                           total_equipos=total_equipos)


# ─────────────────────────────────────────────────────────────
#  NUEVO TICKET
# ─────────────────────────────────────────────────────────────
@user_bp.route('/nuevo-ticket', methods=['GET', 'POST'])
@login_required
def nuevo_ticket():
    if request.method == 'POST':
        titulo           = request.form.get('titulo')
        descripcion      = request.form.get('descripcion')
        id_tipo_problema = request.form.get('id_tipo_problema')
        prioridad        = request.form.get('id_prioridad')
        id_equipo        = request.form.get('id_equipo') or None

        mapa_prioridad = {'1': 'Baja', '2': 'Media', '3': 'Alta', '4': 'Crítica'}
        if prioridad in mapa_prioridad:
            prioridad = mapa_prioridad[prioridad]
        if prioridad not in ('Baja', 'Media', 'Alta', 'Crítica'):
            prioridad = 'Media'

        ticket = Ticket(
            id_usuario=session['user_id'],
            id_equipo=id_equipo,
            id_tipo_problema=id_tipo_problema,
            titulo=titulo,
            descripcion=descripcion,
            id_prioridad=prioridad
        )
        ticket.prioridad = prioridad

        id_nuevo = TicketDAO.crear_ticket(ticket)

        if id_nuevo:
            HistorialDAO.agregar_registro(id_nuevo, session['user_id'],
                                          'Ticket creado', 'Registrado por el usuario')
            try:
                ticket_info = TicketDAO.obtener_por_id(id_nuevo)
                email_notif = current_app.extensions.get('email_notif')
                if email_notif and ticket_info:
                    email_notif.enviar_ticket_creado(ticket_info, session.get('email'))
            except Exception as e:
                print(f'[Email] {e}')

            flash('Ticket creado exitosamente', 'success')
            return redirect(url_for('user.ver_ticket', id_ticket=id_nuevo))
        else:
            flash('Error al crear el ticket', 'danger')

    try:
        from dao.catalogo_dao import CatalogoDAO
        tipos_problema = CatalogoDAO.obtener_tipos_problema()
        prioridades    = CatalogoDAO.obtener_prioridades()
    except Exception:
        tipos_problema = []
        prioridades    = [
            {'id': 1, 'nombre': 'Baja'},
            {'id': 2, 'nombre': 'Media'},
            {'id': 3, 'nombre': 'Alta'},
            {'id': 4, 'nombre': 'Crítica'}
        ]

    equipos = EquipoDAO.obtener_por_usuario(session['user_id'])

    return render_template('user/nuevo_ticket.html',
                           tipos_problema=tipos_problema,
                           prioridades=prioridades,
                           equipos=equipos)


# ─────────────────────────────────────────────────────────────
#  VER TICKET
# ─────────────────────────────────────────────────────────────
@user_bp.route('/ticket/<int:id_ticket>')
@login_required
def ver_ticket(id_ticket):
    ticket_raw = TicketDAO.obtener_por_id(id_ticket)
    if not ticket_raw:
        flash('Ticket no encontrado', 'danger')
        return redirect(url_for('user.dashboard'))

    # Convertir a dict si es necesario
    ticket = dict(ticket_raw) if not isinstance(ticket_raw, dict) else ticket_raw

    ticket_owner = ticket.get('id_usuario')
    if ticket_owner != session['user_id'] and session.get('rol') not in ('admin', 'tecnico', 'jefe'):
        flash('No tienes permiso para ver este ticket', 'danger')
        return redirect(url_for('user.dashboard'))

    # Normalizar fecha y agregar colores
    if ticket.get('fecha_creacion') and not isinstance(ticket['fecha_creacion'], str):
        ticket['fecha_creacion'] = str(ticket['fecha_creacion'])

    ticket['color_prioridad'] = _color_prioridad(ticket.get('prioridad', ''))
    ticket['color_estado']    = _color_estado(ticket.get('estado', ''))

    historial = HistorialDAO.obtener_por_ticket(id_ticket)
    return render_template('user/ver_ticket.html', ticket=ticket, historial=historial)


# ─────────────────────────────────────────────────────────────
#  MIS TICKETS
# ─────────────────────────────────────────────────────────────
@user_bp.route('/mis-tickets')
@login_required
def mis_tickets():
    tickets_raw = TicketDAO.obtener_por_usuario(session['user_id'])
    tickets     = _preparar_tickets(tickets_raw)
    return render_template('user/mis_tickets.html', tickets=tickets)


# ─────────────────────────────────────────────────────────────
#  PERFIL
# ─────────────────────────────────────────────────────────────
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

        datos = {
            'nombre':       nombre,
            'apellido':     apellido,
            'email':        email,
            'telefono':     telefono,
            'area':         area,
            'password_new': password_new or None,
            'foto':         foto_filename
        }

        ok = UsuarioDAO.actualizar_usuario_completo(
            session['user_id'], datos, session.get('rol', 'usuario')
        )
        if ok:
            if nombre:
                session['nombre'] = f"{nombre} {apellido}".strip()
            if email:
                session['email'] = email
            flash('Perfil actualizado correctamente', 'success')
        else:
            flash('Error al actualizar el perfil', 'danger')

        return redirect(url_for('user.perfil'))

    usuario = UsuarioDAO.obtener_por_id(session['user_id'])
    return render_template('user/perfil.html', usuario=usuario)