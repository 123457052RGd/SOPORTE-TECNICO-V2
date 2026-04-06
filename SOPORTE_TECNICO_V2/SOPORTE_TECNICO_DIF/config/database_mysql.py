# config/database_mysql.py

"""
Configuración y conexión a MySQL - Sistema DIF
Usa variables de entorno del archivo .env
"""
import os


import mysql.connector
from mysql.connector import Error
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración de la base de datos
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '558902',
    'database': 'equipos_dif',
    'port': 3306,
    'charset': 'utf8mb4',
    'use_unicode': True
}

def now_mx():
    """Devuelve la hora actual sin microsegundos"""
    return datetime.now().replace(microsecond=0)

def get_connection():
    """Crea y devuelve una conexión activa a MySQL"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except Error as e:
        print(f"❌ Error al conectar a MySQL: {e}")
        return None
    
def execute_query(sql, params=None, fetch=False, fetch_one=False, commit=False):
    """Ejecuta una consulta SQL de forma segura"""
    conn = get_connection()
    if not conn:
        return None
    cursor = None
    result = None
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()

        if commit:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else True

        return result
    except Error as e:
        print(f"❌ Error SQL: {e}")
        print(f"➡ SQL: {sql}")
        print(f"➡ Params: {params}")
        if conn:
            conn.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# ================================
# Helper específico para usuarios
# ================================
def create_user(nombre, email, password, area, id_rol):
    """Inserta un usuario en la tabla usuarios con password hashed"""
    password_hash = generate_password_hash(password)
    sql = """
        INSERT INTO usuarios (nombre_completo, email, password, area, id_rol, activo, fecha_registro)
        VALUES (%s, %s, %s, %s, %s, 1, %s)
    """
    params = (nombre, email, password_hash, area, id_rol, now_mx())
    return execute_query(sql, params, commit=True)

def verify_user(email, password):
    """Verifica login comparando hash"""
    sql = "SELECT * FROM usuarios WHERE email=%s AND activo=1"
    user = execute_query(sql, (email,), fetch_one=True)
    if user and check_password_hash(user['password'], password):
        return user
    return None


def test_connection():
    """Prueba si la conexión a MySQL funciona correctamente"""
    conn = get_connection()
    if conn:
        print("Conexión a MySQL exitosa")
        conn.close()
        return True
    print(" No se pudo conectar a MySQL")
    return False