"""
DAO Base - Clase base para acceso a datos MySQL
FIXES v2 (producción):
- Credenciales leídas desde .env — sin hardcodeo
- pool_size 25 para 50+ usuarios concurrentes
    - Manejo robusto de errores y rollback en caso de fallo
"""
import os
import logging
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('dif.dao')

_POOL_CONFIG = {
    'pool_name':          'dif_pool',
    'pool_size':          25,
    'pool_reset_session': True,
    'host':               os.environ.get('DB_HOST',     '127.0.0.1'),
    'user':               os.environ.get('DB_USER',     'root'),
    'password':           os.environ.get('DB_PASSWORD', ''),
    'database':           os.environ.get('DB_NAME',     'equipos_dif'),
    'port':               int(os.environ.get('DB_PORT', 3306)),
    'charset':            'utf8mb4',
    'use_unicode':        True,
    'autocommit':         False,
    'connect_timeout':    10,
    'connection_timeout': 5,
}

try:
    _pool = mysql.connector.pooling.MySQLConnectionPool(**_POOL_CONFIG)
    logger.info('Connection pool creado correctamente (size=25)')
except Error as e:
    logger.critical('Error creando pool: %s', e)
    _pool = None


def _get_conn():
    if _pool:
        return _pool.get_connection()
    cfg = {k: v for k, v in _POOL_CONFIG.items()
           if not k.startswith('pool') and k != 'connection_timeout'}
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
            logger.error('Error en consulta DB [%s]: %s', type(e).__name__, e)
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