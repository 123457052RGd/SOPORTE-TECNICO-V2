"""
Módulo de notificaciones del sistema
"""
from datetime import datetime

class NotificacionesManager:
    """Gestor de notificaciones internas del sistema"""
    
    @staticmethod
    def generar_notificacion_nuevo_ticket(ticket, usuario):
        """Genera notificación cuando se crea un nuevo ticket"""
        return {
            'tipo': 'nuevo_ticket',
            'titulo': f'Nuevo ticket #{ticket.folio}',
            'mensaje': f'{usuario["nombre_completo"]} ha creado un nuevo ticket: {ticket.titulo}',
            'prioridad': ticket.id_prioridad,
            'fecha': datetime.now(),
            'icono': 'fa-ticket-alt',
            'color': 'info'
        }
    
    @staticmethod
    def generar_notificacion_asignacion(ticket, tecnico):
        """Genera notificación cuando se asigna un ticket"""
        return {
            'tipo': 'asignacion',
            'titulo': f'Ticket asignado #{ticket["folio"]}',
            'mensaje': f'Se te ha asignado el ticket: {ticket["titulo"]}',
            'destinatario': tecnico['id_usuario'],
            'fecha': datetime.now(),
            'icono': 'fa-user-plus',
            'color': 'warning'
        }
    
    @staticmethod
    def generar_notificacion_resolucion(ticket, usuario):
        """Genera notificación cuando se resuelve un ticket"""
        return {
            'tipo': 'resolucion',
            'titulo': f'Ticket resuelto #{ticket["folio"]}',
            'mensaje': f'Tu ticket ha sido resuelto por {ticket.get("nombre_tecnico", "el equipo técnico")}',
            'destinatario': usuario['id_usuario'],
            'fecha': datetime.now(),
            'icono': 'fa-check-circle',
            'color': 'success'
        }
    
    @staticmethod
    def generar_notificacion_actualizacion(ticket):
        """Genera notificación cuando se actualiza un ticket"""
        return {
            'tipo': 'actualizacion',
            'titulo': f'Actualización ticket #{ticket["folio"]}',
            'mensaje': f'Se ha actualizado el estado a: {ticket["estado"]}',
            'fecha': datetime.now(),
            'icono': 'fa-sync-alt',
            'color': 'info'
        }
