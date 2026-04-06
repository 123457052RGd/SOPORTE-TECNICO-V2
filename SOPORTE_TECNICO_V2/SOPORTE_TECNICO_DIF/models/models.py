"""
Clases de datos simples (sin SQLAlchemy).
Solo se usan como objetos de transferencia donde conviene.
"""
from datetime import datetime


class Ticket:
    """Objeto de transferencia para crear un ticket"""
    def __init__(self, id_usuario=None, id_equipo=None, id_tipo_problema=None,
                 titulo='', descripcion='', id_prioridad='Media', prioridad='Media', **kwargs):
        self.id_usuario       = id_usuario
        self.id_equipo        = id_equipo
        self.id_tipo_problema = id_tipo_problema
        self.titulo           = titulo
        self.descripcion      = descripcion
        self.prioridad        = prioridad or id_prioridad
        self.fecha_creacion   = datetime.now()
