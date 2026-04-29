"""
DAO de Notificaciones — Sistema ITIL Helpdesk DIF
Centraliza toda creación de notificaciones internas.
Coloca este archivo en: dao/notificaciones_dao.py
"""
from dao.base_dao import BaseDAO


class NotificacionesDAO:

    @staticmethod
    def crear(id_usuario, tipo, titulo, mensaje, url_accion=None):
        try:
            BaseDAO.execute_query(
                """INSERT INTO notificaciones
                   (id_usuario, tipo, titulo, mensaje, leida, url_accion, fecha_creacion)
                   VALUES (%s, %s, %s, %s, 0, %s, NOW())""",
                (id_usuario, tipo, titulo, mensaje, url_accion),
                commit=True
            )
        except Exception as e:
            print(f'[NotificacionesDAO] Error al crear: {e}')

    @staticmethod
    def notificar_equipo(tipo, titulo, mensaje, url_accion=None):
        """Notifica a todos los técnicos activos."""
        try:
            tecnicos = BaseDAO.execute_query(
                "SELECT id_tecnico FROM tecnicos WHERE activo = 1",
                fetch_all=True
            ) or []
            for t in tecnicos:
                NotificacionesDAO.crear(t['id_tecnico'], tipo, titulo, mensaje, url_accion)
        except Exception as e:
            print(f'[NotificacionesDAO.notificar_equipo] {e}')

    @staticmethod
    def notificar_admins(tipo, titulo, mensaje, url_accion=None):
        """Notifica solo a admins y jefes."""
        try:
            admins = BaseDAO.execute_query(
                "SELECT id_tecnico FROM tecnicos WHERE rol IN ('admin','jefe') AND activo = 1",
                fetch_all=True
            ) or []
            for a in admins:
                NotificacionesDAO.crear(a['id_tecnico'], tipo, titulo, mensaje, url_accion)
        except Exception as e:
            print(f'[NotificacionesDAO.notificar_admins] {e}')

    @staticmethod
    def _obtener_nombre_tecnico(id_tecnico):
        """
        FIX: Busca el nombre REAL del técnico nuevo por su ID.
        Antes se tomaba nombre_tecnico del dict del ticket, que todavía
        tenía el técnico ANTERIOR (antes del UPDATE). Ahora siempre
        se consulta directamente quién es el técnico asignado.
        """
        try:
            row = BaseDAO.execute_query(
                "SELECT CONCAT(nombre,' ',apellido) AS nombre FROM tecnicos WHERE id_tecnico = %s",
                (id_tecnico,), fetch_one=True
            )
            return row['nombre'] if row else 'un técnico'
        except Exception:
            return 'un técnico'

    @staticmethod
    def ticket_creado(ticket_info, id_usuario_creador):
        folio     = ticket_info.get('folio', '?')
        titulo    = (ticket_info.get('titulo') or '')[:60]
        prioridad = ticket_info.get('prioridad', '')
        id_ticket = ticket_info.get('id_ticket')
        nombre    = ticket_info.get('nombre_usuario', 'Usuario')
        url       = f'/admin/ticket/{id_ticket}' if id_ticket else None

        NotificacionesDAO.notificar_equipo(
            tipo='nuevo_ticket',
            titulo=f'Nuevo ticket: {folio}',
            mensaje=f'{nombre} creó "{titulo}" [{prioridad}]',
            url_accion=url
        )

    @staticmethod
    def ticket_asignado(ticket_info, id_tecnico_nuevo):
        """
        FIX: Busca el nombre del técnico nuevo por ID en lugar de tomarlo
        del ticket (que aún tiene el técnico anterior antes del JOIN).
        """
        folio     = ticket_info.get('folio', '?')
        titulo    = (ticket_info.get('titulo') or '')[:60]
        id_ticket = ticket_info.get('id_ticket')
        id_usuario= ticket_info.get('id_usuario')
        url_admin = f'/admin/ticket/{id_ticket}' if id_ticket else None
        url_user  = f'/user/ticket/{id_ticket}'  if id_ticket else None

        if id_tecnico_nuevo:
            NotificacionesDAO.crear(
                id_usuario=id_tecnico_nuevo,
                tipo='asignacion',
                titulo=f'Ticket asignado: {folio}',
                mensaje=f'Se te asignó: "{titulo}"',
                url_accion=url_admin
            )

        if id_usuario:
            nombre_tec = NotificacionesDAO._obtener_nombre_tecnico(id_tecnico_nuevo) \
                         if id_tecnico_nuevo else 'un técnico'
            NotificacionesDAO.crear(
                id_usuario=id_usuario,
                tipo='asignacion',
                titulo=f'Tu ticket {folio} fue asignado',
                mensaje=f'{nombre_tec} atenderá tu ticket: "{titulo}"',
                url_accion=url_user
            )

    @staticmethod
    def ticket_estado_cambiado(ticket_info, estado_nuevo):
        folio     = ticket_info.get('folio', '?')
        titulo    = (ticket_info.get('titulo') or '')[:60]
        id_ticket = ticket_info.get('id_ticket')
        id_usuario= ticket_info.get('id_usuario')
        url_user  = f'/user/ticket/{id_ticket}'  if id_ticket else None
        url_admin = f'/admin/ticket/{id_ticket}' if id_ticket else None
        tipo_notif = 'resolucion' if estado_nuevo in ('Resuelto','Cerrado') else 'actualizacion'

        mensajes = {
            'En Proceso': f'Tu ticket "{titulo}" está siendo atendido.',
            'Resuelto':   f'Tu ticket "{titulo}" fue resuelto. ¡Revísalo!',
            'Cerrado':    f'Tu ticket "{titulo}" ha sido cerrado.',
            'Abierto':    f'Tu ticket "{titulo}" volvió a estado Abierto.',
        }

        if id_usuario:
            NotificacionesDAO.crear(
                id_usuario=id_usuario,
                tipo=tipo_notif,
                titulo=f'Ticket {folio} → {estado_nuevo}',
                mensaje=mensajes.get(estado_nuevo, f'Estado: {estado_nuevo}'),
                url_accion=url_user
            )

        if estado_nuevo in ('Resuelto','Cerrado'):
            NotificacionesDAO.notificar_admins(
                tipo=tipo_notif,
                titulo=f'{folio} → {estado_nuevo}',
                mensaje=f'"{titulo}" marcado como {estado_nuevo}.',
                url_accion=url_admin
            )

    @staticmethod
    def ticket_resuelto(ticket_info):
        NotificacionesDAO.ticket_estado_cambiado(ticket_info, 'Resuelto')

    @staticmethod
    def ticket_cerrado(ticket_info):
        NotificacionesDAO.ticket_estado_cambiado(ticket_info, 'Cerrado')