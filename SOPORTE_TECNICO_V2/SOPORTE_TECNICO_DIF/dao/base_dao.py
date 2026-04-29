"""
DAO Base - Clase base para acceso a datos MySQL
FIX: se eliminó el `raise` del except para que los DAOs puedan
     capturar errores silenciosamente cuando lo necesiten.
     El error se sigue imprimiendo en consola para debug.
"""
import mysql.connector
from mysql.connector import Error, pooling

_POOL_CONFIG = {
    'pool_name':    'dif_pool',
    'pool_size':    10,
    'pool_reset_session': True,
    'host':         '127.0.0.1',
    'user':         'root',
    'password':     '558902',
    'database':     'equipos_dif',
    'port':         3306,
    'charset':      'utf8mb4',
    'use_unicode':  True,
    'autocommit':   False,
    'connect_timeout': 10,
}

try:
    _pool = mysql.connector.pooling.MySQLConnectionPool(**_POOL_CONFIG)
    print("✅ Connection pool creado correctamente")
except Error as e:
    print(f"❌ Error creando pool: {e}")
    _pool = None


def _get_conn():
    if _pool:
        return _pool.get_connection()
    cfg = {k: v for k, v in _POOL_CONFIG.items() if not k.startswith('pool')}
    return mysql.connector.connect(**cfg)


class BaseDAO:

    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
        conn   = None
        cursor = None
        result = None
        try:
            conn   = _get_conn()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(query, params or ())

            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()

            if commit:
                conn.commit()
                result = cursor.lastrowid if cursor.lastrowid else True

        except Error as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"❌ Error en la consulta: {e}")
            print(f"➡ SQL: {query}")
            print(f"➡ Params: {params}")
            # ✅ FIX: NO relanzamos — retornamos None para que el DAO decida
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        return result

    @staticmethod
    def row_to_dict(row):
        return dict(row) if row else None

    @staticmethod
    def rows_to_dict_list(rows):
        return [dict(r) for r in rows] if rows else []