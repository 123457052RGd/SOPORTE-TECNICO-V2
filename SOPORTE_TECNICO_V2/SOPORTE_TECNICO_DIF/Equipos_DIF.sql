CREATE DATABASE Equipos_DIF;

SELECT DATABASE();
USE Equipos_DIF;
SHOW TABLES;
USE
SELECT * FROM equipos;
RENAME TABLE equipos_dif TO equipos;


SELECT COUNT(*) FROM equipos_dif;
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
);
#--- TABLA USARIOS- ------------

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150),
    username VARCHAR(100) UNIQUE,
    email VARCHAR(150) UNIQUE,
    password VARCHAR(255),
    area VARCHAR(100),
    rol VARCHAR(50)
);
#---- TECNICOS Y JEFE DE INFORMATICA---------

INSERT INTO usuarios (nombre, username, email, password, area, rol) VALUES
('Francisco González', 'francisco.gonzalez', 'francisco.gonzalez@difelmarques.gob.mx', '$2a$10$hash1', 'Informática', 'tecnico'),
('Efraín Martínez', 'efrain.martinez', 'efrain.martinez@difelmarques.gob.mx', '$2a$10$hash2', 'Informática', 'tecnico'),
('Humberto Guerrero', 'humberto.guerrero', 'humberto.guerrero@difelmarques.gob.mx', '$2a$10$hash3', 'Informática', 'jefe');

SELECT id_usuario, nombre_completo, email FROM usuarios;

#-----------------------
# crenciciales de los usarios para help desk
#-----------------------------------------

INSERT INTO usuarios (nombre, username, email, password, area, rol, activo, fecha_registro) VALUES
('SUSAN PEREZ FRIOS', 'susan.perez', 'susan.perez@difelmarques.gob.mx', '$2b$12$A1B2C3D4E5F6G7H8I9J0KuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'UNIDAD PJC', 2, 1, NOW()),
('KARLA KABANILLAS', 'karla.kabanillas', 'karla.kabanillas@difelmarques.gob.mx', '$2b$12$B2C3D4E5F6G7H8I9J0K1LuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'D.CONTABILIDAD', 2, 1, NOW()),
('NAYELI NIEVES RAMIREZ', 'nayeli.nieves', 'nayeli.nieves@difelmarques.gob.mx', '$2b$12$C3D4E5F6G7H8I9J0K1L2MuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'D.ADQUISICIONES', 2, 1, NOW()),
('CARLOS ROLANDO DELGADO ORTA', 'carlos.delgado', 'carlos.delgado@difelmarques.gob.mx', '$2b$12$D4E5F6G7H8I9J0K1L2M3NuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'D.CONTABILIDAD', 2, 1, NOW()),
('SANDRA HERNANDEZ RAMIREZ', 'sandra.hernandez', 'sandra.hernandez@difelmarques.gob.mx', '$2b$12$E5F6G7H8I9J0K1L2M3N4OuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'D.RH', 2, 1, NOW()),
('MARICELA MATA BECERRA', 'maricela.mata', 'maricela.mata@difelmarques.gob.mx', '$2b$12$F6G7H8I9J0K1L2M3N4O5PuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'D.CONTABILIDAD', 2, 1, NOW()),
('OSCAR CANO', 'oscar.cano', 'oscar.cano@difelmarques.gob.mx', '$2b$12$G7H8I9J0K1L2M3N4O5P6QuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'REHABILITACION', 2, 1, NOW()),
('MONICA MARINA CRISTOBAL MORALES', 'monica.cristobal', 'monica.cristobal@difelmarques.gob.mx', '$2b$12$H8I9J0K1L2M3N4O5P6Q7RuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'ALMACEN', 2, 1, NOW()),
('PAOLA NABOR RAMIREZ', 'paola.nabor', 'paola.nabor@difelmarques.gob.mx', '$2b$12$I9J0K1L2M3N4O5P6Q7R8SuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'AREA MEDICA', 2, 1, NOW()),
('MARISELA HERNANDEZ VILLA', 'marisela.hernandez', 'marisela.hernandez@difelmarques.gob.mx', '$2b$12$J0K1L2M3N4O5P6Q7R8S9TuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'UNIDAD PJC', 2, 1, NOW()),
('GUADALUPE HERNANDEZ RODRIGUEZ', 'guadalupe.hernandez', 'guadalupe.hernandez@difelmarques.gob.mx', '$2b$12$K1L2M3N4O5P6Q7R8S9T0UuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'SERVICIOS GENERALES', 2, 1, NOW()),
('MARIA FERNANDA GONZALEZ ESCOBAR', 'mariafernanda.gonzalez', 'mariafernanda.gonzalez@difelmarques.gob.mx', '$2b$12$L2M3N4O5P6Q7R8S9T0U1VuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'SERVICIOS GENERALES', 2, 1, NOW()),
('OSCAR MANUEL MONTES', 'oscarmanuel.montes', 'oscarmanuel.montes@difelmarques.gob.mx', '$2b$12$M3N4O5P6Q7R8S9T0U1V2WuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'SERVICIOS GENERALES', 2, 1, NOW()),
('FABIOLA DE MIGUEL ELIAS', 'fabiola.demiguel', 'fabiola.demiguel@difelmarques.gob.mx', '$2b$12$N4O5P6Q7R8S9T0U1V2W3XuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'D.CONTABILIDAD', 2, 1, NOW()),
('IRMA ARAGON RAMIREZ', 'irma.aragon', 'irma.aragon@difelmarques.gob.mx', '$2b$12$O5P6Q7R8S9T0U1V2W3X4YuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'SERVICIOS GENERALES', 2, 1, NOW()),
('PUEBLITO RAMIREZ XISTOS', 'pueblito.ramirez', 'pueblito.ramirez@difelmarques.gob.mx', '$2b$12$P6Q7R8S9T0U1V2W3X4Y5ZuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'ADULTO MAYOR', 2, 1, NOW()),
('LAURA SUSAN RANGEL PAREDES', 'laurasusan.rangel', 'laurasusan.rangel@difelmarques.gob.mx', '$2b$12$Q7R8S9T0U1V2W3X4Y5Z6AuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'ADULTO MAYOR', 2, 1, NOW()),
('LAURA SUSAN RANGEL PAREDES 2', 'laurasusan.rangel2', 'laurasusan.rangel2@difelmarques.gob.mx', '$2b$12$R8S9T0U1V2W3X4Y5Z6A7BuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'PREVENCION Y VIGILANCIA', 2, 1, NOW()),
('GUADALUPE AREA COMUN', 'guadalupe.areacomun', 'guadalupe.areacomun@difelmarques.gob.mx', '$2b$12$S9T0U1V2W3X4Y5Z6A7B8CuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'PREVENCION Y VIGILANCIA', 2, 1, NOW()),
('GERALDIN SALDIVAR', 'geraldin.saldivar', 'geraldin.saldivar@difelmarques.gob.mx', '$2b$12$T0U1V2W3X4Y5Z6A7B8C9DuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'REHABILITACION', 2, 1, NOW()),
('MARCELA LOPEZ CRUZ', 'marcela.lopez', 'marcela.lopez@difelmarques.gob.mx', '$2b$12$U1V2W3X4Y5Z6A7B8C9D0EuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'SIGNOS VITALES', 2, 1, NOW()),
('GRACIELA RAMIREZ AVILES', 'graciela.ramirez', 'graciela.ramirez@difelmarques.gob.mx', '$2b$12$V2W3X4Y5Z6A7B8C9D0E1FuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'D.CONTABILIDAD', 2, 1, NOW()),
('MARIA DOLORES SANCHEZ PEREZ', 'mariadolores.sanchez', 'mariadolores.sanchez@difelmarques.gob.mx', '$2b$12$W3X4Y5Z6A7B8C9D0E1F2GuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'UNIDAD PJC', 2, 1, NOW()),
('ANNA PEREZ', 'anna.perez', 'anna.perez@difelmarques.gob.mx', '$2b$12$X4Y5Z6A7B8C9D0E1F2G3HuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'TRAMITES', 2, 1, NOW()),
('GRISELDA FLORES', 'griselda.flores', 'griselda.flores@difelmarques.gob.mx', '$2b$12$Y5Z6A7B8C9D0E1F2G3H4IuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'PROCURADURIA', 2, 1, NOW()),
('MARIA ALEJANDRA HERNANDEZ PACHECO', 'alejandra.hernandez', 'alejandra.hernandez@difelmarques.gob.mx', '$2b$12$Z6A7B8C9D0E1F2G3H4I5JuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'PROCURADURIA', 2, 1, NOW()),
('MARIANA GUADALUPE SANCHEZ GUTIERREZ', 'marianaguadalupe.sanchez', 'marianaguadalupe.sanchez@difelmarques.gob.mx', '$2b$12$A7B8C9D0E1F2G3H4I5J6KuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'PROCURADURIA', 2, 1, NOW()),
('MARIANA LUNA MENDOZA', 'mariana.luna', 'mariana.luna@difelmarques.gob.mx', '$2b$12$B8C9D0E1F2G3H4I5J6K7LuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'TRAMITES', 2, 1, NOW()),
('LUCERO LUNA DE MIGUEL', 'lucero.luna', 'lucero.luna@difelmarques.gob.mx', '$2b$12$C9D0E1F2G3H4I5J6K7L8MuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'D.ADQUISICIONES', 2, 1, NOW()),
('BLANCA ESTELA OLVERA', 'blancaestela.olvera', 'blancaestela.olvera@difelmarques.gob.mx', '$2b$12$D0E1F2G3H4I5J6K7L8M9NuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'D.CONTROL PATRIMONIAL', 2, 1, NOW()),
('JULIO CESAR ENRIQUEZ ALMARAZ', 'juliocesar.enriquez', 'juliocesar.enriquez@difelmarques.gob.mx', '$2b$12$E1F2G3H4I5J6K7L8M9N0OuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'D.CONTROL PATRIMONIAL', 2, 1, NOW()),
('MA. ANTONIETA ELIZABETH RIVERA RAMIREZ', 'antonieta.rivera', 'antonieta.rivera@difelmarques.gob.mx', '$2b$12$F2G3H4I5J6K7L8M9N0O1PuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'ADULTO MAYOR', 2, 1, NOW()),
('ANA LAURA HURTADO MATEHUALA', 'analaura.hurtado', 'analaura.hurtado@difelmarques.gob.mx', '$2b$12$G3H4I5J6K7L8M9N0O1P2QuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'PEDIATRIA', 2, 1, NOW()),
('GABRIEL AGUILERA CAMARGO', 'gabriel.aguilera', 'gabriel.aguilera@difelmarques.gob.mx', '$2b$12$H4I5J6K7L8M9N0O1P2Q3RuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'UNIDAD PJC', 2, 1, NOW()),
('PATRICIA HERNANDEZ BARCENAS', 'patricia.hernandez', 'patricia.hernandez@difelmarques.gob.mx', '$2b$12$I5J6K7L8M9N0O1P2Q3R4SuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'ADULTO MAYOR', 2, 1, NOW()),
('LAURA SUSAN RANGEL PAREDES 3', 'laurasusan.rangel3', 'laurasusan.rangel3@difelmarques.gob.mx', '$2b$12$J6K7L8M9N0O1P2Q3R4S5TuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'DIRECCION', 2, 1, NOW()),
('MARIA VERONICA SALINAS MADUJANO', 'veronica.salinas', 'veronica.salinas@difelmarques.gob.mx', '$2b$12$K7L8M9N0O1P2Q3R4S5T6UuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'D.CONTROL PATRIMONIAL', 2, 1, NOW()),
('ALEJANDRA ZUNIGA PEREYDA', 'alejandra.zuniga', 'alejandra.zuniga@difelmarques.gob.mx', '$2b$12$L8M9N0O1P2Q3R4S5T6U7VuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'PREVENCION Y VIGILANCIA', 2, 1, NOW()),
('MONICA MUNGUIA ARTEAGA', 'monica.munguia', 'monica.munguia@difelmarques.gob.mx', '$2b$12$M9N0O1P2Q3R4S5T6U7V8WuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'UNIDAD PJC', 2, 1, NOW()),
('GABRIEL AGUILERA CAMARGO 2', 'gabriel.aguilera2', 'gabriel.aguilera2@difelmarques.gob.mx', '$2b$12$N0O1P2Q3R4S5T6U7V8W9XuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'ALMACEN', 2, 1, NOW()),
('MARISOL CORTES VILLEGAZ', 'marisol.cortes', 'marisol.cortes@difelmarques.gob.mx', '$2b$12$O1P2Q3R4S5T6U7V8W9X0YuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'AREA MEDICA', 2, 1, NOW()),
('EDUARDO MUNOZ LUNA', 'eduardo.munoz', 'eduardo.munoz@difelmarques.gob.mx', '$2b$12$P2Q3R4S5T6U7V8W9X0Y1ZuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'UNIDAD PJC', 2, 1, NOW()),
('BEATRIZ RUIZ BAUTISTA', 'beatriz.ruiz', 'beatriz.ruiz@difelmarques.gob.mx', '$2b$12$Q3R4S5T6U7V8W9X0Y1Z2AuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'DIRECCION', 2, 1, NOW()),
('PILAR SOSA CRUZ', 'pilar.sosa', 'pilar.sosa@difelmarques.gob.mx', '$2b$12$R4S5T6U7V8W9X0Y1Z2A3BuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'RECEPCION', 2, 1, NOW()),
('JUAN MANUEL LUNA OLVERA', 'juanmanuel.luna', 'juanmanuel.luna@difelmarques.gob.mx', '$2b$12$S5T6U7V8W9X0Y1Z2A3B4CuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'DENTISTA', 2, 1, NOW()),
('CLAUDIA GARCIA', 'claudia.garcia', 'claudia.garcia@difelmarques.gob.mx', '$2b$12$T6U7V8W9X0Y1Z2A3B4C5DuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'PROCURADURIA', 2, 1, NOW()),
('ABRAM GARCIA', 'abram.garcia', 'abram.garcia@difelmarques.gob.mx', '$2b$12$U7V8W9X0Y1Z2A3B4C5D6EuQwErTyUiOpAsDfGhJkLzXcVbNm34', 'REHABILITACION', 2, 1, NOW()),
('AREA COMUN', 'areacomun', 'areacomun@difelmarques.gob.mx', '$2b$12$V8W9X0Y1Z2A3B4C5D6E7FuQwErTyUiOpAsDfGhJkLzXcVbNm56', 'REHABILITACION', 2, 1, NOW()),
('ROSARIO SORIA', 'rosario.soria', 'rosario.soria@difelmarques.gob.mx', '$2b$12$W9X0Y1Z2A3B4C5D6E7F8GuQwErTyUiOpAsDfGhJkLzXcVbNm78', 'REHABILITACION', 2, 1, NOW()),
('GUADALUPE FERRUZCA', 'guadalupe.ferruzca', 'guadalupe.ferruzca@difelmarques.gob.mx', '$2b$12$X0Y1Z2A3B4C5D6E7F8G9HuQwErTyUiOpAsDfGhJkLzXcVbNm90', 'REHABILITACION', 2, 1, NOW()),
('ADMINISTRADOR', 'admin', 'admin@difelmarques.gob.mx', '$2b$12$Y1Z2A3B4C5D6E7F8G9H0IuQwErTyUiOpAsDfGhJkLzXcVbNm12', 'ADMINISTRACION', 1, 1, NOW());
