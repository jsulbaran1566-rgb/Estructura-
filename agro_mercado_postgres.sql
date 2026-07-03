-- ============================================================
-- AgroMercado API — Script completo de base de datos PostgreSQL
-- Alineado 1:1 con scr/Modelos/models.py
-- ============================================================

-- ============================================================
-- TABLA CATEGORIAS
-- ============================================================
CREATE TABLE categorias (
    nombre VARCHAR(100) PRIMARY KEY
);

-- ============================================================
-- TABLA TIPOS_DOCUMENTO
-- ============================================================
CREATE TABLE tipos_documento (
    codigo VARCHAR(4) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- ============================================================
-- TABLA ROLES
-- ============================================================
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    permisos TEXT
);

-- ============================================================
-- TABLA USUARIOS  (rol_id en vez de rol VARCHAR)
-- NOTA: se agrega "numero_documento" porque antes solo existia
-- "tipo_documento" (el codigo CC/NIT/CE/PP) pero nunca se
-- guardaba el numero de documento en si. Sin esta columna es
-- imposible mostrarlo en el perfil porque el dato no existe.
-- ============================================================
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    tipo_documento VARCHAR(4) NOT NULL,
    numero_documento VARCHAR(30) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(20) UNIQUE NOT NULL,
    clave VARCHAR(255) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    empresa VARCHAR(150),
    rol_id INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    fecha_registro DATE DEFAULT CURRENT_DATE,

    CONSTRAINT chk_usuarios_estado
        CHECK (estado IN ('Activo','Inactivo')),

    CONSTRAINT fk_usuario_tipo_documento
        FOREIGN KEY (tipo_documento)
        REFERENCES tipos_documento(codigo)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (rol_id)
        REFERENCES roles(id)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ============================================================
-- TABLA PROVEEDORES
-- ============================================================
CREATE TABLE proveedores (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    ciudad VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(150),
    estado VARCHAR(20) DEFAULT 'Activo',

    CONSTRAINT chk_proveedores_estado
        CHECK (estado IN ('Activo','Inactivo'))
);

-- ============================================================
-- TABLA LOTES
-- ============================================================
CREATE TABLE lotes (
    id INTEGER PRIMARY KEY,
    producto VARCHAR(150) NOT NULL,
    cantidad INTEGER NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    productor_id INTEGER NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    fecha_cosecha DATE,
    kg_reservados INTEGER DEFAULT 0,
    precio_kg NUMERIC(10,2),

    CONSTRAINT chk_lote_cantidad
        CHECK (cantidad > 0),
    CONSTRAINT chk_lote_reservados
        CHECK (kg_reservados >= 0),
    CONSTRAINT chk_lote_estado
        CHECK (estado IN ('Activo','Inactivo')),

    CONSTRAINT fk_lote_categoria
        FOREIGN KEY (categoria)
        REFERENCES categorias(nombre)
        ON UPDATE CASCADE ON DELETE RESTRICT,

    CONSTRAINT fk_lote_productor
        FOREIGN KEY (productor_id)
        REFERENCES usuarios(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- TABLA RESERVAS  (comprador_id -> usuarios)
-- ============================================================
CREATE TABLE reservas (
    id INTEGER PRIMARY KEY,
    comprador_id INTEGER NOT NULL,
    lote_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    estado VARCHAR(20) DEFAULT 'Pendiente',

    CONSTRAINT chk_reserva_cantidad
        CHECK (cantidad > 0),
    CONSTRAINT chk_reserva_estado
        CHECK (estado IN ('Pendiente','Confirmada','Cancelada','Entregada')),

    CONSTRAINT fk_reserva_comprador
        FOREIGN KEY (comprador_id)
        REFERENCES usuarios(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_reserva_lote
        FOREIGN KEY (lote_id)
        REFERENCES lotes(id)
        ON DELETE RESTRICT
);

-- ============================================================
-- TABLA HISTORIAL SEGUIMIENTO
-- ============================================================
CREATE TABLE historial_seguimiento (
    id SERIAL PRIMARY KEY,
    accion VARCHAR(200) NOT NULL,
    lote INTEGER,
    producto VARCHAR(150) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_historial_lote
        FOREIGN KEY (lote)
        REFERENCES lotes(id)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- ============================================================
-- TABLA COMPRAS  (comprador_id -> usuarios)
-- ============================================================
CREATE TABLE compras (
    id INTEGER PRIMARY KEY,
    comprador_id INTEGER NOT NULL,
    lote_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    total NUMERIC(12,2),

    CONSTRAINT chk_compra_cantidad
        CHECK (cantidad > 0),

    CONSTRAINT fk_compra_comprador
        FOREIGN KEY (comprador_id)
        REFERENCES usuarios(id),

    CONSTRAINT fk_compra_lote
        FOREIGN KEY (lote_id)
        REFERENCES lotes(id)
);

-- ============================================================
-- TABLA VENTAS
-- ============================================================
CREATE TABLE ventas (
    id INTEGER PRIMARY KEY,
    vendedor_id INTEGER NOT NULL,
    lote_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha DATE DEFAULT CURRENT_DATE,
    total NUMERIC(12,2),

    CONSTRAINT chk_venta_cantidad
        CHECK (cantidad > 0),

    CONSTRAINT fk_venta_vendedor
        FOREIGN KEY (vendedor_id)
        REFERENCES usuarios(id),

    CONSTRAINT fk_venta_lote
        FOREIGN KEY (lote_id)
        REFERENCES lotes(id)
);

-- ============================================================
-- TABLA HISTORIAL RESERVAS
-- ============================================================
CREATE TABLE historial_reservas (
    id SERIAL PRIMARY KEY,
    reserva_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_historial_estado
        CHECK (estado IN ('Pendiente','Confirmada','Cancelada','Entregada')),

    CONSTRAINT fk_historial_reserva
        FOREIGN KEY (reserva_id)
        REFERENCES reservas(id)
        ON DELETE CASCADE
);

-- ============================================================
-- TABLA FAVORITOS
-- Relación muchos-a-muchos: un comprador marca productores como favoritos.
-- Clave primaria compuesta -> no necesita id propio ni secuencia.
-- ============================================================
CREATE TABLE favoritos (
    comprador_id   INTEGER NOT NULL,
    productor_id   INTEGER NOT NULL,
    fecha_agregado DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (comprador_id, productor_id),
    CONSTRAINT fk_favorito_comprador
        FOREIGN KEY (comprador_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_favorito_productor
        FOREIGN KEY (productor_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);

CREATE TABLE soporte (
    id             SERIAL PRIMARY KEY,
    usuario_id     INTEGER,
    nombre         VARCHAR(150) NOT NULL,
    correo         VARCHAR(150) NOT NULL,
    mensaje        TEXT NOT NULL,
    estado         VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_soporte_estado
        CHECK (estado IN ('Pendiente', 'En proceso', 'Resuelto')),
    CONSTRAINT fk_soporte_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE SET NULL
);

-- ============================================================
-- INSERT CATEGORIAS
-- ============================================================
INSERT INTO categorias (nombre) VALUES
('Hortaliza'),('Fruta'),('Tuberculo'),('Cereal'),('Leguminosa');

-- ============================================================
-- INSERT TIPOS_DOCUMENTO
-- ============================================================
INSERT INTO tipos_documento (codigo, nombre) VALUES
('CC',  'Cedula de Ciudadania'),
('NIT', 'Numero de Identificacion Tributaria'),
('CE',  'Cedula de Extranjeria'),
('PP',  'Pasaporte');

-- ============================================================
-- INSERT ROLES
-- ============================================================
INSERT INTO roles (id, nombre, descripcion, permisos) VALUES
(1, 'Administrador', 'Acceso total al sistema',             'Ver, Crear, Editar, Eliminar'),
(2, 'Productor',     'Gestiona lotes y actualiza cosechas', 'Ver, Crear, Editar'),
(3, 'Comprador',     'Explora lotes y crea reservas',       'Ver, Crear');

-- ============================================================
-- INSERT USUARIOS
-- (rol_id: 1=Administrador, 2=Productor, 3=Comprador)
-- Se agrega numero_documento para cada usuario existente.
-- ============================================================
INSERT INTO usuarios
(id, tipo_documento, numero_documento, nombre, correo, telefono, clave, direccion, ciudad, empresa, rol_id, estado)
VALUES
(1,  'CC',  '1010101010', 'Carlos Mora',          'admin@agrodirecto.com',    '3001000001', 'admin123', 'Bogota',       NULL,           NULL,                    1, 'Activo'),
(2,  'NIT', '900123456-1','Finca El Paraiso SAS', 'finca.paraiso@campo.com',  '3002000002', 'prod123',  'Medellin',     NULL,           NULL,                    2, 'Activo'),
(3,  'NIT', '900234567-2','Agro Santa Marta',     'agro.santamarta@campo.com','3003000003', 'prod456',  'Santa Marta',  NULL,           NULL,                    2, 'Activo'),
(4,  'NIT', '900345678-3','Finca Los Andes',      'losandes@campo.com',       '3004000004', 'prod789',  'Cali',         NULL,           NULL,                    2, 'Activo'),
(5,  'NIT', '900456789-4','Restaurante La Plaza', 'compras@laplaza.com',      '3005000005', 'comp123',  'Centro',       'Bogota',       'Restaurante La Plaza',  3, 'Activo'),
(6,  'NIT', '900567890-5','Hotel Campestre',      'suministros@hotelc.com',   '3006000006', 'comp456',  'El Poblado',   'Medellin',     'Hotel Campestre',       3, 'Activo'),
(7,  'NIT', '900678901-6','Distribuidora Norte',  'pedidos@distnorte.com',    '3007000007', 'comp789',  'Norte',        'Barranquilla', 'Distribuidora Norte',   3, 'Activo'),
(8,  'CC',  '1020202020', 'Maria Gonzalez',       'maria.g@campo.com',        '3008000008', 'prod000',  'Pereira',      NULL,           NULL,                    2, 'Inactivo'),
(9,  'NIT', '900789012-7','Supermercado Central', 'central@super.com',        '3009000009', 'comp000',  'Sur',          'Cali',         'Supermercado Central',  3, 'Activo'),
(10, 'CC',  '1030303030', 'Juan Ramirez',         'juan.r@agro.com',          '3010000010', 'admin456', 'Bogota',       NULL,           NULL,                    1, 'Activo');


-- ============================================================
-- INSERT PROVEEDORES
-- ============================================================
INSERT INTO proveedores (id, nombre, tipo, ciudad, telefono, correo, estado) VALUES
(1,'TransCarga SAS',     'Logistica',     'Medellin',      '3101000001','ops@transcarga.com',    'Activo'),
(2,'FrioExpress Ltda',   'Refrigeracion', 'Bogota',        '3101000002','frio@express.com',      'Activo'),
(3,'AgroInsumos del Sur','Insumos',       'Cali',          '3101000003','ventas@agroinsumos.com','Activo'),
(4,'EmpaqueStar',        'Empaque',       'Bucaramanga',   '3101000004','info@empaquestar.com',  'Inactivo'),
(5,'LogiCampo SAS',      'Logistica',     'Pereira',       '3101000005','logicampo@campo.com',   'Activo'),
(6,'Semillas del Llano', 'Insumos',       'Villavicencio', '3101000006','semillas@llano.com',    'Activo'),
(7,'CajaFlex Colombia',  'Empaque',       'Manizales',     '3101000007','cajaflex@col.com',      'Activo'),
(8,'ColdChain Andina',   'Refrigeracion', 'Bogota',        '3101000008','cold@andina.com',       'Inactivo');

-- ============================================================
-- INSERT LOTES
-- ============================================================
INSERT INTO lotes
(id,producto,cantidad,categoria,productor_id,estado,fecha_cosecha,kg_reservados,precio_kg)
VALUES
(1, 'Tomate Chonto',    2000,'Hortaliza', 2,'Activo',  '2026-07-15',500, 3000),
(2, 'Aguacate Hass',    3000,'Fruta',     3,'Activo',  '2026-08-01',1200,7500),
(3, 'Papa Pastusa',     5000,'Tuberculo', 4,'Activo',  '2026-07-20',800, 2500),
(4, 'Maiz Amarillo',    4000,'Cereal',    2,'Activo',  '2026-09-10',0,   1800),
(5, 'Frijol Cargamanto',1500,'Leguminosa',4,'Activo',  '2026-08-25',400, 5000),
(6, 'Brocoli',           800,'Hortaliza', 2,'Activo',  '2026-07-05',200, 4200),
(7, 'Mango Tommy',      2500,'Fruta',     3,'Activo',  '2026-10-01',600, 3900),
(8, 'Yuca',             3500,'Tuberculo', 4,'Inactivo','2026-06-30',3500,1500),
(9, 'Arveja Verde',     1000,'Leguminosa',2,'Activo',  '2026-08-15',0,   6000),
(10,'Platano Dominico', 4500,'Fruta',     3,'Activo',  '2026-07-28',900, 2000);

-- ============================================================
-- INSERT RESERVAS  (comprador_id apunta a usuarios)
-- ============================================================
INSERT INTO reservas (id, comprador_id, lote_id, cantidad, fecha, estado) VALUES
(1,5,1, 300,'2026-07-15','Pendiente'),
(2,6,2, 500,'2026-08-01','Pendiente'),
(3,7,3, 400,'2026-07-20','Pendiente'),
(4,5,5, 200,'2026-08-25','Pendiente'),
(5,9,2, 700,'2026-08-01','Entregada'),
(6,6,6, 200,'2026-07-05','Confirmada'),
(7,7,7, 300,'2026-10-01','Pendiente'),
(8,9,3, 400,'2026-07-20','Cancelada'),
(9,5,10,600,'2026-07-28','Pendiente');

-- ============================================================
-- INSERT HISTORIAL SEGUIMIENTO
-- ============================================================
INSERT INTO historial_seguimiento
(id,accion,lote,producto,fecha)
VALUES
(1, 'Siembra registrada',                1,'Tomate Chonto',     '2026-03-10'),
(2, 'Control de plagas aplicado',        1,'Tomate Chonto',     '2026-04-15'),
(3, 'Riego programado completado',       2,'Aguacate Hass',     '2026-04-20'),
(4, 'Inicio de floracion confirmada',    2,'Aguacate Hass',     '2026-05-01'),
(5, 'Abono organico aplicado',           3,'Papa Pastusa',      '2026-04-25'),
(6, 'Cosecha iniciada',                  8,'Yuca',              '2026-06-20'),
(7, 'Entrega al comprador completada',   8,'Yuca',              '2026-06-30'),
(8, 'Siembra registrada',                4,'Maiz Amarillo',     '2026-05-12'),
(9, 'Inspeccion fitosanitaria aprobada', 5,'Frijol Cargamanto', '2026-05-20'),
(10,'Lote habilitado para reservas',     9,'Arveja Verde',      '2026-06-01'),
(11,'Primer corte de muestra tomado',    6,'Brocoli',           '2026-06-10'),
(12,'Cosecha estimada confirmada',       7,'Mango Tommy',       '2026-06-15');

-- ============================================================
-- INSERT COMPRAS  (comprador_id apunta a usuarios)
-- ============================================================
INSERT INTO compras (id, comprador_id, lote_id, cantidad, fecha, total) VALUES
(1,5,8,1000,'2026-06-30',1500000),
(2,6,8,2500,'2026-06-30',3750000);

-- ============================================================
-- INSERT VENTAS
-- ============================================================
INSERT INTO ventas (id, vendedor_id, lote_id, cantidad, fecha, total) VALUES
(1,4,8,3500,'2026-06-30',5250000);

-- ============================================================
-- INSERT HISTORIAL RESERVAS
-- ============================================================
INSERT INTO historial_reservas
(id,reserva_id,estado,fecha)
VALUES
(1,1,'Pendiente', '2026-06-01'),
(2,1,'Confirmada','2026-06-05'),
(3,2,'Pendiente', '2026-06-02'),
(4,2,'Confirmada','2026-06-06'),
(5,3,'Pendiente', '2026-06-03'),
(6,4,'Confirmada','2026-06-07'),
(7,5,'Entregada', '2026-06-10'),
(8,6,'Confirmada','2026-06-08'),
(9,7,'Pendiente', '2026-06-12'),
(10,8,'Cancelada','2026-06-13');

-- ============================================================
-- INSERT FAVORITOS
-- comprador_id -> usuarios con rol_id=3 (Comprador)
-- productor_id -> usuarios con rol_id=2 (Productor)
-- ============================================================
INSERT INTO favoritos (comprador_id, productor_id, fecha_agregado) VALUES
(5, 2, '2026-06-01'),
(5, 3, '2026-06-05'),
(6, 2, '2026-06-10'),
(6, 4, '2026-06-12'),
(7, 3, '2026-06-15'),
(9, 4, '2026-06-20');

-- ============================================================
-- SINCRONIZAR SECUENCIAS (evita UniqueViolation en próximos INSERT)
-- Necesario porque los datos de arriba se insertaron con id explícito
-- en columnas SERIAL, y eso no mueve el contador interno de la secuencia.
-- favoritos no aparece aquí porque su llave primaria es compuesta
-- (comprador_id, productor_id) y no usa SERIAL.
-- ============================================================
SELECT setval(
    'historial_seguimiento_id_seq',
    (SELECT COALESCE(MAX(id), 0) FROM historial_seguimiento)
);

SELECT setval(
    'historial_reservas_id_seq',
    (SELECT COALESCE(MAX(id), 0) FROM historial_reservas)
);