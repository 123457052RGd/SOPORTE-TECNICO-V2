"""
Módulo de generación de reportes - Sistema DIF
Coloca este archivo en: utils/reportes_pdf.py
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
    def generar_reporte_pdf(stats, tickets):
        """HTML listo para imprimir como PDF desde el navegador (Ctrl+P)."""
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
        total = stats.get('total', 0)

        color_est  = {'Abierto':'#3b82f6','En Proceso':'#f59e0b','Resuelto':'#22c55e','Cerrado':'#94a3b8'}
        color_prio = {'Baja':'#22c55e','Media':'#f59e0b','Alta':'#f97316','Crítica':'#ef4444','Critica':'#ef4444'}

        kpi_html = ''.join(
            f'<div class="kpi"><div class="kpi-num" style="color:{color_est.get(e["nombre"],"#0d9488")}">'
            f'{e["cantidad"]}</div><div class="kpi-lbl">{e["nombre"]}</div></div>'
            for e in stats.get('por_estado', [])
        )

        rows_html = ''
        for i, t in enumerate(tickets):
            bg = '#f8fafc' if i % 2 == 0 else '#fff'
            cp = color_prio.get(t.get('prioridad',''), '#94a3b8')
            ce = color_est.get(t.get('estado',''), '#94a3b8')
            rows_html += f"""<tr style="background:{bg}">
              <td style="font-family:monospace;font-size:10px;font-weight:700;color:#0f766e">{t.get('folio','')}</td>
              <td style="font-size:11px">{str(t.get('titulo',''))[:55]}</td>
              <td style="font-size:10px">{t.get('nombre_usuario','')}</td>
              <td style="font-size:10px">{t.get('area_usuario','')}</td>
              <td><span style="background:{ce};color:#fff;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700">{t.get('estado','')}</span></td>
              <td><span style="background:{cp};color:#fff;padding:2px 7px;border-radius:10px;font-size:9px;font-weight:700">{t.get('prioridad','')}</span></td>
              <td style="font-size:10px;color:#64748b">{t.get('nombre_tecnico','') or '—'}</td>
              <td style="font-size:10px;color:#64748b">{str(t.get('fecha_creacion',''))[:16]}</td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Reporte ITIL Helpdesk — DIF</title>
<style>
  @page {{ size: A4 landscape; margin: 1.2cm; }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  body{{ font-family:'Segoe UI',Arial,sans-serif; color:#1e293b; background:#fff; font-size:12px; }}
  .no-print{{ background:#0d9488; color:#fff; padding:10px 18px; text-align:center;
    font-size:13px; font-weight:600; margin-bottom:14px; border-radius:8px;
    display:flex; align-items:center; justify-content:center; gap:12px; }}
  .print-btn{{ background:#fff; color:#0d9488; border:none; padding:6px 16px;
    border-radius:6px; font-weight:700; cursor:pointer; font-size:12px; }}
  .header{{ background:linear-gradient(135deg,#0d9488,#0f766e); color:#fff;
    padding:18px 24px; border-radius:10px; margin-bottom:14px;
    display:flex; justify-content:space-between; align-items:center; }}
  .header h1{{ font-size:18px; font-weight:800; margin-bottom:3px; }}
  .header p{{ font-size:11px; opacity:.8; }}
  .header-meta{{ text-align:right; font-size:11px; opacity:.85; }}
  .kpi-row{{ display:flex; gap:10px; margin-bottom:14px; }}
  .kpi{{ flex:1; background:#f8fafc; border:1px solid #e2e8f0; border-radius:9px;
    padding:12px; text-align:center; }}
  .kpi-num{{ font-size:24px; font-weight:800; }}
  .kpi-lbl{{ font-size:9px; color:#64748b; text-transform:uppercase;
    letter-spacing:.4px; margin-top:2px; font-weight:600; }}
  .section{{ background:#fff; border:1px solid #e2e8f0; border-radius:9px;
    overflow:hidden; margin-bottom:12px; }}
  .section-hdr{{ background:#f8fafc; padding:8px 14px; border-bottom:1px solid #e2e8f0;
    font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:.4px; }}
  table{{ width:100%; border-collapse:collapse; }}
  th{{ background:#1e293b; color:#94a3b8; font-size:9px; font-weight:700;
    text-transform:uppercase; letter-spacing:.4px; padding:8px 10px;
    border-bottom:2px solid #334155; text-align:left; }}
  td{{ padding:7px 10px; border-bottom:1px solid #f1f5f9; vertical-align:middle; }}
  tr:last-child td{{ border-bottom:none; }}
  .footer{{ text-align:center; font-size:9px; color:#94a3b8; padding-top:10px;
    border-top:1px solid #e2e8f0; margin-top:12px; }}
  @media print{{
    .no-print{{ display:none !important; }}
    body{{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  }}
</style>
</head>
<body>
<div class="no-print">
  📄 Para guardar como PDF usa <strong>Ctrl+P → Guardar como PDF</strong>
  <button class="print-btn" onclick="window.print()">🖨 Imprimir / PDF</button>
</div>
<div class="header">
  <div>
    <h1>📊 Reporte de Tickets — DIF El Márques</h1>
    <p>Sistema ITIL Helpdesk · Soporte Técnico de Informática</p>
  </div>
  <div class="header-meta">
    <div style="font-size:15px;font-weight:700">{fecha}</div>
    <div>{total} tickets en total</div>
  </div>
</div>
<div class="kpi-row">
  <div class="kpi"><div class="kpi-num" style="color:#0d9488">{total}</div><div class="kpi-lbl">Total</div></div>
  {kpi_html}
</div>
<div class="section">
  <div class="section-hdr">Listado completo de tickets ({len(tickets)} registros)</div>
  <table>
    <thead>
      <tr>
        <th>Folio</th><th>Título</th><th>Usuario</th><th>Área</th>
        <th>Estado</th><th>Prioridad</th><th>Técnico</th><th>Fecha</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
<div class="footer">ITIL Helpdesk — Sistema DIF de Soporte Técnico · Reporte generado: {fecha}</div>
</body></html>"""

    @staticmethod
    def generar_reporte_word(stats, tickets):
        """Genera reporte .docx usando python-docx."""
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            import io
        except ImportError:
            raise ImportError("Instala python-docx: pip install python-docx")

        doc = Document()
        section = doc.sections[0]
        section.page_width  = Inches(11)
        section.page_height = Inches(8.5)
        section.left_margin = section.right_margin = Inches(1)

        title = doc.add_heading('Reporte de Tickets — DIF El Márques', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title.runs[0].font.color.rgb = RGBColor(0x0d, 0x94, 0x88)

        p = doc.add_paragraph(f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")}')
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()

        doc.add_heading('Resumen General', 1)
        p = doc.add_paragraph()
        run = p.add_run(f'Total de tickets: ')
        run.bold = True
        p.add_run(str(stats.get('total', 0)))

        for estado in stats.get('por_estado', []):
            p = doc.add_paragraph(style='List Bullet')
            run = p.add_run(f"{estado['nombre']}: ")
            run.bold = True
            p.add_run(str(estado['cantidad']))

        doc.add_paragraph()
        doc.add_heading('Listado de Tickets', 1)

        cols = ['Folio', 'Título', 'Usuario', 'Área', 'Estado', 'Prioridad', 'Técnico', 'Fecha']
        table = doc.add_table(rows=1, cols=len(cols))
        table.style = 'Table Grid'

        hdr = table.rows[0].cells
        for i, col in enumerate(cols):
            hdr[i].text = col
            run = hdr[i].paragraphs[0].runs[0]
            run.font.bold = True
            run.font.size = Pt(9)

        for t in tickets:
            row = table.add_row().cells
            vals = [
                t.get('folio',''), str(t.get('titulo',''))[:50],
                t.get('nombre_usuario',''), t.get('area_usuario',''),
                t.get('estado',''), t.get('prioridad',''),
                t.get('nombre_tecnico','') or '—', str(t.get('fecha_creacion',''))[:16],
            ]
            for i, val in enumerate(vals):
                row[i].text = val
                if row[i].paragraphs[0].runs:
                    row[i].paragraphs[0].runs[0].font.size = Pt(8)

        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue()

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


# ── ALIAS para compatibilidad con user_routes.py ──────────────
# user_routes.py hace: from utils.reportes_pdf import generar_ticket_pdf
# Esta función genera el HTML del comprobante de UN ticket individual.

def generar_ticket_pdf(ticket, historial=None):
    """
    Genera HTML de comprobante para un ticket individual.
    Recibe el dict del ticket y opcionalmente el historial.
    """
    historial = historial or []
    fecha_gen = datetime.now().strftime('%d/%m/%Y %H:%M')

    color_est  = {'Abierto':'#3b82f6','En Proceso':'#f59e0b','Resuelto':'#22c55e','Cerrado':'#94a3b8'}
    color_prio = {'Baja':'#22c55e','Media':'#f59e0b','Alta':'#f97316','Crítica':'#ef4444','Critica':'#ef4444'}

    ce = color_est.get(ticket.get('estado',''), '#94a3b8')
    cp = color_prio.get(ticket.get('prioridad',''), '#94a3b8')

    hist_rows = ''
    for ev in historial:
        hist_rows += f"""<tr>
          <td style="font-size:10px;color:#64748b">{ev.get('fecha','')}</td>
          <td style="font-size:11px;font-weight:600">{ev.get('accion','')}</td>
          <td style="font-size:10px;color:#64748b">{ev.get('descripcion','') or '—'}</td>
          <td style="font-size:10px">{ev.get('nombre_completo','')}</td>
        </tr>"""

    solucion_html = ''
    if ticket.get('solucion'):
        solucion_html = f"""
        <div class="section">
          <div class="section-hdr" style="color:#065f46;background:#f0fdf4;border-color:#bbf7d0">
            ✅ Solución Aplicada
          </div>
          <div style="padding:14px">
            <p style="white-space:pre-wrap;font-size:12px;line-height:1.6">{ticket.get('solucion','')}</p>
            {'<p style="font-size:11px;color:#64748b;margin-top:8px">Observaciones: ' + ticket.get('observaciones_tecnico','') + '</p>' if ticket.get('observaciones_tecnico') else ''}
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Comprobante {ticket.get('folio','')}</title>
<style>
  @page {{ size: A4; margin: 1.5cm; }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  body{{ font-family:'Segoe UI',Arial,sans-serif; color:#1e293b; background:#fff; font-size:12px; }}
  .no-print{{ background:#0d9488; color:#fff; padding:8px 16px; text-align:center;
    font-size:12px; font-weight:600; margin-bottom:14px; border-radius:8px;
    display:flex; align-items:center; justify-content:center; gap:10px; }}
  .print-btn{{ background:#fff; color:#0d9488; border:none; padding:5px 14px;
    border-radius:6px; font-weight:700; cursor:pointer; font-size:11px; }}
  .header{{ background:linear-gradient(135deg,#0d9488,#0f766e); color:#fff;
    padding:16px 20px; border-radius:10px; margin-bottom:14px;
    display:flex; justify-content:space-between; align-items:center; }}
  .header h1{{ font-size:16px; font-weight:800; margin-bottom:2px; }}
  .header p{{ font-size:10px; opacity:.8; }}
  .folio{{ font-family:monospace; font-size:18px; font-weight:800; }}
  .section{{ border:1px solid #e2e8f0; border-radius:9px; overflow:hidden; margin-bottom:12px; }}
  .section-hdr{{ background:#f8fafc; padding:8px 14px; border-bottom:1px solid #e2e8f0;
    font-size:10px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:.4px; }}
  .grid{{ display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:14px; }}
  .field label{{ font-size:9px; font-weight:700; color:#94a3b8; text-transform:uppercase;
    letter-spacing:.4px; display:block; margin-bottom:3px; }}
  .field .val{{ font-size:12px; color:#1e293b; font-weight:500; }}
  .badge{{ padding:3px 10px; border-radius:20px; font-size:10px;
    font-weight:700; color:#fff; display:inline-block; }}
  table{{ width:100%; border-collapse:collapse; }}
  th{{ background:#1e293b; color:#94a3b8; font-size:9px; font-weight:700;
    text-transform:uppercase; letter-spacing:.4px; padding:7px 10px;
    border-bottom:2px solid #334155; text-align:left; }}
  td{{ padding:7px 10px; border-bottom:1px solid #f1f5f9; vertical-align:middle; }}
  tr:last-child td{{ border-bottom:none; }}
  .footer{{ text-align:center; font-size:9px; color:#94a3b8; padding-top:10px;
    border-top:1px solid #e2e8f0; margin-top:12px; }}
  @media print{{
    .no-print{{ display:none !important; }}
    body{{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
  }}
</style>
</head>
<body>
<div class="no-print">
  Comprobante de ticket · <strong>Ctrl+P</strong> para imprimir o guardar PDF
  <button class="print-btn" onclick="window.print()">🖨 Imprimir</button>
</div>

<div class="header">
  <div>
    <h1>🎫 Comprobante de Ticket</h1>
    <p>Sistema ITIL Helpdesk · DIF El Márques · Soporte Técnico</p>
  </div>
  <div class="folio">{ticket.get('folio','')}</div>
</div>

<div class="section">
  <div class="section-hdr">Información General</div>
  <div class="grid">
    <div class="field"><label>Estado</label><div class="val"><span class="badge" style="background:{ce}">{ticket.get('estado','')}</span></div></div>
    <div class="field"><label>Prioridad</label><div class="val"><span class="badge" style="background:{cp}">{ticket.get('prioridad','')}</span></div></div>
    <div class="field"><label>Usuario</label><div class="val">{ticket.get('nombre_usuario','')}</div></div>
    <div class="field"><label>Área</label><div class="val">{ticket.get('area_usuario','')}</div></div>
    <div class="field"><label>Tipo de Problema</label><div class="val">{ticket.get('tipo_problema','') or '—'}</div></div>
    <div class="field"><label>Técnico Asignado</label><div class="val">{ticket.get('nombre_tecnico','') or 'Sin asignar'}</div></div>
    <div class="field"><label>Fecha de Creación</label><div class="val">{str(ticket.get('fecha_creacion',''))[:16]}</div></div>
    <div class="field"><label>Fecha de Resolución</label><div class="val">{str(ticket.get('fecha_resolucion','') or '—')[:16]}</div></div>
  </div>
</div>

<div class="section">
  <div class="section-hdr">Descripción del Problema</div>
  <div style="padding:14px">
    <p style="font-weight:700;margin-bottom:6px;font-size:13px">{ticket.get('titulo','')}</p>
    <p style="white-space:pre-wrap;font-size:12px;color:#334155;line-height:1.6">{ticket.get('descripcion','')}</p>
  </div>
</div>

{solucion_html}

{'<div class="section"><div class="section-hdr">Historial de Cambios</div><table><thead><tr><th>Fecha</th><th>Acción</th><th>Descripción</th><th>Responsable</th></tr></thead><tbody>' + hist_rows + '</tbody></table></div>' if historial else ''}

<div class="footer">
  ITIL Helpdesk — Sistema DIF de Soporte Técnico © 2026 · Comprobante generado: {fecha_gen}
</div>
</body></html>"""