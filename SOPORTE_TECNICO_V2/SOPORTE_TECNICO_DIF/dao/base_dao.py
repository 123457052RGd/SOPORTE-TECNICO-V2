"""
DAO Base - Clase base para acceso a datos MySQL
"""
import mysql.connector
from mysql.connector import Error

# Config directa para evitar problemas con get_connection()
_DB = {
    'host':        '127.0.0.1',
    'user':        'root',
    'password':    '558902',
    'database':    'equipos_dif',
    'port':        3306,
    'charset':     'utf8mb4',
    'use_unicode': True,
    'autocommit':  False,
}


def _get_conn():
    """Conexión limpia sin cursores previos que interfieran"""
    return mysql.connector.connect(**_DB)


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
                conn.rollback()
            print(f"❌ Error en la consulta: {e}")
            print(f"➡ SQL: {query}")
            print(f"➡ Params: {params}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

        return result

    @staticmethod
    def row_to_dict(row):
        return dict(row) if row else None

    @staticmethod
    def rows_to_dict_list(rows):
        return [dict(r) for r in rows] if rows else []