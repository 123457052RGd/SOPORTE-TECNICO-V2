"""
reset_passwords.py
------------------
Ejecuta este script UNA SOLA VEZ desde tu proyecto para:
1. Generar hashes werkzeug válidos
2. Actualizar las contraseñas en la BD

Contraseña por defecto para todos los usuarios: DIF2026!
Contraseña para técnicos: depende de lo que tengas ya (ver abajo)

Ejecutar: python reset_passwords.py
"""

from werkzeug.security import generate_password_hash
from config.database_mysql import get_connection

# ──────────────────────────────────────────────────────────
# CONFIGURA AQUÍ LAS CONTRASEÑAS INICIALES
# ──────────────────────────────────────────────────────────

PASSWORD_DEFAULT_USUARIOS = "DIF2026!"   # Todos los usuarios helpdesk

PASSWORDS_TECNICOS = {
    "francisco.gonzalez@difelmarques.gob.mx": "Tecnico2026!",
    "efrain.martinez@difelmarques.gob.mx":    "Tecnico2026!",
    "humberto.guerrero@difelmarques.gob.mx":  "Jefe2026!",   # jefe
}

# ──────────────────────────────────────────────────────────

def reset_usuarios():
    conn = get_connection()
    cursor = conn.cursor()

    hash_default = generate_password_hash(PASSWORD_DEFAULT_USUARIOS)
    cursor.execute(
        "UPDATE usuarios SET password = %s WHERE activo = 1",
        (hash_default,)
    )
    print(f"✅ {cursor.rowcount} usuarios actualizados con contraseña: {PASSWORD_DEFAULT_USUARIOS}")

    conn.commit()
    cursor.close()
    conn.close()


def reset_tecnicos():
    conn = get_connection()
    cursor = conn.cursor()

    for email, pwd in PASSWORDS_TECNICOS.items():
        h = generate_password_hash(pwd)
        cursor.execute(
            "UPDATE tecnicos SET password = %s WHERE email = %s",
            (h, email)
        )
        print(f"✅ Técnico {email} → contraseña: {pwd}")

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("\n=== RESETEANDO CONTRASEÑAS ===\n")
    reset_tecnicos()
    reset_usuarios()
    print("\n Listo. Puedes iniciar sesión con las contraseñas configuradas.\n")
    print("TÉCNICOS:  Tecnico2026! / Jefe2026!")
    print("USUARIOS:  DIF2026!")
    print("\n  Pide a cada usuario que cambie su contraseña al primer ingreso.")