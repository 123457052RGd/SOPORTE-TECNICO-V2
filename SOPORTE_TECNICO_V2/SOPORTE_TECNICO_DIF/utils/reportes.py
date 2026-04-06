"""
Módulo de generación de reportes - Sistema DIF
"""
from datetime import datetime
import json


class ReportesManager:

    @staticmethod
    def generar_reporte_texto(stats, tickets):
        lineas = [
            "=" * 60,
            "ITIL HELPDESK - REPORTE DE TICKETS",
            "Sistema DIF El Marques - Soporte Tecnico",
            "=" * 60,
            f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            "",
            "ESTADISTICAS GENERALES",
            "-" * 60,
            f"Total de tickets: {stats.get('total', 0)}",
            "",
            "Tickets por estado:",
        ]
        for e in stats.get('por_estado', []):
            lineas.append(f"  - {e['nombre']}: {e['cantidad']}")
        lineas.append("")
        lineas.append("Tickets por prioridad:")
        for p in stats.get('por_prioridad', []):
            lineas.append(f"  - {p['nombre']}: {p['cantidad']}")
        lineas.append("")
        lineas.append("Tipos de problema mas frecuentes:")
        for t in stats.get('por_tipo', []):
            lineas.append(f"  - {t['nombre']}: {t['cantidad']}")
        lineas.append("")
        lineas.append("LISTA DE TICKETS (ultimos 20)")
        lineas.append("-" * 60)
        for ticket in tickets[:20]:
            lineas.append(f"Folio:   {ticket.get('folio', '')}")
            lineas.append(f"Titulo:  {ticket.get('titulo', '')}")
            lineas.append(f"Estado:  {ticket.get('estado', '')} | Prioridad: {ticket.get('prioridad', '')}")
            lineas.append(f"Usuario: {ticket.get('nombre_usuario', '')} - {ticket.get('area_usuario', '')}")
            if ticket.get('nombre_tecnico'):
                lineas.append(f"Tecnico: {ticket['nombre_tecnico']}")
            lineas.append("")
        lineas += ["=" * 60, "Fin del reporte"]
        return "\n".join(lineas)

    @staticmethod
    def generar_reporte_json(stats, tickets):
        return json.dumps({
            'fecha_generacion': datetime.now().isoformat(),
            'sistema': 'ITIL Helpdesk - Sistema DIF El Marques',
            'estadisticas': stats,
            'tickets': tickets
        }, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def generar_reporte_csv(tickets):
        filas = ["Folio,Titulo,Usuario,Area,Estado,Prioridad,Tecnico,Fecha Creacion"]
        for t in tickets:
            fila = [
                str(t.get('folio', '')),
                str(t.get('titulo', '')).replace(',', ';'),
                str(t.get('nombre_usuario', '')).replace(',', ';'),
                str(t.get('area_usuario', '')).replace(',', ';'),
                str(t.get('estado', '')),
                str(t.get('prioridad', '')),
                str(t.get('nombre_tecnico', 'Sin asignar')).replace(',', ';'),
                str(t.get('fecha_creacion', ''))[:16],
            ]
            filas.append(','.join(fila))
        return "\n".join(filas)

    @staticmethod
    def calcular_metricas_desempeno(tickets):
        total     = len(tickets)
        resueltos = len([t for t in tickets if t.get('estado') in ('Resuelto', 'Cerrado')])
        return {
            'tickets_totales':    total,
            'tickets_resueltos':  resueltos,
            'tickets_pendientes': len([t for t in tickets if t.get('estado') == 'Abierto']),
            'tickets_en_proceso': len([t for t in tickets if t.get('estado') == 'En Proceso']),
            'tickets_criticos':   len([t for t in tickets if t.get('prioridad') == 'Critica']),
            'tasa_resolucion':    round((resueltos / total * 100), 2) if total else 0,
        }
