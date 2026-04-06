"""
DAO para gestión de tickets - MySQL
BD: equipos_dif | Tabla: tickets (se crea si no existe)
"""
from dao.base_dao import BaseDAO
from config.database_mysql import now_mx


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
        # Devolver el id insertado
        if result:
            row = BaseDAO.execute_query(
                'SELECT id_ticket FROM tickets WHERE folio = %s', (folio,), fetch_one=True
            )
            return row['id_ticket'] if row else None
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
            colores_estado    = {'Abierto':'#ffc107','En Proceso':'#17a2b8','Resuelto':'#28a745','Cerrado':'#6c757d'}
            colores_prioridad = {'Baja':'#28a745','Media':'#ffc107','Alta':'#fd7e14','Crítica':'#dc3545'}
            row['color_estado']    = colores_estado.get(row.get('estado',''),'#999')
            row['color_prioridad'] = colores_prioridad.get(row.get('prioridad',''),'#999')
            row['fecha_creacion']  = str(row.get('fecha_creacion',''))
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
        colores_estado    = {'Abierto':'#ffc107','En Proceso':'#17a2b8','Resuelto':'#28a745','Cerrado':'#6c757d'}
        colores_prioridad = {'Baja':'#28a745','Media':'#ffc107','Alta':'#fd7e14','Crítica':'#dc3545'}
        for r in rows:
            r['color_estado']    = colores_estado.get(r.get('estado',''),'#999')
            r['color_prioridad'] = colores_prioridad.get(r.get('prioridad',''),'#999')
            r['fecha_creacion']  = str(r.get('fecha_creacion',''))
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
        colores_estado    = {'Abierto':'#ffc107','En Proceso':'#17a2b8','Resuelto':'#28a745','Cerrado':'#6c757d'}
        colores_prioridad = {'Baja':'#28a745','Media':'#ffc107','Alta':'#fd7e14','Crítica':'#dc3545'}
        for r in rows:
            r['color_estado']    = colores_estado.get(r.get('estado',''),'#999')
            r['color_prioridad'] = colores_prioridad.get(r.get('prioridad',''),'#999')
            r['fecha_creacion']  = str(r.get('fecha_creacion',''))
        return rows

    @staticmethod
    def actualizar_estado(id_ticket, estado, id_usuario):
        BaseDAO.execute_query(
            'UPDATE tickets SET estado = %s WHERE id_ticket = %s',
            (estado, id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Cambio de estado', f'Estado: {estado}')
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
        return True

    @staticmethod
    def cerrar_ticket(id_ticket, id_usuario):
        BaseDAO.execute_query(
            "UPDATE tickets SET estado = 'Cerrado', fecha_cierre = %s WHERE id_ticket = %s",
            (now_mx(), id_ticket), commit=True
        )
        HistorialDAO.agregar_registro(id_ticket, id_usuario, 'Cerrado', 'Ticket cerrado')
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
        colores_estado = {'Abierto':'#ffc107','En Proceso':'#17a2b8','Resuelto':'#28a745','Cerrado':'#6c757d'}
        for e in estados_raw:
            e['color'] = colores_estado.get(e['nombre'], '#999')
        stats['por_estado'] = estados_raw

        prioridades_raw = BaseDAO.execute_query(
            """SELECT prioridad AS nombre, COUNT(*) AS cantidad FROM tickets
               GROUP BY prioridad
               ORDER BY FIELD(prioridad,'Baja','Media','Alta','Crítica')""",
            fetch_all=True
        ) or []
        colores_prioridad = {'Baja':'#28a745','Media':'#ffc107','Alta':'#fd7e14','Crítica':'#dc3545'}
        for p in prioridades_raw:
            p['color'] = colores_prioridad.get(p['nombre'], '#999')
        stats['por_prioridad'] = prioridades_raw

        # Tipos de problema desde la propia tabla tickets
        stats['por_tipo'] = BaseDAO.execute_query(
            """SELECT id_tipo_problema AS nombre, COUNT(*) AS cantidad
               FROM tickets GROUP BY id_tipo_problema
               ORDER BY cantidad DESC LIMIT 5""",
            fetch_all=True
        ) or []

        return stats


class HistorialDAO(BaseDAO):

    @staticmethod
    def agregar_registro(id_ticket, id_usuario, accion, descripcion=''):
        try:
            # Buscar nombre del usuario
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
        return rows