from dao.base_dao import BaseDAO
from datetime import datetime

class NotificacionDAO:

    @staticmethod
    def crear(id_usuario, id_destinatario, tipo_destinatario, id_ticket, mensaje, tipo='info', titulo='Notificación', url_accion=None):
        query = """
        INSERT INTO notificaciones
        (id_usuario, id_destinatario, tipo_destinatario, id_ticket, mensaje, url_accion, tipo, titulo, leida, fecha_creacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
        """
        
        return BaseDAO.execute_query(query, (
            id_usuario,
            id_destinatario,
            tipo_destinatario,
            id_ticket,
            mensaje,
            url_accion,
            tipo,
            titulo,
            datetime.now()
        ))