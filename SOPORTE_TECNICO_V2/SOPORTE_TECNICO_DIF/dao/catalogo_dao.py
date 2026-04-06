"""
DAO para catálogos - tipos de problema y sugerencias
BD: equipos_dif
"""
from dao.base_dao import BaseDAO


class CatalogoDAO(BaseDAO):

    @staticmethod
    def obtener_tipos_problema():
        rows = BaseDAO.execute_query(
            'SELECT id_tipo, nombre, descripcion, categoria FROM tipos_problema ORDER BY categoria, nombre',
            fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_prioridades():
        return [
            {'id': 1, 'nombre': 'Baja',    'descripcion': 'Puede esperar'},
            {'id': 2, 'nombre': 'Media',   'descripcion': 'Normal'},
            {'id': 3, 'nombre': 'Alta',    'descripcion': 'Urgente'},
            {'id': 4, 'nombre': 'Crítica', 'descripcion': 'Detiene operaciones'},
        ]

    @staticmethod
    def obtener_sugerencias_por_tipo(id_tipo):
        rows = BaseDAO.execute_query(
            'SELECT id_sugerencia, sugerencia FROM sugerencias WHERE id_tipo = %s ORDER BY id_sugerencia',
            (id_tipo,), fetch_all=True
        )
        return rows or []