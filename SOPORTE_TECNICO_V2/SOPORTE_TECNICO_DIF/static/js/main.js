$(document).ready(function () {

    // ALERTAS AUTO
    setTimeout(() => $('.alert').fadeOut('slow'), 5000);

    // CONFIRMACIONES
    $('.btn-danger').on('click', function (e) {
        if (!confirm('¿Seguro?')) e.preventDefault();
    });

    // TOOLTIPS
    $('[data-bs-toggle="tooltip"]').tooltip();

    // VALIDACIÓN FORMULARIOS
    $('.needs-validation').on('submit', function (e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });

    // 🔴 FILTROS AVANZADOS
    function filtrarTabla() {
        let texto = $('#searchInput').val().toLowerCase();
        let rol = $('#filtroRol').val();
        let estado = $('#filtroEstado').val();

        $('#dataTable tbody tr').each(function () {
            let row = $(this);

            let contenido = row.text().toLowerCase();
            let rolRow = row.find('.col-rol').text().toLowerCase();
            let estadoRow = row.find('.col-estado').text().toLowerCase();

            let matchTexto = contenido.includes(texto);
            let matchRol = !rol || rolRow.includes(rol);
            let matchEstado = !estado || estadoRow.includes(estado);

            row.toggle(matchTexto && matchRol && matchEstado);
        });
    }

    $('#searchInput').on('keyup', filtrarTabla);
    $('#filtroRol').on('change', filtrarTabla);
    $('#filtroEstado').on('change', filtrarTabla);

    // LOADING
    $(window).on('beforeunload', function () {
        $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary"></div></div>');
    });

    // FORM CAMBIOS
    let changed = false;
    $('form').on('change', () => changed = true);
    $('form').on('submit', () => changed = false);

    $(window).on('beforeunload', function () {
        if (changed) return 'Cambios no guardados';
    });

});

// HELPERS
function showAlert(msg, type = 'info') {
    $('.container').prepend(`
        <div class="alert alert-${type}">${msg}</div>
    `);
}