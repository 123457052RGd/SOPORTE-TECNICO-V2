"""
DAO para gestión de tickets - MySQL
BD: equipos_dif

FIXES:
  - _notif con id_usuario=None ahora notifica a TODOS los técnicos/admins activos
    en lugar de insertar una fila con NULL (que nadie recibe con polling por user_id)
  - asignar_tecnico: refresca el ticket DESPUÉS del UPDATE para tener nombre_tecnico correcto
  - Notificaciones al usuario usan url correcta /user/ticket/ (no /mis-tickets/)
"""
from dao.base_dao import BaseDAO
from config.database_mysql import now_mx


# ──────────────────────────────────────────────
# HELPER INTERNO: insertar notificación
# ──────────────────────────────────────────────
def _notif(titulo, mensaje, tipo='info', id_usuario=None, url=None, id_ticket=None):
    """
    FIX: Si id_usuario=None → notifica a TODOS los técnicos activos
         (antes insertaba NULL y nadie lo recibía en el polling por user_id)
    Si id_usuario=int → solo para ese usuario
    """
    try:
        if id_usuario is None:
            # Notificar a todos los técnicos/admins activos
            tecnicos = BaseDAO.execute_query(
                "SELECT id_tecnico FROM tecnicos WHERE activo = 1",
                fetch_all=True
            ) or []
            for tec in tecnicos:
                BaseDAO.execute_query(
                    """INSERT INTO notificaciones
                           (id_ticket, id_usuario, tipo, titulo, mensaje, leida, url_accion, fecha_creacion)
                       VALUES (%s, %s, %s, %s, %s, 0, %s, %s)""",
                    (id_ticket, tec['id_tecnico'], tipo, titulo, mensaje, url, now_mx()),
                    commit=True
                )
        else:
            BaseDAO.execute_query(
                """INSERT INTO notificaciones
                       (id_ticket, id_usuario, tipo, titulo, mensaje, leida, url_accion, fecha_creacion)
                   VALUES (%s, %s, %s, %s, %s, 0, %s, %s)""",
                (id_ticket, id_usuario, tipo, titulo, mensaje, url, now_mx()),
                commit=True
            )
    except Exception as e:
        print(f'[Notif] Error al insertar: {e}')


class TicketDAO(BaseDAO):

    @staticmethod
    def generar_folio():
        result = BaseDAO.execute_query(
            'SELECT COUNT(*) AS total FROM tickets', fetch_one=True
        )
        total = result['total'] if result else 0
        return f"TKT-{now_mx().strftime('%Y%m%d')}-{str(total + 1).zfill(4)}"

    @staticmethod
    def crear_ticket(ticket):
        folio = TicketDAO.generar_folio()
        result = BaseDAO.execute_query(
            """INSERT INTO tickets
               (folio, id_usuario, id_equipo, id_tipo_problema,
                titulo, descripcion, prioridad, estado, fecha_creacion)
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'Abierto', %s)""",
            (
                folio,
                ticket.id_usuario,
                ticket.id_equipo if ticket.id_equipo else None,
                ticket.id_tipo_problema,
                ticket.titulo,
                ticket.descripcion,
                getattr(ticket, 'prioridad', 'Media'),
                now_mx()
            ),
            commit=True
        )
        if result:
            row = BaseDAO.execute_query(
                'SELECT id_ticket FROM tickets WHERE folio = %s', (folio,), fetch_one=True
            )
            id_ticket = row['id_ticket'] if row else None
            if id_ticket:
                # FIX: id_usuario=None → llega a TODOS los técnicos
                _notif(
                    titulo=f'Nuevo ticket {folio}',
                    mensaje=f'Se creó un nuevo ticket de soporte: {ticket.titulo[:80]}',
                    tipo='nuevo_ticket',
                    id_usuario=None,
                    url=f'/admin/ticket/{id_ticket}',
                    id_ticket=id_ticket
                )
            return id_ticket
        return None

    @staticmethod
    def obtener_por_id(id_ticket):
        row = BaseDAO.execute_query(
            """SELECT t.*,
                      u.nombre AS nombre_usuario,
                      u.area   AS area_usuario,
                      u.email  AS email_usuario,
                      CONCAT(tec.nombre,' ',tec.apellido) AS nombre_tecnico
               FROM tickets t
               LEFT JOIN usuarios  u   ON t.id_usuario = u.id
               LEFT JOIN tecnicos  tec ON t.id_tecnico  = tec.id_tecnico
               WHERE t.id_ticket = %s""",
            (id_ticket,), fetch_one=True
        )
        if row:
            colores_estado    = {'Abierto':'#3b82f6','En Proceso':'#f59e0b','Resuelto':'#22c55e','Cerrado':'#94a3b8'}
            colores_prioridad = {'Baja':'#22c55e','Media':'#f59e0b','Alta':'#f97316','Crítica':'#ef4444'}
            row['color_estado']    = colores_estado.get(row.get('estado', ''), '#94a3b8')
            row['color_prioridad'] = colores_prioridad.get(row.get('prioridad', ''), '#94a3b8')
            row['fecha_creacion']  = str(row.get('fecha_creacion', ''))
            row['nombre_tecnico']  = row.get('nombre_tecnico') or None
            row['id_tecnico']      = row.get('id_tecnico') or None
        return row

    @staticmethod
    def obtener_todos():
        rows = BaseDAO.execute_query(
            """SELECT t.*,
                      u.nombre AS nombre_usuario,
                      u.area   AS area_usuario,
                      CONCAT(tec.nombre,' ',tec.apellido) AS nombre_tecnico
               FROM tickets t
               LEFT JOIN usuarios  u   ON t.id_usuario = u.id
               LEFT JOIN tecnicos  tec ON t.id_tecnico  = tec.id_tecnico
               ORDER BY t.fecha_creacion DESC""",
            fetch_all=True
        ) or []
        colores_estado    = {'Abierto':'#3b82f6','En Proceso':'#f59e0b','Resuelto':'#22c55e','Cerrado':'#94a3b8'}
        colores_prioridad = {'Baja':'#22c55e','Media':'#f59e0b','Alta':'#f97316','Crítica':'#ef4444'}
        for r in rows:
            r['color_estado']    = colores_estado.get(r.get('estado', ''), '#94a3b8')
            r['color_prioridad'] = colores_prioridad.get(r.get('prioridad', ''), '#94a3b8')
            r['fecha_creacion']  = str(r.get('fecha_creacion', ''))
        return rows

    @staticmethod
    def obtener_por_usuario(id_usuario):
        rows = BaseDAO.execute_query(
            """SELECT t.*,
                      CONCAT(tec.nombre,' ',tec.apellido) AS nombre_tecnico
               FROM tickets t
               LEFT JOIN tecnicos tec ON t.id_tecnico = tec.id_tecnico
               WHERE t.id_usuario = %s
               ORDER BY t.fecha_creacion DESC""",
            (id_usuario,), fetch_all=True
        ) or []
        colores_estado    = {'Abierto':'#3b82f6','En Proceso':'#f59e0b','Resuelto':'#22c55e','Cerrado':'#94a3b8'}
        colores_prioridad = {'Baja':'#22c55e','Media':'#f59e0b','Alta':'#f97316','Crítica':'#ef4444'}
        for r in rows:
            r['color_estado']    = colores_estado.get(r.get('estado', ''), '#94a3b8')
            r['color_prioridad'] = colores_prioridad.get(r.get('prioridad', ''), '#94a3b8')
            r['fecha_creacion']  = str(r.get('fecha_creacion', ''))
        return rows

    @staticmethod
    def actualizar_estado(id_ticket, estado, id_usuario):
        BaseDAO.execute_query(
            'UPDATE tickets SET estado = %s WHERE id_ticket = %s',
            (estado, id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Cambio de estado', f'Estado: {estado}')

        # FIX: refrescar ticket DESPUÉS del UPDATE para datos actualizados
        ticket = TicketDAO.obtener_por_id(id_ticket)
        if ticket:
            # Notificación a todos los técnicos
            _notif(
                titulo=f'Estado actualizado — {ticket.get("folio","")}',
                mensaje=f'{ticket.get("titulo","")[:60]}. Estado: {estado}',
                tipo='actualizacion',
                id_usuario=None,
                url=f'/admin/ticket/{id_ticket}',
                id_ticket=id_ticket
            )
            # Notificación al usuario dueño del ticket
            if ticket.get('id_usuario'):
                _notif(
                    titulo=f'Tu ticket {ticket.get("folio","")} fue actualizado',
                    mensaje=f'El estado de tu ticket cambio a: {estado}',
                    tipo='actualizacion',
                    id_usuario=ticket['id_usuario'],
                    url=f'/user/ticket/{id_ticket}',   # FIX: url correcta
                    id_ticket=id_ticket
                )
        return True

    @staticmethod
    def asignar_tecnico(id_ticket, id_tecnico, id_usuario):
        BaseDAO.execute_query(
            """UPDATE tickets
               SET id_tecnico = %s, estado = 'En Proceso', fecha_asignacion = %s
               WHERE id_ticket = %s""",
            (id_tecnico, now_mx(), id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Asignación', 'Técnico asignado')

        # FIX: obtener ticket DESPUÉS del UPDATE — así nombre_tecnico ya está actualizado
        ticket = TicketDAO.obtener_por_id(id_ticket)
        if ticket:
            nombre_tec = ticket.get('nombre_tecnico') or 'técnico'
            # Notif a todos los técnicos (panel admin)
            _notif(
                titulo=f'Ticket asignado - {ticket.get("folio","")}',
                mensaje=f'{ticket.get("titulo","")[:60]} asignado a {nombre_tec}',
                tipo='asignacion',
                id_usuario=None,
                url=f'/admin/ticket/{id_ticket}',
                id_ticket=id_ticket
            )
            # Notif al usuario dueño
            if ticket.get('id_usuario'):
                _notif(
                    titulo=f'Tu ticket {ticket.get("folio","")} fue asignado',
                    mensaje=f'El técnico {nombre_tec} atenderá tu solicitud',
                    tipo='asignacion',
                    id_usuario=ticket['id_usuario'],
                    url=f'/user/ticket/{id_ticket}',   # FIX: url correcta
                    id_ticket=id_ticket
                )
        return True

    @staticmethod
    def agregar_solucion(id_ticket, solucion, observaciones, id_usuario):
        BaseDAO.execute_query(
            """UPDATE tickets
               SET solucion = %s, observaciones_tecnico = %s,
                   estado = 'Resuelto', fecha_resolucion = %s
               WHERE id_ticket = %s""",
            (solucion, observaciones or '', now_mx(), id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Resuelto', 'Solución agregada')

        ticket = TicketDAO.obtener_por_id(id_ticket)
        if ticket:
            _notif(
                titulo=f'Ticket resuelto - {ticket.get("folio","")}',
                mensaje=f'{ticket.get("titulo","")[:60]} fue marcado como Resuelto',
                tipo='resolucion',
                id_usuario=None,
                url=f'/admin/ticket/{id_ticket}',
                id_ticket=id_ticket
            )
            if ticket.get('id_usuario'):
                _notif(
                    titulo=f'Tu ticket {ticket.get("folio","")} fue resuelto',
                    mensaje='Solución aplicada correctamente.',
                    tipo='resolucion',
                    id_usuario=ticket['id_usuario'],
                    url=f'/user/ticket/{id_ticket}',   # FIX: url correcta
                    id_ticket=id_ticket
                )
        return True

    @staticmethod
    def cerrar_ticket(id_ticket, id_usuario):
        BaseDAO.execute_query(
            "UPDATE tickets SET estado = 'Cerrado', fecha_cierre = %s WHERE id_ticket = %s",
            (now_mx(), id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Cerrado', 'Ticket cerrado')

        ticket = TicketDAO.obtener_por_id(id_ticket)
        if ticket:
            _notif(
                titulo=f'Ticket cerrado - {ticket.get("folio","")}',
                mensaje=f'{ticket.get("titulo","")[:60]} fue cerrado',
                tipo='actualizacion',
                id_usuario=None,
                url=f'/admin/ticket/{id_ticket}',
                id_ticket=id_ticket
            )
            if ticket.get('id_usuario'):
                _notif(
                    titulo=f'Tu ticket {ticket.get("folio","")} fue cerrado',
                    mensaje='El ticket ha sido cerrado. Si necesitas más ayuda, crea uno nuevo.',
                    tipo='actualizacion',
                    id_usuario=ticket['id_usuario'],
                    url=f'/user/ticket/{id_ticket}',   # FIX: url correcta
                    id_ticket=id_ticket
                )
        return True

    @staticmethod
    def obtener_estadisticas():
        stats = {}

        r = BaseDAO.execute_query('SELECT COUNT(*) AS total FROM tickets', fetch_one=True)
        stats['total'] = r['total'] if r else 0

        estados_raw = BaseDAO.execute_query(
            """SELECT estado AS nombre, COUNT(*) AS cantidad FROM tickets
               GROUP BY estado
               ORDER BY FIELD(estado,'Abierto','En Proceso','Resuelto','Cerrado')""",
            fetch_all=True
        ) or []
        colores_estado = {
            'Abierto':    '#3b82f6',
            'En Proceso': '#f59e0b',
            'Resuelto':   '#22c55e',
            'Cerrado':    '#94a3b8'
        }
        for e in estados_raw:
            e['color'] = colores_estado.get(e['nombre'], '#94a3b8')
        stats['por_estado'] = estados_raw

        prioridades_raw = BaseDAO.execute_query(
            """SELECT prioridad AS nombre, COUNT(*) AS cantidad FROM tickets
               GROUP BY prioridad
               ORDER BY FIELD(prioridad,'Baja','Media','Alta','Crítica')""",
            fetch_all=True
        ) or []
        colores_prioridad = {
            'Baja':    '#22c55e',
            'Media':   '#f59e0b',
            'Alta':    '#f97316',
            'Crítica': '#ef4444'
        }
        for p in prioridades_raw:
            p['color'] = colores_prioridad.get(p['nombre'], '#94a3b8')
        stats['por_prioridad'] = prioridades_raw

        por_tipo = BaseDAO.execute_query(
            """SELECT
                 COALESCE(tp.nombre, CONCAT('Tipo #', t.id_tipo_problema)) AS nombre,
                 COUNT(*) AS cantidad
               FROM tickets t
               LEFT JOIN tipos_problema tp ON t.id_tipo_problema = tp.id_tipo
               WHERE t.id_tipo_problema IS NOT NULL
               GROUP BY t.id_tipo_problema, tp.nombre
               ORDER BY cantidad DESC
               LIMIT 10""",
            fetch_all=True
        )
        if por_tipo is None:
            por_tipo = BaseDAO.execute_query(
                """SELECT id_tipo_problema AS nombre, COUNT(*) AS cantidad
                   FROM tickets WHERE id_tipo_problema IS NOT NULL
                   GROUP BY id_tipo_problema ORDER BY cantidad DESC LIMIT 10""",
                fetch_all=True
            ) or []
            for p in por_tipo:
                v = p.get('nombre')
                if isinstance(v, int) or (isinstance(v, str) and v.isdigit()):
                    p['nombre'] = f'Tipo #{v}'

        stats['por_tipo'] = por_tipo or []
        return stats


# ──────────────────────────────────────────────
# HISTORIAL DAO
# ──────────────────────────────────────────────
class HistorialDAO(BaseDAO):

    @staticmethod
    def agregar_registro(id_ticket, id_usuario, accion, descripcion=''):
        try:
            tec = BaseDAO.execute_query(
                'SELECT CONCAT(nombre," ",apellido) AS n FROM tecnicos WHERE id_tecnico = %s',
                (id_usuario,), fetch_one=True
            )
            if tec:
                nombre = tec['n']
            else:
                usr = BaseDAO.execute_query(
                    'SELECT nombre AS n FROM usuarios WHERE id = %s',
                    (id_usuario,), fetch_one=True
                )
                nombre = usr['n'] if usr else 'Sistema'

            BaseDAO.execute_query(
                """INSERT INTO ticket_historial
                   (id_ticket, accion, descripcion, usuario, fecha)
                   VALUES (%s, %s, %s, %s, %s)""",
                (id_ticket, accion, descripcion, nombre, now_mx()),
                commit=True
            )
        except Exception as e:
            print(f'[HistorialDAO] Error: {e}')

    @staticmethod
    def obtener_por_ticket(id_ticket):
        rows = BaseDAO.execute_query(
            'SELECT * FROM ticket_historial WHERE id_ticket = %s ORDER BY fecha DESC',
            (id_ticket,), fetch_all=True
        ) or []
        for r in rows:
            r['nombre_completo'] = r.get('usuario', 'Sistema')
            r['fecha'] = str(r.get('fecha', ''))
        return rows