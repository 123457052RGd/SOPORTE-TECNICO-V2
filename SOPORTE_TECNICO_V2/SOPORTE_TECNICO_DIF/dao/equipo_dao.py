"""
DAO para gestión de equipos - MySQL
BD: equipos_dif | Tabla: equipos
"""
from dao.base_dao import BaseDAO


class EquipoDAO(BaseDAO):

    @staticmethod
    def obtener_todos():
        rows = BaseDAO.execute_query(
            'SELECT * FROM equipos ORDER BY area, nombre_responsable',
            fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_por_id(id_equipo):
        return BaseDAO.execute_query(
            'SELECT * FROM equipos WHERE id_equipo = %s',
            (id_equipo,), fetch_one=True
        )

    @staticmethod
    def obtener_por_usuario(id_usuario):
        """Busca email del usuario y cruza con correo en equipos"""
        usr = BaseDAO.execute_query(
            'SELECT email FROM usuarios WHERE id = %s',
            (id_usuario,), fetch_one=True
        )
        if not usr:
            usr = BaseDAO.execute_query(
                'SELECT email FROM tecnicos WHERE id_tecnico = %s',
                (id_usuario,), fetch_one=True
            )
        if not usr:
            return []

        email = usr['email']
        rows = BaseDAO.execute_query(
            'SELECT * FROM equipos WHERE correo = %s ORDER BY area',
            (email,), fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_por_area(area):
        rows = BaseDAO.execute_query(
            'SELECT * FROM equipos WHERE area = %s ORDER BY nombre_responsable',
            (area,), fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_tipos():
        rows = BaseDAO.execute_query(
            'SELECT DISTINCT tipo FROM equipos WHERE tipo IS NOT NULL ORDER BY tipo',
            fetch_all=True
        )
        return [r['tipo'] for r in rows] if rows else []

    @staticmethod
    def buscar(texto):
        b = f'%{texto}%'
        rows = BaseDAO.execute_query(
            """SELECT * FROM equipos
               WHERE nombre_responsable LIKE %s
                  OR nombre_usuario     LIKE %s
                  OR num_inventario     LIKE %s
                  OR ip_pc              LIKE %s
                  OR area               LIKE %s
                  OR correo             LIKE %s
               ORDER BY area, nombre_responsable""",
            (b, b, b, b, b, b), fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_stats():
        total = BaseDAO.execute_query(
            'SELECT COUNT(*) AS c FROM equipos', fetch_one=True
        )
        por_tipo = BaseDAO.execute_query(
            """SELECT tipo AS TIPO, COUNT(*) AS cantidad
               FROM equipos WHERE tipo IS NOT NULL
               GROUP BY tipo ORDER BY cantidad DESC""",
            fetch_all=True
        )
        por_area = BaseDAO.execute_query(
            """SELECT area AS AREA, COUNT(*) AS cantidad
               FROM equipos WHERE area IS NOT NULL
               GROUP BY area ORDER BY cantidad DESC""",
            fetch_all=True
        )
        return {
            'total':    total['c'] if total else 0,
            'por_tipo': por_tipo or [],
            'por_area': por_area or []
        }