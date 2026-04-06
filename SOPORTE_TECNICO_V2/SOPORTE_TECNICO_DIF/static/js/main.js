// Sistema de Tickets DIF - JavaScript

$(document).ready(function() {
    // Auto-cerrar alertas después de 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirmación para acciones críticas
    $('.btn-danger').on('click', function(e) {
        if (!confirm('¿Está seguro de realizar esta acción?')) {
            e.preventDefault();
        }
    });

    // Tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Validación de formularios
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Búsqueda en tablas
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#dataTable tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // Animación de carga
    $(window).on('beforeunload', function() {
        $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"></div></div>');
    });

    // Confirmación antes de salir con formulario sin guardar
    var formChanged = false;
    $('form').on('change', 'input, select, textarea', function() {
        formChanged = true;
    });

    $('form').on('submit', function() {
        formChanged = false;
    });

    $(window).on('beforeunload', function() {
        if (formChanged) {
            return '¿Está seguro de salir? Los cambios no guardados se perderán.';
        }
    });
});

// Funciones auxiliares
function showLoading() {
    $('body').append('<div class="loading-overlay"><div class="spinner-border text-primary" role="status"></div></div>');
}

function hideLoading() {
    $('.loading-overlay').remove();
}

function showAlert(message, type = 'info') {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('.container').first().prepend(alertHtml);
    
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
}

// Formateo de fechas
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}
