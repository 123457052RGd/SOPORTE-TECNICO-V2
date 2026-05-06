# ─────────────────────────────────────────────────────────────────────────────
# REEMPLAZA la función exportar_reporte en routes/admin_routes.py
# (busca "@admin_bp.route('/exportar-reporte/<formato>')" y sustituye
#  todo el bloque hasta el siguiente @admin_bp.route)
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.route('/exportar-reporte/<formato>')
@admin_required
def exportar_reporte(formato):
    from utils.reportes_pdf import ReportesManager   # ← import directo, sin pasar por reportes.py

    # Período opcional: ?periodo=hoy | semana | mes | año   (sin nada = todos)
    periodo = request.args.get('periodo') or None
    PERIODOS_VALIDOS = {'hoy', 'semana', 'mes', 'año'}
    if periodo and periodo not in PERIODOS_VALIDOS:
        periodo = None

    ahora = now_mx().strftime("%Y%m%d_%H%M%S")
    stats = TicketDAO.obtener_estadisticas(periodo=periodo)
    lista = TicketDAO.obtener_todos(periodo=periodo)

    # Etiqueta legible para el nombre del archivo
    etiqueta = {'hoy': 'hoy', 'semana': 'semana', 'mes': 'mes', 'año': 'año'}.get(periodo, 'todos')

    if formato == 'csv':
        contenido = ReportesManager.generar_reporte_csv(lista)
        return Response(
            stream_with_context(iter([contenido])),
            mimetype='text/csv; charset=utf-8-sig',
            headers={'Content-Disposition': f'attachment; filename=tickets_{etiqueta}_{ahora}.csv'}
        )

    elif formato == 'pdf':
        html_str = ReportesManager.generar_reporte_pdf(stats, lista)
        r = make_response(html_str)
        r.headers['Content-Type'] = 'text/html; charset=utf-8'
        return r

    elif formato == 'word':
        try:
            docx_bytes = ReportesManager.generar_reporte_word(stats, lista)
            r = make_response(docx_bytes)
            r.headers['Content-Type'] = (
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            r.headers['Content-Disposition'] = (
                f'attachment; filename=reporte_{etiqueta}_{ahora}.docx'
            )
            return r
        except Exception as e:
            flash(f'Error al generar Word: {e}', 'danger')
            return redirect(url_for('admin.estadisticas'))

    flash('Formato no soportado', 'danger')
    return redirect(url_for('admin.estadisticas'))