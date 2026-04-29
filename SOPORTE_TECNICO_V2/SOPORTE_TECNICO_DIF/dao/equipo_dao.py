"""
DAO para gestión de equipos - MySQL
BD: equipos_dif | Tabla: equipos
FIX: obtener_por_usuario ahora busca SOLO por correo normalizado
     (LOWER + TRIM) para evitar el error 1054 de columna id_usuario inexistente.
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
        """
        Busca los equipos del usuario en 2 pasos:

        1. Obtiene el correo normalizado del usuario (busca primero en
           `tecnicos`, luego en `usuarios`).
        2. Busca equipos cuyo campo `correo` coincida (ignorando
           mayúsculas y espacios).

        La columna id_usuario NO existe en la tabla equipos, por lo que
        NO se intenta buscar por ese campo.
        """
        # ── Paso 1: obtener el email del usuario ──────────────────────
        email = None

        # Buscar en tecnicos (admin / tecnico / jefe)
        usr = BaseDAO.execute_query(
            'SELECT LOWER(TRIM(email)) AS email FROM tecnicos WHERE id_tecnico = %s',
            (id_usuario,), fetch_one=True
        )
        if usr and usr.get('email'):
            email = usr['email']
        else:
            # Buscar en usuarios regulares
            usr = BaseDAO.execute_query(
                'SELECT LOWER(TRIM(email)) AS email FROM usuarios WHERE id = %s',
                (id_usuario,), fetch_one=True
            )
            if usr and usr.get('email'):
                email = usr['email']

        if not email:
            # No se encontró el usuario en ninguna tabla
            return []

        # ── Paso 2: buscar equipos por correo normalizado ─────────────
        rows = BaseDAO.execute_query(
            'SELECT * FROM equipos WHERE LOWER(TRIM(correo)) = %s ORDER BY area',
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

    # ──────────────────────────────────────────────
    # Crear equipo
    # ──────────────────────────────────────────────
    @staticmethod
    def crear_equipo(datos):
        """
        datos: dict con las claves del formulario.
        Retorna id_equipo creado o None si falla.
        Normaliza el correo a minúsculas antes de guardar.
        """
        correo = (datos.get('correo') or '').strip().lower() or None

        result = BaseDAO.execute_query(
            """INSERT INTO equipos (
                area, tipo, nombre_responsable, nombre_usuario,
                num_inventario, num_serie, procesador, frecuencia,
                ram, tipo_disco, capacidad_disco, ip_pc,
                monitor_pulgadas, serie_monitor, inv_monitor,
                telefono, serie_telefono, ip_telefono, correo
               ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s
               )""",
            (
                datos.get('area'),
                datos.get('tipo'),
                datos.get('nombre_responsable'),
                datos.get('nombre_usuario'),
                datos.get('num_inventario'),
                datos.get('num_serie'),
                datos.get('procesador'),
                datos.get('frecuencia'),
                datos.get('ram'),
                datos.get('tipo_disco'),
                datos.get('capacidad_disco'),
                datos.get('ip_pc'),
                datos.get('monitor_pulgadas'),
                datos.get('serie_monitor'),
                datos.get('inv_monitor'),
                datos.get('telefono'),
                datos.get('serie_telefono'),
                datos.get('ip_telefono'),
                correo,
            ),
            commit=True
        )
        if result:
            row = BaseDAO.execute_query(
                'SELECT id_equipo FROM equipos ORDER BY id_equipo DESC LIMIT 1',
                fetch_one=True
            )
            return row['id_equipo'] if row else None
        return None

    # ──────────────────────────────────────────────
    # Actualizar equipo
    # ──────────────────────────────────────────────
    @staticmethod
    def actualizar_equipo(id_equipo, datos):
        correo = (datos.get('correo') or '').strip().lower() or None
        result = BaseDAO.execute_query(
            """UPDATE equipos SET
                area               = %s,
                tipo               = %s,
                nombre_responsable = %s,
                nombre_usuario     = %s,
                num_inventario     = %s,
                num_serie          = %s,
                procesador         = %s,
                frecuencia         = %s,
                ram                = %s,
                tipo_disco         = %s,
                capacidad_disco    = %s,
                ip_pc              = %s,
                monitor_pulgadas   = %s,
                serie_monitor      = %s,
                inv_monitor        = %s,
                telefono           = %s,
                serie_telefono     = %s,
                ip_telefono        = %s,
                correo             = %s
               WHERE id_equipo = %s""",
            (
                datos.get('area'),
                datos.get('tipo'),
                datos.get('nombre_responsable'),
                datos.get('nombre_usuario'),
                datos.get('num_inventario'),
                datos.get('num_serie'),
                datos.get('procesador'),
                datos.get('frecuencia'),
                datos.get('ram'),
                datos.get('tipo_disco'),
                datos.get('capacidad_disco'),
                datos.get('ip_pc'),
                datos.get('monitor_pulgadas'),
                datos.get('serie_monitor'),
                datos.get('inv_monitor'),
                datos.get('telefono'),
                datos.get('serie_telefono'),
                datos.get('ip_telefono'),
                correo,
                id_equipo,
            ),
            commit=True
        )
        return bool(result)

    # ──────────────────────────────────────────────
    # Eliminar equipo
    # ──────────────────────────────────────────────
    @staticmethod
    def eliminar_equipo(id_equipo):
        result = BaseDAO.execute_query(
            'DELETE FROM equipos WHERE id_equipo = %s',
            (id_equipo,),
            commit=True
        )
        return bool(result)

    @staticmethod
    def obtener_stats():
        total = BaseDAO.execute_query(
            'SELECT COUNT(*) AS c FROM equipos', fetch_one=True
        )
        raw_tipo = BaseDAO.execute_query(
            """SELECT tipo AS tipo, COUNT(*) AS cantidad
               FROM equipos WHERE tipo IS NOT NULL
               GROUP BY tipo ORDER BY cantidad DESC""",
            fetch_all=True
        ) or []
        raw_area = BaseDAO.execute_query(
            """SELECT area AS area, COUNT(*) AS cantidad
               FROM equipos WHERE area IS NOT NULL
               GROUP BY area ORDER BY cantidad DESC""",
            fetch_all=True
        ) or []

        por_tipo = [{
            'tipo': r.get('tipo') or r.get('TIPO') or 'Sin tipo',
            'TIPO': r.get('tipo') or r.get('TIPO') or 'Sin tipo',
            'cantidad': r.get('cantidad', 0)
        } for r in raw_tipo]

        por_area = [{
            'area': r.get('area') or r.get('AREA') or 'Sin área',
            'AREA': r.get('area') or r.get('AREA') or 'Sin área',
            'cantidad': r.get('cantidad', 0)
        } for r in raw_area]

        return {
            'total':    total['c'] if total else 0,
            'por_tipo': por_tipo,
            'por_area': por_area,
        }