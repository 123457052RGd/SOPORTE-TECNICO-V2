# 🚀 Guía de Despliegue — ITIL Helpdesk DIF El Marqués
**Desarrollado por:** ING Diego Rubio Guerrero  
**Stack:** Python 3.11 · Flask 3.0 · MySQL 8.x  
**Versión:** 2.0 — Mayo 2026

---

## ✅ Requisitos del servidor

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | 3.10+         |
| MySQL     | 8.0+          |
| RAM       | 2 GB          |
| SO        | Ubuntu 22.04 / Windows Server 2019 |

---

## 📁 Paso 1 — Clonar el proyecto

```bash
git clone https://github.com/TU_USUARIO/soporte-tecnico-dif.git
cd soporte-tecnico-dif/SOPORTE_TECNICO_DIF
```

---

## 🔐 Paso 2 — Crear el archivo .env

El archivo `.env` **NO está en el repositorio** por seguridad.
Créalo manualmente en la raíz del proyecto con este contenido:

```env
# ─── Correo ───────────────────────────────────────────
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=soportehelpdeskdifelmarques@gmail.com
MAIL_PASSWORD=TU_PASSWORD_DE_GMAIL
MAIL_DEFAULT_SENDER=soportehelpdeskdifelmarques@gmail.com
ADMIN_EMAIL=soportehelpdeskdifelmarques@gmail.com

# ─── Seguridad (NO cambiar esta clave — está generada de forma segura) ──
SECRET_KEY=a61d7e847f91e1a46603ecce4a696959624a85543a2b2b1fc2cf149f3c9235f1

# ─── Base de datos ────────────────────────────────────
DB_HOST=127.0.0.1
DB_USER=dif_app
DB_PASSWORD=TU_PASSWORD_MYSQL
DB_NAME=equipos_dif
DB_PORT=3306
```

> ⚠️ Sustituye `TU_PASSWORD_DE_GMAIL` y `TU_PASSWORD_MYSQL` con las contraseñas reales.

---

## 🗄️ Paso 3 — Configurar MySQL

### 3a. Crear usuario específico para la app (NO usar root)
```sql
CREATE USER 'dif_app'@'localhost' IDENTIFIED BY 'TU_PASSWORD_MYSQL';
GRANT SELECT, INSERT, UPDATE, DELETE ON equipos_dif.* TO 'dif_app'@'localhost';
FLUSH PRIVILEGES;
```

### 3b. Importar la base de datos
```bash
mysql -u root -p equipos_dif < Equipos_DIF.sql
```

### 3c. Verificar tablas
```sql
USE equipos_dif;
SHOW TABLES;
-- Deben aparecer: equipos, notificaciones, tecnicos, tickets,
--                 ticket_historial, tipos_problema, usuarios
```

---

## 📦 Paso 4 — Instalar dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Linux/Mac)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate

# Instalar paquetes
pip install -r requirements.txt

# Instalar gunicorn (servidor de producción)
pip install gunicorn
```

---

## ▶️ Paso 5 — Arrancar el sistema

### Desarrollo / pruebas locales
```bash
python main.py
```
Acceder en: `http://localhost:5000`

### Producción (servidor de empresa)
```bash
gunicorn -w 2 -k gthread --threads 4 \
         --timeout 60 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         -b 0.0.0.0:5000 \
         main:app
```

> Crear la carpeta `logs/` antes de correr gunicorn:
> ```bash
> mkdir -p logs
> ```

---

## 🔄 Paso 6 — Correr como servicio (Linux con systemd)

Crear archivo `/etc/systemd/system/dif-helpdesk.service`:

```ini
[Unit]
Description=ITIL Helpdesk DIF El Marqués
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/ruta/al/proyecto/SOPORTE_TECNICO_DIF
EnvironmentFile=/ruta/al/proyecto/SOPORTE_TECNICO_DIF/.env
ExecStart=/ruta/al/proyecto/.venv/bin/gunicorn \
          -w 2 -k gthread --threads 4 \
          --timeout 60 \
          -b 0.0.0.0:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable dif-helpdesk
sudo systemctl start dif-helpdesk
sudo systemctl status dif-helpdesk
```

---

## 💾 Backup de base de datos

```bash
# Ejecutar antes del primer día de uso real
mysqldump -u root -p equipos_dif > backup_$(date +%Y%m%d).sql
```

Programar backup diario con cron (Linux):
```bash
crontab -e
# Agregar esta línea (backup diario a las 2am):
0 2 * * * mysqldump -u dif_app -pTU_PASSWORD equipos_dif > /backups/dif_$(date +\%Y\%m\%d).sql
```

---

## 🧪 Verificación de que todo funciona

1. Abrir `http://servidor:5000` — debe cargar el login
2. Ingresar con usuario admin (`admin@difelmarques.gob.mx`)
3. Crear un ticket desde un usuario normal
4. Verificar que el técnico recibe notificación
5. Cambiar estado del ticket y verificar que el usuario lo ve actualizado

---

## 📞 Contacto del desarrollador

**ING Diego Rubio Guerrero**
Sistema desarrollado para DIF El Marqués — 2026

nro +52 4425844661