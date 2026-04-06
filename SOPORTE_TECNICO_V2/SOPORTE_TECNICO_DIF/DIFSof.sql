-- CREATE DATABASE DIFSof CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
DROP DATABASE IF EXISTS DIFSof;
CREATE DATABASE DIFSof CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE DIFSof;
DROP TABLE Activos;
SELECT COUNT(*) FROM Activos;
DROP TABLE IF EXISTS Equipos_DIF;
SELECT DATABASE();
select * from equipos_dif;
SHOW TABLES;
SELECT COUNT(*) FROM datos_equipos_dif;

-- Ejecuta esto en MySQL Workbench como administrador
SET GLOBAL time_zone = '+00:00';
-- ##################################################
-- TABLA: CLIENTES (USUARIOS FINALES)
-- ##################################################
CREATE TABLE Clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    rol ENUM('cliente') DEFAULT 'cliente',
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_departamento (departamento)
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: TECNICOS (ADMINISTRADORES Y TÉCNICOS)
-- ##################################################
CREATE TABLE Tecnicos (
    id_tecnico INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    area VARCHAR(100) DEFAULT 'Informática',
    telefono VARCHAR(20),
    rol ENUM('admin','tecnico') NOT NULL DEFAULT 'tecnico',
    activo BOOLEAN DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_rol (rol)
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: (Equipos_DIF)
-- ##################################################
CREATE TABLE Equipos_DIF (
    id_equipo INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(150),
    tipo VARCHAR(100),
    nombre_responsable VARCHAR(150),
    nombre_usuario VARCHAR(100),
    num_inventario VARCHAR(100),
    num_serie VARCHAR(100),
    procesador VARCHAR(150),
    frecuencia VARCHAR(50),
    ram VARCHAR(50),
    tipo_disco VARCHAR(50),
    capacidad_disco VARCHAR(50),
    ip_pc VARCHAR(50),
    monitor_pulgadas VARCHAR(20),
    serie_monitor VARCHAR(100),
    inv_monitor VARCHAR(100),
    telefono VARCHAR(50),
    serie_telefono VARCHAR(100),
    ip_telefono VARCHAR(50),
    correo VARCHAR(150),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- ##################################################
-- TABLA: TIPOS DE PROBLEMA
-- ##################################################
CREATE TABLE Tipos_Problema (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50)
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: TICKETS
-- ##################################################
CREATE TABLE Tickets (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    folio VARCHAR(20) UNIQUE NOT NULL,
    id_cliente INT NOT NULL,
    id_tecnico INT NULL,
    id_activo INT NULL,
    id_tipo_problema INT NULL,
    asunto VARCHAR(255) NOT NULL,
    descripcion_problema TEXT NOT NULL,
    estado ENUM('Abierto','En Proceso','Resuelto','Cerrado') DEFAULT 'Abierto',
    prioridad ENUM('Baja','Media','Alta','Crítica') DEFAULT 'Media',
    fecha_apertura DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_primera_atencion DATETIME NULL,
    fecha_resolucion DATETIME NULL,
    fecha_cierre DATETIME NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_tecnico) REFERENCES Tecnicos(id_tecnico) ON DELETE SET NULL,
    FOREIGN KEY (id_activo) REFERENCES Activos(id_activo) ON DELETE SET NULL,
    FOREIGN KEY (id_tipo_problema) REFERENCES Tipos_Problema(id_tipo),
    INDEX idx_folio (folio),
    INDEX idx_estado (estado),
    INDEX idx_cliente (id_cliente),
    INDEX idx_tecnico (id_tecnico),
    INDEX idx_prioridad (prioridad),
    INDEX idx_fecha (fecha_apertura)
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: RESOLUCIONES
-- ##################################################
CREATE TABLE Resoluciones (
    id_resolucion INT AUTO_INCREMENT PRIMARY KEY,
    id_ticket INT NOT NULL UNIQUE,
    diagnostico TEXT NOT NULL,
    solucion_aplicada TEXT NOT NULL,
    observaciones_tecnico TEXT,
    tiempo_empleado DECIMAL(6,2) DEFAULT 0 COMMENT 'Tiempo en horas',
    fecha_resolucion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ticket) REFERENCES Tickets(id_ticket) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: HISTORIAL DE TICKETS
-- ##################################################
CREATE TABLE Historial_Tickets (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_ticket INT NOT NULL,
    accion VARCHAR(100) NOT NULL,
    descripcion TEXT,
    usuario VARCHAR(100) NOT NULL,
    tipo_usuario ENUM('cliente','tecnico','admin') DEFAULT 'tecnico',
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ticket) REFERENCES Tickets(id_ticket) ON DELETE CASCADE,
    INDEX idx_ticket (id_ticket)
) ENGINE=InnoDB;

-- ##################################################
-- TABLA: SUGERENCIAS
-- ##################################################
CREATE TABLE Sugerencias (
    id_sugerencia INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo_problema INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    orden INT DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_tipo_problema) REFERENCES Tipos_Problema(id_tipo)
) ENGINE=InnoDB;

##################################3
-- TABLA CALIFICACIÓN DEL SERVICIO (UI/UX feedback)
--###########################################

CREATE TABLE feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT,
  rating INT,
  comentario TEXT,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- ##################################################
-- DATOS INICIALES
-- ##################################################

-- TIPOS DE PROBLEMA
INSERT INTO Tipos_Problema (nombre, descripcion, categoria) VALUES
('Problema de Hardware', 'Fallas físicas en equipos', 'Hardware'),
('Problema de Software', 'Errores en programas o sistemas', 'Software'),
('Problema de Red', 'Conexión a internet o red local', 'Red'),
('Problema de Impresora', 'Fallas en impresoras', 'Hardware'),
('Solicitud de Soporte', 'Asesoría o capacitación', 'Soporte'),
('Otro', 'Otros problemas no clasificados', 'General');

-- SUGERENCIAS
INSERT INTO Sugerencias (id_tipo_problema, titulo, descripcion, orden) VALUES
(1, 'Reiniciar el equipo', 'Apague completamente el equipo, espere 30 segundos y enciéndalo nuevamente.', 1),
(1, 'Verificar conexiones', 'Revise que todos los cables estén bien conectados (corriente, monitor, teclado, mouse).', 2),
(2, 'Reiniciar el programa', 'Cierre completamente el programa y ábralo de nuevo.', 1),
(2, 'Actualizar el sistema', 'Verifique si hay actualizaciones pendientes del sistema operativo.', 2),
(3, 'Verificar cable de red', 'Revise que el cable de red esté bien conectado a su equipo y al puerto de red.', 1),
(3, 'Reiniciar el equipo', 'Reinicie su computadora para renovar la conexión de red.', 2),
(4, 'Verificar conexiones de impresora', 'Revise que la impresora esté encendida y conectada correctamente.', 1),
(4, 'Revisar papel y tinta', 'Verifique que la impresora tenga papel y tinta/tóner suficiente.', 2);

-- CLIENTES (USUARIOS FINALES)
INSERT INTO Clientes (nombre, apellido, email, password, departamento, telefono) VALUES
('Juan', 'Pérez García', 'juan.perez@dif.gob.mx', MD5('user123'), 'Recursos Humanos', '4429876543'),
('María', 'López Hernández', 'maria.lopez@dif.gob.mx', MD5('user123'), 'Contabilidad', '4426547890'),
('Carlos', 'Ramírez Torres', 'carlos.ramirez@dif.gob.mx', MD5('user123'), 'Trabajo Social', '4423216549'),
('Laura', 'Martínez Silva', 'laura.martinez@dif.gob.mx', MD5('user123'), 'Administración', '4425551234');

-- TECNICOS (EQUIPO DE INFORMÁTICA)
INSERT INTO Tecnicos (nombre, apellido, email, password, area, telefono, rol) VALUES
('Humberto', 'Guerrero', 'humberto.guerrero@dif.gob.mx', MD5('admin123'), 'Informática - Jefe', '4421234567', 'admin'),
('Francisco', 'González', 'francisco.gonzalez@dif.gob.mx', MD5('admin123'), 'Informática - Técnico', '4421234568', 'tecnico'),
('Efraín', 'Martínez', 'efrain.martinez@dif.gob.mx', MD5('admin123'), 'Informática - Técnico', '4421234569', 'tecnico');

-- ACTIVOS (EQUIPOS)
INSERT INTO Activos (id_cliente, nombre_equipo, tipo_activo, marca, modelo, serial_number, numero_inventario, ubicacion) VALUES
(1, 'PC-RH-01', 'Computadora', 'HP', 'ProDesk 400 G6', 'SN-HP-123456', 'INV-2024-001', 'Recursos Humanos - Oficina 201'),
(1, 'IMP-RH-01', 'Impresora', 'HP', 'LaserJet Pro', 'SN-HP-789012', 'INV-2024-002', 'Recursos Humanos - Oficina 201'),
(2, 'PC-CONT-01', 'Computadora', 'Dell', 'OptiPlex 3070', 'SN-DELL-345678', 'INV-2024-003', 'Contabilidad - Oficina 102'),
(3, 'PC-TS-01', 'Computadora', 'Lenovo', 'ThinkCentre M720', 'SN-LEN-901234', 'INV-2024-004', 'Trabajo Social - Oficina 301'),
(4, 'IMP-ADMIN-01', 'Impresora', 'Epson', 'EcoTank L3250', 'SN-EPS-567890', 'INV-2024-005', 'Administración - Oficina 101');

-- TICKETS DE EJEMPLO
INSERT INTO Tickets (folio, id_cliente, id_activo, id_tipo_problema, asunto, descripcion_problema, prioridad, estado) VALUES
('TKT-20250127-0001', 1, 1, 1, 'Computadora muy lenta', 'La computadora se congela constantemente al iniciar programas. Tarda mucho en abrir Excel y Word.', 'Alta', 'Abierto'),
('TKT-20250127-0002', 2, 3, 2, 'Error en sistema de nómina', 'El sistema de nómina muestra un error al intentar generar el reporte mensual.', 'Crítica', 'Abierto'),
('TKT-20250127-0003', 3, 4, 3, 'Sin conexión a internet', 'La computadora no se conecta a internet. Aparece mensaje de "Sin acceso a red".', 'Media', 'Abierto');


-- ##################################################
-- VISTAS ÚTILES
-- ##################################################

CREATE OR REPLACE VIEW vista_tickets_completa AS
SELECT 
    t.id_ticket,
    t.folio,
    t.asunto,
    t.descripcion_problema,
    t.estado,
    t.prioridad,
    t.fecha_apertura,
    t.fecha_primera_atencion,
    t.fecha_resolucion,
    t.fecha_cierre,
    CONCAT(c.nombre, ' ', c.apellido) AS cliente_nombre,
    c.email AS cliente_email,
    c.departamento,
    c.telefono AS cliente_telefono,
    CONCAT(te.nombre, ' ', te.apellido) AS tecnico_nombre,
    te.email AS tecnico_email,
    te.area AS tecnico_area,
    a.nombre_equipo,
    a.tipo_activo,
    a.marca,
    a.modelo,
    a.serial_number,
    a.ubicacion,
    tp.nombre AS tipo_problema,
    r.diagnostico,
    r.solucion_aplicada,
    r.tiempo_empleado
FROM Tickets t
INNER JOIN Clientes c ON t.id_cliente = c.id_cliente
LEFT JOIN Tecnicos te ON t.id_tecnico = te.id_tecnico
LEFT JOIN Activos a ON t.id_activo = a.id_activo
LEFT JOIN Tipos_Problema tp ON t.id_tipo_problema = tp.id_tipo
LEFT JOIN Resoluciones r ON t.id_ticket = r.id_ticket;

-- ##################################################
-- PROCEDIMIENTOS ALMACENADOS
-- ##################################################

DELIMITER //

-- Procedimiento para asignar ticket a técnico
CREATE PROCEDURE sp_asignar_ticket(
    IN p_id_ticket INT,
    IN p_id_tecnico INT,
    IN p_usuario VARCHAR(100)
)
BEGIN
    UPDATE Tickets 
    SET id_tecnico = p_id_tecnico,
        estado = 'En Proceso',
        fecha_primera_atencion = IF(fecha_primera_atencion IS NULL, NOW(), fecha_primera_atencion)
    WHERE id_ticket = p_id_ticket;
    
    INSERT INTO Historial_Tickets (id_ticket, accion, descripcion, usuario, tipo_usuario)
    VALUES (p_id_ticket, 'Asignación de técnico', 'Ticket asignado a técnico', p_usuario, 'admin');
END //

-- Procedimiento para resolver ticket
CREATE PROCEDURE sp_resolver_ticket(
    IN p_id_ticket INT,
    IN p_diagnostico TEXT,
    IN p_solucion TEXT,
    IN p_observaciones TEXT,
    IN p_tiempo_empleado DECIMAL(6,2),
    IN p_usuario VARCHAR(100)
)
BEGIN
    -- Insertar resolución
    INSERT INTO Resoluciones (id_ticket, diagnostico, solucion_aplicada, observaciones_tecnico, tiempo_empleado)
    VALUES (p_id_ticket, p_diagnostico, p_solucion, p_observaciones, p_tiempo_empleado);
    
    -- Actualizar ticket
    UPDATE Tickets 
    SET estado = 'Resuelto',
        fecha_resolucion = NOW()
    WHERE id_ticket = p_id_ticket;
    
    -- Agregar al historial
    INSERT INTO Historial_Tickets (id_ticket, accion, descripcion, usuario, tipo_usuario)
    VALUES (p_id_ticket, 'Ticket resuelto', 'Solución aplicada y documentada', p_usuario, 'tecnico');
END //

DELIMITER ;

-- ##################################################
-- CONSULTAS DE VERIFICACIÓN
-- ##################################################

SELECT 'CLIENTES' AS Tabla, COUNT(*) AS Total FROM Clientes
UNION ALL
SELECT 'TECNICOS', COUNT(*) FROM Tecnicos
UNION ALL
SELECT 'ACTIVOS', COUNT(*) FROM Activos
UNION ALL
SELECT 'TIPOS_PROBLEMA', COUNT(*) FROM Tipos_Problema
UNION ALL
SELECT 'TICKETS', COUNT(*) FROM Tickets
UNION ALL
SELECT 'RESOLUCIONES', COUNT(*) FROM Resoluciones
UNION ALL
SELECT 'HISTORIAL', COUNT(*) FROM Historial_Tickets   
UNION ALL
SELECT 'SUGERENCIAS', COUNT(*) FROM Sugerencias;

-- ##################################################
-- FIN DEL SCRIPT
-- ##################################################

-- Para verificar la creación
SELECT '✓ Base de datos ITIL Helpdesk creada exitosamente' AS Mensaje;

CREATE TABLE Equipos_DIF (
    id_equipo INT AUTO_INCREMENT PRIMARY KEY,

    area VARCHAR(150),
    tipo VARCHAR(100),

    nombre_responsable VARCHAR(150),
    nombre_usuario VARCHAR(100),

    num_inventario VARCHAR(100),
    num_serie VARCHAR(100),

    procesador VARCHAR(150),
    frecuencia VARCHAR(50),

    ram VARCHAR(50),
    
    
    
  

SELECT * FROM Equipos_DIF LIMIT 10;


SELECT COUNT(*) FROM Clientes;
SELECT COUNT(*) FROM Tecnicos;
SELECT COUNT(*) FROM Activos;
SELECT COUNT(*) FROM Tickets;
    tipo_disco VARCHAR(50),
    capacidad_disco VARCHAR(50),

    ip_pc VARCHAR(50),

    monitor_pulgadas VARCHAR(20),
    serie_monitor VARCHAR(100),
    inv_monitor VARCHAR(100),

    telefono VARCHAR(50),
    serie_telefono VARCHAR(100),
    ip_telefono VARCHAR(50),

    correo VARCHAR(150),

    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);




-- ##################################################
-- TABLA INVENTARIO DIF (IMPORTACIÓN EXCEL)
-- ##################################################

CREATE TABLE Equipos_DIF (
    id_equipo INT AUTO_INCREMENT PRIMARY KEY,

    area VARCHAR(150),
    tipo VARCHAR(100),

    nombre_responsable VARCHAR(150),
    nombre_usuario VARCHAR(100),

    num_inventario VARCHAR(100),
    num_serie VARCHAR(100),

    procesador VARCHAR(150),
    frecuencia VARCHAR(50),

    ram VARCHAR(50),

    tipo_disco VARCHAR(50),
    capacidad_disco VARCHAR(50),
SELECT * FROM Equipos_DIF;
    ip_pc VARCHAR(50),

    monitor_pulgadas VARCHAR(20),
    serie_monitor VARCHAR(100),
    inv_monitor VARCHAR(100),

    telefono VARCHAR(50),
    serie_telefono VARCHAR(100),
    ip_telefono VARCHAR(50),

    correo VARCHAR(150),

    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;



DROP TABLE IF EXISTS Equipos_DIF;
SHOW TABLES;
SELECT COUNT(*) FROM Equipos_DIF;
SELECT * FROM Equipos_DIF LIMIT 51;