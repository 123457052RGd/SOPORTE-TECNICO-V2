from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import os

def generar_ticket_pdf(ticket, historial, ruta_salida):
    doc = SimpleDocTemplate(ruta_salida, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    # Rutas de logos
    logo_dif = "static/img/logodif.png"
    logo_sys = "static/img/logo.png"

    # Encabezado con logos
    encabezado = []
    if os.path.exists(logo_dif):
        encabezado.append(Image(logo_dif, width=80, height=50))
    else:
        encabezado.append("")

    encabezado.append(Paragraph("<b>SISTEMA DE SOPORTE TÉCNICO</b>", styles['Title']))

    if os.path.exists(logo_sys):
        encabezado.append(Image(logo_sys, width=80, height=50))
    else:
        encabezado.append("")

    tabla_header = Table([encabezado], colWidths=[100, 300, 100])
    elementos.append(tabla_header)
    elementos.append(Spacer(1, 20))

    # Datos del ticket
    elementos.append(Paragraph(f"<b>Folio:</b> {ticket.get('folio')}", styles['Normal']))
    elementos.append(Paragraph(f"<b>Usuario:</b> {ticket.get('nombre_usuario')}", styles['Normal']))
    elementos.append(Paragraph(f"<b>Área:</b> {ticket.get('area_usuario')}", styles['Normal']))
    elementos.append(Paragraph(f"<b>Estado:</b> {ticket.get('estado')}", styles['Normal']))
    elementos.append(Paragraph(f"<b>Prioridad:</b> {ticket.get('prioridad')}", styles['Normal']))
    elementos.append(Spacer(1, 15))

    elementos.append(Paragraph("<b>Descripción:</b>", styles['Heading2']))
    elementos.append(Paragraph(ticket.get('descripcion', ''), styles['Normal']))
    elementos.append(Spacer(1, 20))

    # Historial
    elementos.append(Paragraph("<b>Historial:</b>", styles['Heading2']))

    data = [["Fecha", "Acción", "Descripción"]]

    for h in historial:
        data.append([
            str(h.get('fecha', '')),
            h.get('accion', ''),
            h.get('descripcion', '')
        ])

    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elementos.append(tabla)

    doc.build(elementos)
