"""
Rutas del administrador - Flask + MySQL
BD: equipos_dif
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash, jsonify,
                   current_app, make_response)
from routes.auth_routes  import admin_required
from dao.usuario_dao     import UsuarioDAO
from dao.ticket_dao      import TicketDAO, HistorialDAO
from dao.equipo_dao      import EquipoDAO
from config.database_mysql import now_mx

admin_bp = Blueprint('admin', __name__)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats             = TicketDAO.obtener_estadisticas()
    tickets_recientes = TicketDAO.obtener_todos()[:10]

    clientes       = UsuarioDAO.obtener_todos()
    tecnicos       = UsuarioDAO.obtener_tecnicos()
    total_usuarios = len(clientes) + len(tecnicos)

    stats_eq      = EquipoDAO.obtener_stats()
    total_equipos = stats_eq['total']

    equipos_por_area = sorted(
        stats_eq['por_area'], key=lambda x: x['cantidad'], reverse=True
    )[:5]
    equipos_por_tipo = sorted(
        stats_eq['por_tipo'], key=lambda x: x['cantidad'], reverse=True
    )

    return render_template('admin/dashboard.html',
                           stats=stats,
                           tickets_recientes=tickets_recientes,
                           total_usuarios=total_usuarios,
                           total_equipos=total_equipos,
                           equipos_por_area=equipos_por_area,
                           equipos_por_tipo=equipos_por_tipo)


# ──────────────────────────────────────────────
# TICKETS
# ──────────────────────────────────────────────
@admin_bp.route('/tickets')
@admin_required
def tickets():
    estado_filtro    = request.args.get('estado', '')
    prioridad_filtro = request.args.get('prioridad', '')

    lista_tickets = TicketDAO.obtener_todos()
    if estado_filtro:
        lista_tickets = [t for t in lista_tickets if t['estado'] == estado_filtro]
    if prioridad_filtro:
        lista_tickets = [t for t in lista_tickets if t['prioridad'] == prioridad_filtro]

    estados     = ['Abierto', 'En Proceso', 'Resuelto', 'Cerrado']
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']

    return render_template('admin/tickets.html',
                           tickets=lista_tickets,
                           estados=estados,
                           prioridades=prioridades,
                           estado_filtro=estado_filtro,
                           prioridad_filtro=prioridad_filtro)


@admin_bp.route('/ticket/<int:id_ticket>')
@admin_required
def ver_ticket(id_ticket):
    ticket = TicketDAO.obtener_por_id(id_ticket)
    if not ticket:
        flash('Ticket no encontrado', 'danger')
        return redirect(url_for('admin.tickets'))

    historial = HistorialDAO.obtener_por_ticket(id_ticket)
    tecnicos  = UsuarioDAO.obtener_tecnicos()
    estados   = ['Abierto', 'En Proceso', 'Resuelto', 'Cerrado']

    return render_template('admin/ver_ticket.html',
                           ticket=ticket,
                           historial=historial,
                           tecnicos=tecnicos,
                           estados=estados)


@admin_bp.route('/ticket/<int:id_ticket>/asignar', methods=['POST'])
@admin_required
def asignar_ticket(id_ticket):
    id_tecnico = request.form.get('id_tecnico')
    if id_tecnico:
        TicketDAO.asignar_tecnico(id_ticket, id_tecnico, session['user_id'])
        try:
            ticket_info = TicketDAO.obtener_por_id(id_ticket)
            email_notif = current_app.extensions.get('email_notif')
            if email_notif and ticket_info:
                email_notif.enviar_ticket_actualizado(ticket_info, ticket_info.get('email_usuario'))
        except Exception as e:
            print(f'[Email] Error: {e}')
        flash('Ticket asignado correctamente', 'success')
    else:
        flash('Debe seleccionar un técnico', 'warning')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


@admin_bp.route('/ticket/<int:id_ticket>/estado', methods=['POST'])
@admin_required
def cambiar_estado(id_ticket):
    estado = request.form.get('id_estado')
    if estado:
        TicketDAO.actualizar_estado(id_ticket, estado, session['user_id'])
        flash('Estado actualizado correctamente', 'success')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


@admin_bp.route('/ticket/<int:id_ticket>/resolver', methods=['POST'])
@admin_required
def resolver_ticket(id_ticket):
    solucion      = request.form.get('solucion')
    observaciones = request.form.get('observaciones')
    if solucion:
        TicketDAO.agregar_solucion(id_ticket, solucion, observaciones, session['user_id'])
        try:
            ticket_info = TicketDAO.obtener_por_id(id_ticket)
            email_notif = current_app.extensions.get('email_notif')
            if email_notif and ticket_info:
                email_notif.enviar_ticket_resuelto(ticket_info, ticket_info.get('email_usuario'))
        except Exception as e:
            print(f'[Email] Error: {e}')
        flash('Solución agregada. Ticket marcado como resuelto.', 'success')
    else:
        flash('Debe agregar una solución', 'warning')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


@admin_bp.route('/ticket/<int:id_ticket>/cerrar', methods=['POST'])
@admin_required
def cerrar_ticket(id_ticket):
    TicketDAO.cerrar_ticket(id_ticket, session['user_id'])
    try:
        ticket_info = TicketDAO.obtener_por_id(id_ticket)
        email_notif = current_app.extensions.get('email_notif')
        if email_notif and ticket_info:
            email_notif.enviar_ticket_cerrado(ticket_info, ticket_info.get('email_usuario'))
    except Exception as e:
        print(f'[Email] Error: {e}')
    flash('Ticket cerrado correctamente', 'success')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


# ──────────────────────────────────────────────
# USUARIOS
# ──────────────────────────────────────────────
@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    clientes = UsuarioDAO.obtener_todos()
    tecnicos = UsuarioDAO.obtener_tecnicos()

    areas = {}
    for c in clientes:
        area = c.get('area') or 'Sin área'
        areas.setdefault(area, []).append(c)

    return render_template('admin/usuarios.html',
                           clientes=clientes,
                           tecnicos=tecnicos,
                           areas=areas,
                           total_clientes=len(clientes),
                           total_tecnicos=len(tecnicos))


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        nombre       = request.form.get('nombre', '').strip()
        email        = request.form.get('email', '').strip().lower()
        password     = request.form.get('password', '').strip()
        departamento = request.form.get('departamento', '').strip()

        if not all([nombre, email, password]):
            flash('Nombre, email y contraseña son obligatorios.', 'warning')
            return redirect(url_for('admin.nuevo_usuario'))

        existente = UsuarioDAO.obtener_por_email(email)
        if existente:
            flash(f'El email {email} ya está registrado.', 'danger')
            return redirect(url_for('admin.nuevo_usuario'))

        ok = UsuarioDAO.crear_usuario(nombre, email, password, departamento)
        if ok:
            flash(f'Usuario {nombre} creado. Credenciales: {email} / {password}', 'success')
            return redirect(url_for('admin.usuarios'))
        else:
            flash('Error al crear el usuario. Intenta de nuevo.', 'danger')

    return render_template('admin/nuevo_usuario.html')


# ──────────────────────────────────────────────
# EQUIPOS
# ──────────────────────────────────────────────
@admin_bp.route('/equipos')
@admin_required
def equipos():
    busqueda    = request.args.get('busqueda', '').strip()
    area_filtro = request.args.get('area', '').strip()
    tipo_filtro = request.args.get('tipo', '').strip()

    lista_equipos = EquipoDAO.buscar(busqueda) if busqueda else EquipoDAO.obtener_todos()

    if area_filtro:
        lista_equipos = [e for e in lista_equipos if e.get('area') == area_filtro]
    if tipo_filtro:
        lista_equipos = [e for e in lista_equipos if e.get('tipo') == tipo_filtro]

    por_area = {}
    for e in lista_equipos:
        area = e.get('area') or 'Sin área'
        por_area.setdefault(area, []).append(e)

    stats_eq    = EquipoDAO.obtener_stats()
    todos       = EquipoDAO.obtener_todos()
    areas_lista = sorted({e.get('area') for e in todos if e.get('area')})
    tipos_lista = EquipoDAO.obtener_tipos()

    return render_template('admin/equipos.html',
                           equipos=lista_equipos,
                           por_area=por_area,
                           stats_tipo=stats_eq['por_tipo'],
                           areas_lista=areas_lista,
                           tipos_lista=tipos_lista,
                           total_equipos=len(lista_equipos),
                           busqueda=busqueda,
                           area_filtro=area_filtro,
                           tipo_filtro=tipo_filtro)


# ──────────────────────────────────────────────
# ESTADÍSTICAS Y REPORTES
# ──────────────────────────────────────────────
@admin_bp.route('/estadisticas')
@admin_required
def estadisticas():
    stats = TicketDAO.obtener_estadisticas()
    return render_template('admin/estadisticas.html', stats=stats)


@admin_bp.route('/api/estadisticas')
@admin_required
def api_estadisticas():
    stats = TicketDAO.obtener_estadisticas()
    return jsonify(stats)


@admin_bp.route('/exportar-reporte/<formato>')
@admin_required
def exportar_reporte(formato):
    from utils.reportes import ReportesManager
    stats         = TicketDAO.obtener_estadisticas()
    lista_tickets = TicketDAO.obtener_todos()
    ahora         = now_mx().strftime("%Y%m%d_%H%M%S")

    if formato == 'txt':
        contenido = ReportesManager.generar_reporte_texto(stats, lista_tickets)
        response  = make_response(contenido)
        response.headers['Content-Type']        = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_{ahora}.txt'
        return response
    elif formato == 'json':
        contenido = ReportesManager.generar_reporte_json(stats, lista_tickets)
        response  = make_response(contenido)
        response.headers['Content-Type']        = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_{ahora}.json'
        return response
    elif formato == 'csv':
        contenido = ReportesManager.generar_reporte_csv(lista_tickets)
        response  = make_response(contenido)
        response.headers['Content-Type']        = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_{ahora}.csv'
        return response
    else:
        flash('Formato no soportado', 'danger')
        return redirect(url_for('admin.estadisticas'))


# ──────────────────────────────────────────────
# PERFIL ADMIN
# ──────────────────────────────────────────────
@admin_bp.route('/perfil', methods=['GET', 'POST'])
@admin_required
def perfil():
    from werkzeug.utils import secure_filename
    import os

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
            return redirect(url_for('admin.perfil'))
        if password_new and len(password_new) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'warning')
            return redirect(url_for('admin.perfil'))

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
            session['user_id'], datos, session.get('rol', 'admin')
        )
        if ok:
            if nombre and apellido:
                session['nombre'] = f"{nombre} {apellido}".strip()
            if email:
                session['email'] = email
            flash('Perfil actualizado correctamente', 'success')
        else:
            flash('Error al actualizar el perfil', 'danger')

        return redirect(url_for('admin.perfil'))

    usuario = UsuarioDAO.obtener_por_id(session['user_id'])
    return render_template('admin/perfil.html', usuario=usuario)