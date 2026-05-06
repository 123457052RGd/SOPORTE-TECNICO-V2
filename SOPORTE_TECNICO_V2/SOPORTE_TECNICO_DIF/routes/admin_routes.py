"""
    Rutas para administración (dashboard, gestión de tickets, usuarios, equipos, estadísticas)
"""
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash, jsonify,
                   current_app, make_response, Response, stream_with_context)
from routes.auth_routes  import admin_required
from dao.usuario_dao     import UsuarioDAO
from dao.ticket_dao      import TicketDAO, HistorialDAO
from dao.equipo_dao      import EquipoDAO
from dao.base_dao        import BaseDAO
from config.database_mysql import now_mx

admin_bp = Blueprint('admin', __name__)

ROLES_ADMIN = ('admin', 'tecnico', 'jefe')
_COLORES_TEC = ['#0891b2', '#7c3aed', '#d97706', '#059669', '#dc2626', '#0369a1']

AREAS_DIF = [
    'UNIDAD PJC','D.CONTABILIDAD','D.RH','D.ADQUISICIONES',
    'REHABILITACION','ALMACEN','AREA MEDICA','SERVICIOS GENERALES',
    'ADULTO MAYOR','PREVENCION Y VIGILANCIA','SIGNOS VITALES',
    'TRAMITES','PROCURADURIA','D.CONTROL PATRIMONIAL','PEDIATRIA',
    'DIRECCION','RECEPCION','DENTISTA','INFORMATICA','ADMINISTRACION',
]
TIPOS_EQUIPO = [
    'CPU Y MONITOR','LAPTOP','IMPRESORA','MULTIFUNCIONAL',
    'TELEFONO IP','SWITCH','TABLET','SERVIDOR','OTRO',
]


def _obtener_tecnicos_carga():
    rows = BaseDAO.execute_query(
        """SELECT
               tec.id_tecnico,
               CONCAT(tec.nombre,' ',tec.apellido)             AS nombre,
               COUNT(tk.id_ticket)                             AS total,
               COALESCE(SUM(tk.estado IN ('Abierto','En Proceso')),0) AS activos
           FROM tecnicos tec
           LEFT JOIN tickets tk ON tk.id_tecnico = tec.id_tecnico
           WHERE tec.activo = 1
           GROUP BY tec.id_tecnico, tec.nombre, tec.apellido
           ORDER BY activos DESC, total DESC""",
        fetch_all=True
    ) or []
    max_total = max((int(r.get('total') or 0) for r in rows), default=1) or 1
    resultado = []
    for i, r in enumerate(rows):
        total   = int(r.get('total')   or 0)
        activos = int(r.get('activos') or 0)
        nombre  = r.get('nombre', '')
        partes  = nombre.strip().split()
        initials = (partes[0][0]+partes[-1][0]).upper() if len(partes)>=2 else nombre[:2].upper()
        resultado.append({
            'id': r.get('id_tecnico'), 'nombre': nombre, 'initials': initials,
            'color': _COLORES_TEC[i % len(_COLORES_TEC)],
            'total': total, 'activos': activos,
            'pct': round(total/max_total*100) if max_total else 0,
        })
    return resultado


def _extraer_datos_equipo(form):
    def v(c): return form.get(c,'').strip() or None
    return {
        'area': v('area'), 'tipo': v('tipo'),
        'nombre_responsable': (form.get('nombre_responsable','').strip().upper() or None),
        'nombre_usuario': v('nombre_usuario'), 'num_inventario': v('num_inventario'),
        'num_serie': v('num_serie'), 'procesador': v('procesador'),
        'frecuencia': v('frecuencia'), 'ram': v('ram'),
        'tipo_disco': v('tipo_disco'), 'capacidad_disco': v('capacidad_disco'),
        'ip_pc': v('ip_pc'), 'monitor_pulgadas': v('monitor_pulgadas'),
        'serie_monitor': v('serie_monitor'), 'inv_monitor': v('inv_monitor'),
        'telefono': v('telefono'), 'serie_telefono': v('serie_telefono'),
        'ip_telefono': v('ip_telefono'),
        'correo': (form.get('correo','').strip().lower() or None),
    }


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats             = TicketDAO.obtener_estadisticas()
    tickets_recientes = TicketDAO.obtener_todos()[:10]
    clientes          = UsuarioDAO.obtener_todos()
    tecnicos          = UsuarioDAO.obtener_tecnicos()
    total_usuarios    = len(clientes) + len(tecnicos)
    stats_eq          = EquipoDAO.obtener_stats()
    total_equipos     = stats_eq['total']
    equipos_por_area  = []
    for row in sorted(stats_eq.get('por_area',[]), key=lambda x: x.get('cantidad',0), reverse=True)[:5]:
        equipos_por_area.append({
            'area':     row.get('area') or row.get('AREA') or 'Sin área',
            'cantidad': row.get('cantidad', 0),
        })
    tecnicos_carga = _obtener_tecnicos_carga()
    return render_template('admin/dashboard.html',
                           stats=stats, tickets_recientes=tickets_recientes,
                           total_usuarios=total_usuarios, total_equipos=total_equipos,
                           equipos_por_area=equipos_por_area, tecnicos_carga=tecnicos_carga)


# ──────────────────────────────────────────────
# TICKETS
# ──────────────────────────────────────────────
@admin_bp.route('/tickets')
@admin_required
def tickets():
    estado_filtro    = request.args.get('estado', '')
    prioridad_filtro = request.args.get('prioridad', '')
    lista_tickets    = TicketDAO.obtener_todos()
    if estado_filtro:
        lista_tickets = [t for t in lista_tickets if t['estado'] == estado_filtro]
    if prioridad_filtro:
        lista_tickets = [t for t in lista_tickets if t['prioridad'] == prioridad_filtro]
    return render_template('admin/tickets.html',
                           tickets=lista_tickets,
                           estados=['Abierto','En Proceso','Resuelto','Cerrado'],
                           prioridades=['Baja','Media','Alta','Crítica'],
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
    return render_template('admin/ver_ticket.html', ticket=ticket, historial=historial,
                           tecnicos=tecnicos, estados=['Abierto','En Proceso','Resuelto','Cerrado'])


@admin_bp.route('/ticket/<int:id_ticket>/asignar', methods=['POST'])
@admin_required
def asignar_ticket(id_ticket):
    id_tecnico = request.form.get('id_tecnico')
    if id_tecnico:
        TicketDAO.asignar_tecnico(id_ticket, id_tecnico, session['user_id'])
        try:
            ti = TicketDAO.obtener_por_id(id_ticket)
            en = current_app.extensions.get('email_notif')
            if en and ti: en.enviar_ticket_actualizado(ti, ti.get('email_usuario'))
        except Exception as e:
            current_app.logger.warning(f'[Email] {e}')
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
    solucion = request.form.get('solucion')
    obs      = request.form.get('observaciones')
    if solucion:
        TicketDAO.agregar_solucion(id_ticket, solucion, obs, session['user_id'])
        try:
            ti = TicketDAO.obtener_por_id(id_ticket)
            en = current_app.extensions.get('email_notif')
            if en and ti: en.enviar_ticket_resuelto(ti, ti.get('email_usuario'))
        except Exception as e:
            current_app.logger.warning(f'[Email] {e}')
        flash('Solución agregada. Ticket marcado como resuelto.', 'success')
    else:
        flash('Debe agregar una solución', 'warning')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


@admin_bp.route('/ticket/<int:id_ticket>/cerrar', methods=['POST'])
@admin_required
def cerrar_ticket(id_ticket):
    TicketDAO.cerrar_ticket(id_ticket, session['user_id'])
    try:
        ti = TicketDAO.obtener_por_id(id_ticket)
        en = current_app.extensions.get('email_notif')
        if en and ti: en.enviar_ticket_cerrado(ti, ti.get('email_usuario'))
    except Exception as e:
        current_app.logger.warning(f'[Email] {e}')
    flash('Ticket cerrado correctamente', 'success')
    return redirect(url_for('admin.ver_ticket', id_ticket=id_ticket))


# ──────────────────────────────────────────────
# USUARIOS
# ──────────────────────────────────────────────
@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    tecnicos_raw = BaseDAO.execute_query(
        """SELECT id_tecnico AS id_usuario,
                  CONCAT(nombre,' ',apellido) AS nombre_completo,
                  email, area, telefono, rol AS rol_nombre, activo
           FROM tecnicos ORDER BY nombre""",
        fetch_all=True
    ) or []

    clientes_raw = BaseDAO.execute_query(
        """SELECT u.id AS id_usuario,
                  u.nombre AS nombre_completo,
                  u.email, u.area, u.telefono,
                  u.rol AS rol_nombre, u.activo,
                  COUNT(t.id_ticket) AS total_tickets
           FROM usuarios u
           LEFT JOIN tickets t ON t.id_usuario = u.id
           GROUP BY u.id ORDER BY u.nombre""",
        fetch_all=True
    ) or []

    areas = {}
    for c in clientes_raw:
        areas.setdefault(c.get('area') or 'Sin área', []).append(c)

    return render_template('admin/usuarios.html',
                           clientes=clientes_raw,
                           tecnicos=tecnicos_raw,
                           areas=areas,
                           total_clientes=len(clientes_raw),
                           total_tecnicos=len(tecnicos_raw))


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        nombre       = request.form.get('nombre','').strip()
        email        = request.form.get('email','').strip().lower()
        password     = request.form.get('password','').strip()
        departamento = request.form.get('departamento','').strip()
        if not all([nombre, email, password]):
            flash('Nombre, email y contraseña son obligatorios.', 'warning')
            return redirect(url_for('admin.nuevo_usuario'))
        if UsuarioDAO.obtener_por_email(email):
            flash(f'El email {email} ya está registrado.', 'danger')
            return redirect(url_for('admin.nuevo_usuario'))
        ok = UsuarioDAO.crear_usuario(nombre, email, password, departamento)
        if ok:
            flash(f'Usuario {nombre} creado. Credenciales: {email} / {password}', 'success')
            return redirect(url_for('admin.usuarios'))
        flash('Error al crear el usuario.', 'danger')
    return render_template('admin/nuevo_usuario.html')


@admin_bp.route('/usuarios/<int:id_usuario>/editar', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id_usuario):
    usuario = UsuarioDAO.obtener_por_id(id_usuario)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('admin.usuarios'))

    if request.method == 'POST':
        from werkzeug.security import generate_password_hash
        nombre       = request.form.get('nombre', '').strip()
        apellido     = request.form.get('apellido', '').strip()
        email        = request.form.get('email', '').strip().lower()
        area         = request.form.get('area', '').strip()
        telefono     = request.form.get('telefono', '').strip()
        rol          = request.form.get('rol', '').strip()
        activo       = int(request.form.get('activo', 1))
        password_new = request.form.get('password_new', '').strip()

        if not nombre or not email:
            flash('Nombre y correo son obligatorios.', 'warning')
            return render_template('admin/editar_usuario.html', usuario=usuario, areas=AREAS_DIF)

        datos = {
            'nombre':       nombre,
            'apellido':     apellido,
            'email':        email,
            'area':         area,
            'telefono':     telefono or None,
            'rol':          rol,
            'activo':       activo,
            'password_new': password_new or None,
        }
        ok = UsuarioDAO.actualizar_usuario_completo(id_usuario, datos, rol_sesion='admin')
        if ok:
            flash(f'Usuario {nombre} actualizado correctamente.', 'success')
        else:
            flash('Error al actualizar el usuario.', 'danger')
        return redirect(url_for('admin.usuarios'))

    return render_template('admin/editar_usuario.html', usuario=usuario, areas=AREAS_DIF)


@admin_bp.route('/usuarios/<int:id_usuario>/eliminar', methods=['POST'])
@admin_required
def eliminar_usuario(id_usuario):
    if id_usuario == session.get('user_id'):
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('admin.usuarios'))

    usuario = UsuarioDAO.obtener_por_id(id_usuario)
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('admin.usuarios'))

    activos = BaseDAO.execute_query(
        "SELECT COUNT(*) AS c FROM tickets WHERE id_usuario = %s AND estado IN ('Abierto','En Proceso')",
        (id_usuario,), fetch_one=True
    )
    if activos and activos['c'] > 0:
        flash(f'No se puede eliminar: tiene {activos["c"]} ticket(s) activo(s).', 'danger')
        return redirect(url_for('admin.usuarios'))

    es_tecnico = (usuario.get('rol_nombre') or '').lower() in ('admin','tecnico','jefe')
    if es_tecnico:
        BaseDAO.execute_query('DELETE FROM tecnicos WHERE id_tecnico = %s', (id_usuario,), commit=True)
    else:
        BaseDAO.execute_query('DELETE FROM usuarios WHERE id = %s', (id_usuario,), commit=True)

    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('admin.usuarios'))


@admin_bp.route('/usuarios/<int:id_usuario>/toggle-activo', methods=['POST'])
@admin_required
def toggle_activo_usuario(id_usuario):
    if id_usuario == session.get('user_id'):
        return jsonify({'ok': False, 'error': 'No puedes desactivarte a ti mismo'})

    usuario = UsuarioDAO.obtener_por_id(id_usuario)
    if not usuario:
        return jsonify({'ok': False, 'error': 'No encontrado'})

    nuevo = 0 if usuario.get('activo') else 1
    es_tecnico = (usuario.get('rol_nombre') or '').lower() in ('admin','tecnico','jefe')
    tabla = 'tecnicos' if es_tecnico else 'usuarios'
    pk    = 'id_tecnico' if es_tecnico else 'id'
    BaseDAO.execute_query(
        f'UPDATE {tabla} SET activo = %s WHERE {pk} = %s',
        (nuevo, id_usuario), commit=True
    )
    return jsonify({'ok': True, 'activo': nuevo})


# ──────────────────────────────────────────────
# EQUIPOS
# ──────────────────────────────────────────────
@admin_bp.route('/equipos')
@admin_required
def equipos():
    busqueda    = request.args.get('busqueda','').strip()
    area_filtro = request.args.get('area','').strip()
    tipo_filtro = request.args.get('tipo','').strip()
    lista_equipos = EquipoDAO.buscar(busqueda) if busqueda else EquipoDAO.obtener_todos()
    if area_filtro: lista_equipos = [e for e in lista_equipos if e.get('area') == area_filtro]
    if tipo_filtro: lista_equipos = [e for e in lista_equipos if e.get('tipo') == tipo_filtro]
    por_area = {}
    for e in lista_equipos:
        por_area.setdefault(e.get('area') or 'Sin área', []).append(e)
    stats_eq    = EquipoDAO.obtener_stats()
    todos       = EquipoDAO.obtener_todos()
    areas_lista = sorted({e.get('area') for e in todos if e.get('area')})
    tipos_lista = EquipoDAO.obtener_tipos()
    stats_tipo  = [{'TIPO': r.get('TIPO') or r.get('tipo') or 'Sin tipo',
                    'cantidad': r.get('cantidad',0)} for r in stats_eq.get('por_tipo',[])]
    return render_template('admin/equipos.html', equipos=lista_equipos, por_area=por_area,
                        stats_tipo=stats_tipo, areas_lista=areas_lista,
                        tipos_lista=tipos_lista, total_equipos=len(lista_equipos),
                        busqueda=busqueda, area_filtro=area_filtro, tipo_filtro=tipo_filtro)


@admin_bp.route('/equipos/nuevo', methods=['GET', 'POST'])
@admin_required
def nuevo_equipo():
    if request.method == 'POST':
        datos = _extraer_datos_equipo(request.form)
        if not datos['area'] or not datos['tipo'] or not datos['nombre_responsable']:
            flash('Área, tipo y nombre del responsable son obligatorios.', 'warning')
            return render_template('admin/nuevo_equipo.html',
                                equipo=None, areas=AREAS_DIF, tipos=TIPOS_EQUIPO)
        id_nuevo = EquipoDAO.crear_equipo(datos)
        if id_nuevo:
            flash('Equipo dado de alta correctamente', 'success')
            return redirect(url_for('admin.equipos'))
        flash('Error al dar de alta el equipo.', 'danger')
    return render_template('admin/nuevo_equipo.html',
                           equipo=None, areas=AREAS_DIF, tipos=TIPOS_EQUIPO)


@admin_bp.route('/equipos/<int:id_equipo>/editar', methods=['GET', 'POST'])
@admin_required
def editar_equipo(id_equipo):
    equipo = EquipoDAO.obtener_por_id(id_equipo)
    if not equipo:
        flash('Equipo no encontrado', 'danger')
        return redirect(url_for('admin.equipos'))
    if request.method == 'POST':
        if EquipoDAO.actualizar_equipo(id_equipo, _extraer_datos_equipo(request.form)):
            flash('Equipo actualizado correctamente', 'success')
            return redirect(url_for('admin.equipos'))
        flash('Error al actualizar el equipo', 'danger')
    return render_template('admin/nuevo_equipo.html',
                           equipo=equipo, areas=AREAS_DIF, tipos=TIPOS_EQUIPO)


@admin_bp.route('/equipos/<int:id_equipo>/eliminar', methods=['POST'])
@admin_required
def eliminar_equipo(id_equipo):
    if EquipoDAO.eliminar_equipo(id_equipo):
        flash('Equipo eliminado correctamente', 'success')
    else:
        flash('Error al eliminar el equipo', 'danger')
    return redirect(url_for('admin.equipos'))


# ──────────────────────────────────────────────
# ESTADÍSTICAS
# ──────────────────────────────────────────────
@admin_bp.route('/estadisticas')
@admin_required
def estadisticas():
    return render_template('admin/estadisticas.html', stats=TicketDAO.obtener_estadisticas())


@admin_bp.route('/api/estadisticas')
@admin_required
def api_estadisticas():
    return jsonify(TicketDAO.obtener_estadisticas())


# ──────────────────────────────────────────────
# EXPORTAR REPORTE  (CSV / PDF / Word)
# URL: /admin/exportar-reporte/csv
#      /admin/exportar-reporte/csv?periodo=hoy
#      /admin/exportar-reporte/pdf?periodo=semana
#      /admin/exportar-reporte/word?periodo=mes
#      /admin/exportar-reporte/word?periodo=año
# ──────────────────────────────────────────────
@admin_bp.route('/exportar-reporte/<formato>')
@admin_required
def exportar_reporte(formato):
    from utils.reportes_pdf import ReportesManager   # import directo — sin pasar por reportes.py

    # Período opcional via query string
    periodo = request.args.get('periodo') or None
    if periodo not in {None, 'hoy', 'semana', 'mes', 'año'}:
        periodo = None

    ahora    = now_mx().strftime("%Y%m%d_%H%M%S")
    etiqueta = periodo or 'todos'
    stats    = TicketDAO.obtener_estadisticas(periodo=periodo)
    lista    = TicketDAO.obtener_todos(periodo=periodo)

    if formato == 'csv':
        contenido = ReportesManager.generar_reporte_csv(lista)
        return Response(
            stream_with_context(iter([contenido])),
            mimetype='text/csv; charset=utf-8-sig',
            headers={'Content-Disposition': f'attachment; filename=tickets_{etiqueta}_{ahora}.csv'}
        )

    elif formato == 'pdf':
        html_str = ReportesManager.generar_reporte_pdf(stats, lista)
        r = make_response(html_str)
        r.headers['Content-Type'] = 'text/html; charset=utf-8'
        return r

    elif formato == 'word':
        try:
            docx_bytes = ReportesManager.generar_reporte_word(stats, lista)
            r = make_response(docx_bytes)
            r.headers['Content-Type'] = (
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            r.headers['Content-Disposition'] = (
                f'attachment; filename=reporte_{etiqueta}_{ahora}.docx'
            )
            return r
        except Exception as e:
            flash(f'Error al generar Word: {e}', 'danger')
            return redirect(url_for('admin.estadisticas'))

    flash('Formato no soportado', 'danger')
    return redirect(url_for('admin.estadisticas'))


# ──────────────────────────────────────────────
# NOTIFICACIONES ADMIN
# ──────────────────────────────────────────────
@admin_bp.route('/api/notificaciones')
@admin_required
def api_notificaciones():
    user_id = session.get('user_id')
    rows = BaseDAO.execute_query(
        """SELECT id_notificacion, tipo, titulo, mensaje, leida, url_accion,
                  DATE_FORMAT(fecha_creacion, '%d/%m/%Y %H:%i') AS fecha_fmt
           FROM notificaciones
           WHERE id_usuario = %s AND oculta = 0
           ORDER BY fecha_creacion DESC
           LIMIT 5""",
        (user_id,), fetch_all=True
    ) or []
    no_leidas = sum(1 for r in rows if not r.get('leida'))
    return jsonify({'notificaciones': rows, 'no_leidas': no_leidas})


@admin_bp.route('/api/notificaciones/marcar-leidas', methods=['POST'])
@admin_required
def marcar_notificaciones_leidas():
    user_id = session.get('user_id')
    BaseDAO.execute_query(
        "UPDATE notificaciones SET leida = 1 WHERE id_usuario = %s AND leida = 0",
        (user_id,), commit=True
    )
    return jsonify({"ok": True})


@admin_bp.route('/api/notificaciones/borrar-todas', methods=['POST'])
@admin_required
def borrar_todas_notificaciones():
    user_id = session.get('user_id')
    BaseDAO.execute_query(
        "DELETE FROM notificaciones WHERE id_usuario = %s",
        (user_id,), commit=True
    )
    return jsonify({"ok": True})


@admin_bp.route('/api/notificaciones/<int:id_notif>/ocultar', methods=['POST'])
@admin_required
def ocultar_notificacion(id_notif):
    user_id = session.get('user_id')
    BaseDAO.execute_query(
        "UPDATE notificaciones SET oculta = 1 WHERE id_notificacion = %s AND id_usuario = %s",
        (id_notif, user_id), commit=True
    )
    return jsonify({"ok": True})


# ──────────────────────────────────────────────
# HISTORIAL DE NOTIFICACIONES (AUDITORÍA)
# ──────────────────────────────────────────────
@admin_bp.route('/notificaciones/historial')
@admin_required
def historial_notificaciones():
    user_id     = session.get('user_id')
    filtro_dia  = request.args.get('dia',  '')
    filtro_mes  = request.args.get('mes',  '')
    filtro_anio = request.args.get('anio', '')
    filtro_tipo = request.args.get('tipo', '')

    where  = ["id_usuario = %s"]
    params = [user_id]
    if filtro_dia:  where.append("DAY(fecha_creacion) = %s");   params.append(filtro_dia)
    if filtro_mes:  where.append("MONTH(fecha_creacion) = %s"); params.append(filtro_mes)
    if filtro_anio: where.append("YEAR(fecha_creacion) = %s");  params.append(filtro_anio)
    if filtro_tipo: where.append("tipo = %s");                  params.append(filtro_tipo)

    sql = f"""SELECT id_notificacion, tipo, titulo, mensaje, leida, oculta, url_accion,
                     DATE_FORMAT(fecha_creacion, '%d/%m/%Y %H:%i') AS fecha_fmt,
                     YEAR(fecha_creacion)  AS anio,
                     MONTH(fecha_creacion) AS mes,
                     DAY(fecha_creacion)   AS dia
              FROM notificaciones
              WHERE {' AND '.join(where)}
              ORDER BY fecha_creacion DESC"""

    todas = BaseDAO.execute_query(sql, tuple(params), fetch_all=True) or []

    anios_row = BaseDAO.execute_query(
        "SELECT DISTINCT YEAR(fecha_creacion) AS a FROM notificaciones WHERE id_usuario = %s ORDER BY a DESC",
        (user_id,), fetch_all=True
    ) or []
    anios = [r['a'] for r in anios_row]
    tipos = ['nuevo_ticket','asignacion','resolucion','actualizacion','vencido','info']

    return render_template('admin/historial_notificaciones.html',
                           notificaciones=todas, anios=anios, tipos=tipos,
                           filtro_dia=filtro_dia, filtro_mes=filtro_mes,
                           filtro_anio=filtro_anio, filtro_tipo=filtro_tipo,
                           total=len(todas))


# ──────────────────────────────────────────────
# PERFIL ADMIN
# ──────────────────────────────────────────────
@admin_bp.route('/perfil', methods=['GET', 'POST'])
@admin_required
def perfil():
    from werkzeug.utils import secure_filename
    import os
    ALLOWED = {'png','jpg','jpeg','gif','webp'}
    if request.method == 'POST':
        nombre        = request.form.get('nombre','').strip()
        apellido      = request.form.get('apellido','').strip()
        email         = request.form.get('email','').strip().lower()
        telefono      = request.form.get('telefono','').strip()
        area          = request.form.get('area','').strip()
        password_new  = request.form.get('password_new','').strip()
        password_conf = request.form.get('password_confirm','').strip()
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
                ext = foto.filename.rsplit('.',1)[-1].lower()
                if ext in ALLOWED:
                    fn = secure_filename(f"perfil_{session['user_id']}.{ext}")
                    carpeta = current_app.config.get('UPLOAD_FOLDER','static/uploads')
                    os.makedirs(carpeta, exist_ok=True)
                    ruta = os.path.join(carpeta, fn)
                    foto.save(ruta)
                    if os.path.exists(ruta):
                        foto_filename = fn
        rol_nuevo = request.form.get('rol', '').strip()
        datos = {'nombre':nombre,'apellido':apellido,'email':email,'telefono':telefono,
                 'area':area,'password_new':password_new or None,'foto':foto_filename,
                 'rol': rol_nuevo or None}
        ok = UsuarioDAO.actualizar_usuario_completo(session['user_id'], datos, session.get('rol','admin'))
        if ok and rol_nuevo and rol_nuevo != session.get('rol'):
            session['rol'] = rol_nuevo
            session.modified = True
        if ok:
            if nombre: session['nombre'] = f"{nombre} {apellido}".strip()
            if email:  session['email']  = email
            if foto_filename: session['foto'] = foto_filename
            session.modified = True
            flash('Perfil actualizado correctamente', 'success')
        else:
            flash('Error al actualizar el perfil', 'danger')
        return redirect(url_for('admin.perfil'))
    usuario = UsuarioDAO.obtener_por_id(session["user_id"], rol=session.get("rol"))
    return render_template('admin/perfil.html', usuario=usuario)