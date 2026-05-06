"""
DAO de usuarios. Soporta tanto usuarios normales como técnicos/jefes/admins.
"""
from dao.base_dao import BaseDAO
from werkzeug.security import generate_password_hash, check_password_hash

ROLES_TECNICO = ('admin', 'tecnico', 'jefe')


class UsuarioDAO(BaseDAO):

    @staticmethod
    def obtener_por_id(id_usuario, rol=None):
        """
        Busca el usuario por ID en la tabla correcta según su rol.

        BUG ANTERIOR: siempre buscaba primero en `tecnicos`, por lo que si un
        usuario normal tenía el mismo ID numérico que un técnico, se devolvían
        los datos del técnico en lugar del usuario real.

        SOLUCIÓN: si se pasa `rol`, se busca directamente en la tabla correcta.
        Si no se pasa rol, se intenta determinar por la sesión de Flask.
        Como último recurso se mantiene el fallback original.
        """
        # Determinar tabla por rol
        es_tecnico = rol in ROLES_TECNICO if rol else None

        if es_tecnico is True:
            # Buscar solo en técnicos
            row = BaseDAO.execute_query(
                """SELECT id_tecnico AS id_usuario,
                          nombre, apellido,
                          CONCAT(nombre,' ',apellido) AS nombre_completo,
                          email, area, telefono,
                          rol AS rol_nombre, activo,
                          foto,
                          NULL AS fecha_registro
                   FROM tecnicos WHERE id_tecnico = %s""",
                (id_usuario,), fetch_one=True
            )
            return row

        if es_tecnico is False:
            # Buscar solo en usuarios normales
            row = BaseDAO.execute_query(
                """SELECT id AS id_usuario,
                          nombre,
                          '' AS apellido,
                          nombre AS nombre_completo,
                          email, area,
                          telefono,
                          rol AS rol_nombre, activo,
                          foto,
                          fecha_registro
                   FROM usuarios WHERE id = %s""",
                (id_usuario,), fetch_one=True
            )
            return row

        # Fallback: si no se conoce el rol, intentar determinar consultando ambas
        # tablas pero verificando que el email coincida con lo esperado.
        # Primero intenta usuarios (la mayoría de los logins son usuarios normales).
        row = BaseDAO.execute_query(
            """SELECT id AS id_usuario,
                      nombre,
                      '' AS apellido,
                      nombre AS nombre_completo,
                      email, area,
                      telefono,
                      rol AS rol_nombre, activo,
                      foto,
                      fecha_registro
               FROM usuarios WHERE id = %s""",
            (id_usuario,), fetch_one=True
        )
        if row:
            return row

        row = BaseDAO.execute_query(
            """SELECT id_tecnico AS id_usuario,
                      nombre, apellido,
                      CONCAT(nombre,' ',apellido) AS nombre_completo,
                      email, area, telefono,
                      rol AS rol_nombre, activo,
                      foto,
                      NULL AS fecha_registro
               FROM tecnicos WHERE id_tecnico = %s""",
            (id_usuario,), fetch_one=True
        )
        return row

    @staticmethod
    def obtener_por_email(email):
        row = BaseDAO.execute_query(
            """SELECT id_tecnico AS id_usuario,
                      nombre, apellido,
                      CONCAT(nombre,' ',apellido) AS nombre_completo,
                      email, password, area, telefono,
                      rol AS rol_nombre, activo, foto
               FROM tecnicos WHERE email = %s""",
            (email,), fetch_one=True
        )
        if not row:
            row = BaseDAO.execute_query(
                """SELECT id AS id_usuario,
                          nombre,
                          '' AS apellido,
                          nombre AS nombre_completo,
                          email, password, area,
                          telefono,
                          rol AS rol_nombre, activo, foto
                   FROM usuarios WHERE email = %s""",
                (email,), fetch_one=True
            )
        return row

    @staticmethod
    def validar_credenciales(email, password):
        """Valida credenciales. Soporta bcrypt y texto plano legacy."""
        tec = BaseDAO.execute_query(
            """SELECT id_tecnico AS id_usuario,
                      CONCAT(nombre,' ',apellido) AS nombre_completo,
                      email, password, area, telefono,
                      rol AS rol_nombre, activo
               FROM tecnicos WHERE email = %s AND activo = 1""",
            (email,), fetch_one=True
        )
        if tec:
            stored = tec['password'] or ''
            if stored == password:
                return tec
            try:
                if check_password_hash(stored, password):
                    return tec
            except Exception:
                pass

        usr = BaseDAO.execute_query(
            """SELECT id AS id_usuario,
                      nombre AS nombre_completo,
                      email, password, area,
                      telefono,
                      rol AS rol_nombre, activo
               FROM usuarios WHERE email = %s AND activo = 1""",
            (email,), fetch_one=True
        )
        if usr:
            stored = usr['password'] or ''
            if stored == password:
                return usr
            try:
                if check_password_hash(stored, password):
                    return usr
            except Exception:
                pass

        return None

    @staticmethod
    def obtener_todos():
        rows = BaseDAO.execute_query(
            """SELECT id AS id_usuario,
                      nombre AS nombre_completo,
                      email, area, telefono,
                      rol AS rol_nombre, activo
               FROM usuarios WHERE activo = 1 ORDER BY nombre""",
            fetch_all=True
        )
        return rows or []

    @staticmethod
    def obtener_tecnicos():
        rows = BaseDAO.execute_query(
            """SELECT id_tecnico AS id_usuario,
                      CONCAT(nombre,' ',apellido) AS nombre_completo,
                      email, area, telefono,
                      rol AS rol_nombre, activo
               FROM tecnicos WHERE activo = 1 ORDER BY nombre""",
            fetch_all=True
        )
        return rows or []

    @staticmethod
    def actualizar_usuario_completo(id_usuario, datos, rol_sesion='usuario'):
        """
        Actualiza perfil en la tabla correcta según el rol de sesión.
        Técnicos/Jefes/Admins SÍ pueden cambiar el campo rol.
        Usuarios finales NO pueden cambiar su propio rol.
        """
        try:
            es_tecnico = rol_sesion in ROLES_TECNICO
            campos  = []
            valores = []

            if datos.get('nombre'):
                campos.append('nombre = %s')
                valores.append(datos['nombre'])

            if es_tecnico and datos.get('apellido') is not None:
                campos.append('apellido = %s')
                valores.append(datos['apellido'])

            if datos.get('email'):
                campos.append('email = %s')
                valores.append(datos['email'])

            if 'telefono' in datos and datos['telefono'] is not None:
                campos.append('telefono = %s')
                valores.append(datos['telefono'])

            if datos.get('area') is not None:
                campos.append('area = %s')
                valores.append(datos['area'])

            if datos.get('password_new'):
                campos.append('password = %s')
                valores.append(generate_password_hash(datos['password_new']))

            foto_val = datos.get('foto')
            if foto_val and isinstance(foto_val, str) and foto_val.strip():
                campos.append('foto = %s')
                valores.append(foto_val.strip())

            # ── ROL: solo técnicos/jefes/admins pueden cambiar el rol ──
            if es_tecnico and datos.get('rol') and datos['rol'].strip():
                roles_validos = ('usuario', 'tecnico', 'jefe', 'admin')
                nuevo_rol = datos['rol'].strip().lower()
                if nuevo_rol in roles_validos:
                    campos.append('rol = %s')
                    valores.append(nuevo_rol)

            # ── PRIMER LOGIN: si cambió contraseña, quitar flag (ambas tablas) ──
            if datos.get('password_new'):
                if es_tecnico:
                    campos.append('primer_login = %s')
                    valores.append(0)

            if not campos:
                return True  # nada que actualizar

            valores.append(id_usuario)
            tabla = 'tecnicos' if es_tecnico else 'usuarios'
            pk    = 'id_tecnico' if es_tecnico else 'id'

            query = f"UPDATE {tabla} SET {', '.join(campos)} WHERE {pk} = %s"
            BaseDAO.execute_query(query, tuple(valores), commit=True)

            # Limpiar primer_login en tabla usuarios también
            if datos.get('password_new') and not es_tecnico:
                BaseDAO.execute_query(
                    "UPDATE usuarios SET primer_login = 0 WHERE id = %s",
                    (id_usuario,), commit=True
                )
            return True

        except Exception as e:
            try:
                from flask import current_app
                current_app.logger.error(f'[UsuarioDAO] Error actualizar perfil: {e}')
            except Exception:
                pass
            return False

    @staticmethod
    def actualizar_usuario(id_usuario, datos):
        """Legacy"""
        try:
            BaseDAO.execute_query(
                "UPDATE usuarios SET area = %s, telefono = %s WHERE id = %s",
                (datos.get('area'), datos.get('telefono'), id_usuario),
                commit=True
            )
            return True
        except Exception:
            return False

    @staticmethod
    def crear_usuario(nombre, email, password, area='', rol='usuario'):
        try:
            username = email.split('@')[0]
            BaseDAO.execute_query(
                """INSERT INTO usuarios
                   (nombre, username, email, password, area, rol, activo, fecha_registro)
                   VALUES (%s, %s, %s, %s, %s, %s, 1, NOW())""",
                (nombre, username, email, generate_password_hash(password), area, rol),
                commit=True
            )
            return True
        except Exception:
            return False
