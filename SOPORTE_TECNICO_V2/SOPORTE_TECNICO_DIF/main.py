"""
Punto de entrada — ITIL Helpdesk DIF El Marqués
Desarrollado por: ING Diego Rubio Guerrero - 2026

USO EN DESARROLLO:
    python main.py

USO EN PRODUCCIÓN (50+ usuarios):
    gunicorn -w 2 -k gthread --threads 4 -b 0.0.0.0:5000 main:app

    Parámetros recomendados:
      -w 2          → 2 procesos worker
      --threads 4   → 4 hilos por worker (maneja picos de tráfico)
      --timeout 60  → cierra requests colgados
      --access-logfile - → logs al stdout
"""
from app import app

if __name__ == '__main__':
    app.run(
        debug=False,       # NUNCA True en producción
        host='0.0.0.0',
        port=5000,
        threaded=True,     # Maneja múltiples requests simultáneos en desarrollo
    )