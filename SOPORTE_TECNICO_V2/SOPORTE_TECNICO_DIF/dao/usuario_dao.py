"""
DAO para gestión de usuarios - MySQL
BD: equipos_dif | Tablas: usuarios, tecnicos
"""
from dao.base_dao import BaseDAO
from werkzeug.security import check_password_hash, generate_password_hash


class UsuarioDAO(BaseDAO):

    @staticmethod
    def obtener_por_id(id_usuario):
        """Busca primero en tecnicos, luego en usuarios — lee foto y telefono reales"""
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
        if not row:
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

    @staticmethod
    def obtener_por_email(email):
        """Busca por email en tecnicos y usuarios"""
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
        # 1. Tecnicos
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

        # 2. Usuarios normales
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
        """Obtiene todos los usuarios activos"""
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
        """Obtiene técnicos y admins activos"""
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
        Actualiza perfil completo: nombre, apellido, email, telefono,
        area, password y foto. Funciona para tecnicos y usuarios.
        """
        try:
            es_tecnico = rol_sesion in ('admin', 'tecnico', 'jefe')
            campos  = []
            valores = []

            if datos.get('nombre'):
                campos.append('nombre = %s')
                valores.append(datos['nombre'])

            if es_tecnico and datos.get('apellido'):
                campos.append('apellido = %s')
                valores.append(datos['apellido'])

            if datos.get('email'):
                campos.append('email = %s')
                valores.append(datos['email'])

            # Telefono para AMBOS (tecnicos y usuarios)
            if datos.get('telefono') is not None:
                campos.append('telefono = %s')
                valores.append(datos['telefono'])

            if datos.get('area'):
                campos.append('area = %s')
                valores.append(datos['area'])

            if datos.get('password_new'):
                campos.append('password = %s')
                valores.append(generate_password_hash(datos['password_new']))

            # Foto — siempre guardar si viene
            if datos.get('foto'):
                campos.append('foto = %s')
                valores.append(datos['foto'])

            if not campos:
                return True

            valores.append(id_usuario)
            tabla = 'tecnicos' if es_tecnico else 'usuarios'
            pk    = 'id_tecnico' if es_tecnico else 'id'

            query = f"UPDATE {tabla} SET {', '.join(campos)} WHERE {pk} = %s"
            print(f'[UsuarioDAO] Query: {query}')
            print(f'[UsuarioDAO] Valores: {valores}')

            BaseDAO.execute_query(query, tuple(valores), commit=True)
            return True

        except Exception as e:
            print(f'[UsuarioDAO] Error actualizar perfil: {e}')
            return False

    @staticmethod
    def actualizar_usuario(id_usuario, datos):
        """Método legacy"""
        try:
            BaseDAO.execute_query(
                "UPDATE usuarios SET area = %s, telefono = %s WHERE id = %s",
                (datos.get('area'), datos.get('telefono'), id_usuario),
                commit=True
            )
            return True
        except Exception as e:
            print(f'[UsuarioDAO] Error: {e}')
            return False

    @staticmethod
    def crear_usuario(nombre, email, password, area='', rol='usuario'):
        """Crea un nuevo usuario con contraseña hasheada"""
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
        except Exception as e:
            print(f'[UsuarioDAO] Error crear usuario: {e}')
            return False