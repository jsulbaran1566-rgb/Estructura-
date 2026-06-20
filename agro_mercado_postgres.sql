-- ============================================================
-- ESTRUCTURA COMPLETA Y POBLADO DE LA BASE DE DATOS (AgroMercado)
-- ============================================================

-- ------------------------------------------------------------
-- 1. CREACIÓN DE TABLAS (DDL)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS categorias (
    nombre VARCHAR(100) NOT NULL,
    CONSTRAINT pk_categorias PRIMARY KEY (nombre)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id     INTEGER      NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    rol    VARCHAR(50)  NOT NULL,
    CONSTRAINT pk_usuarios  PRIMARY KEY (id),
    CONSTRAINT chk_usuarios_rol CHECK (rol IN ('Productor', 'Comprador', 'Administrador'))
);

CREATE TABLE IF NOT EXISTS compradores (
    id     INTEGER      NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    ciudad VARCHAR(100) NOT NULL,
    CONSTRAINT pk_compradores PRIMARY KEY (id),
    CONSTRAINT fk_compradores_usuario FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS lotes (
    id        INTEGER      NOT NULL,
    producto  VARCHAR(150) NOT NULL,
    cantidad  INTEGER      NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    productor_id INTEGER   NOT NULL,
    CONSTRAINT pk_lotes            PRIMARY KEY (id),
    CONSTRAINT chk_lotes_cant      CHECK (cantidad > 0),
    CONSTRAINT fk_lotes_categoria  FOREIGN KEY (categoria) REFERENCES categorias(nombre) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_lotes_productor  FOREIGN KEY (productor_id) REFERENCES usuarios(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS reservas (
    id           INTEGER      NOT NULL,
    comprador_id INTEGER      NOT NULL,
    lote_id      INTEGER      NOT NULL,
    cantidad     INTEGER      NOT NULL,
    fecha        VARCHAR(20)  NOT NULL DEFAULT '09/05/2026',
    CONSTRAINT pk_reservas       PRIMARY KEY (id),
    CONSTRAINT chk_reservas_cant CHECK (cantidad > 0),
    CONSTRAINT fk_reservas_comprador FOREIGN KEY (comprador_id) REFERENCES compradores(id) ON DELETE RESTRICT,
    CONSTRAINT fk_reservas_lote      FOREIGN KEY (lote_id) REFERENCES lotes(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS historial_seguimiento (
    id       SERIAL       NOT NULL,
    accion   VARCHAR(200) NOT NULL,
    lote     INTEGER,
    producto VARCHAR(150) NOT NULL,
    fecha    DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_historial_seguimiento PRIMARY KEY (id),
    CONSTRAINT fk_historial_lote FOREIGN KEY (lote) REFERENCES lotes(id) ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS compras (
    id           INTEGER      NOT NULL,
    comprador_id INTEGER      NOT NULL,
    lote_id      INTEGER      NOT NULL,
    cantidad     INTEGER      NOT NULL,
    fecha        DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_compras      PRIMARY KEY (id),
    CONSTRAINT chk_compras_cant CHECK (cantidad > 0),
    CONSTRAINT fk_compras_comprador FOREIGN KEY (comprador_id) REFERENCES compradores(id),
    CONSTRAINT fk_compras_lote      FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

CREATE TABLE IF NOT EXISTS ventas (
    id           INTEGER      NOT NULL,
    vendedor_id  INTEGER      NOT NULL,
    lote_id      INTEGER      NOT NULL,
    cantidad     INTEGER      NOT NULL,
    fecha        DATE         NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT pk_ventas      PRIMARY KEY (id),
    CONSTRAINT chk_ventas_cant CHECK (cantidad > 0),
    CONSTRAINT fk_ventas_vendedor  FOREIGN KEY (vendedor_id) REFERENCES usuarios(id),
    CONSTRAINT fk_ventas_lote      FOREIGN KEY (lote_id) REFERENCES lotes(id)
);

CREATE TABLE IF NOT EXISTS historial_reservas (
    id         SERIAL       NOT NULL,
    reserva_id INTEGER      NOT NULL,
    estado     VARCHAR(50)  NOT NULL, 
    fecha      VARCHAR(20)  NOT NULL DEFAULT '09/05/2026',
    CONSTRAINT pk_historial_reservas PRIMARY KEY (id),
    CONSTRAINT fk_historial_reserva_id FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE
);


-- ------------------------------------------------------------
-- 2. INSERCIÓN DE DATOS SIMULADOS (DML)
-- ------------------------------------------------------------

-- Insertar Categorías
INSERT INTO categorias (nombre) VALUES
('Hortaliza'),
('Fruta'),
('Tuberculo'),
('Cereal'),
('Leguminosa');

-- Insertar Usuarios
INSERT INTO usuarios (id, nombre, rol) VALUES
(1, 'Carlos Mora', 'Administrador'),
(2, 'Finca El Paraiso SAS', 'Productor'),
(3, 'Agro Santa Marta', 'Productor'),
(4, 'Finca Los Andes', 'Productor'),
(5, 'Restaurante La Plaza', 'Comprador'),
(6, 'Hotel Campestre', 'Comprador'),
(7, 'Distribuidora Norte', 'Comprador'),
(8, 'Maria Gonzalez', 'Productor'),
(9, 'Supermercado Central', 'Comprador'),
(10, 'Juan Ramirez', 'Administrador');

-- Insertar Compradores
INSERT INTO compradores (id, nombre, ciudad) VALUES
(5, 'Restaurante La Plaza', 'Bogota'),
(6, 'Hotel Campestre', 'Medellin'),
(7, 'Distribuidora Norte', 'Barranquilla'),
(9, 'Supermercado Central', 'Cali');

-- Insertar Lotes
INSERT INTO lotes (id, producto, cantidad, categoria, productor_id) VALUES
(1, 'Tomate Chonto', 2000, 'Hortaliza', 2),
(2, 'Aguacate Hass', 3000, 'Fruta', 3),
(3, 'Papa Pastusa', 5000, 'Tuberculo', 4),
(4, 'Maiz Amarillo', 4000, 'Cereal', 2),
(5, 'Frijol Cargamanto', 1500, 'Leguminosa', 4),
(6, 'Brocoli', 800, 'Hortaliza', 2),
(7, 'Mango Tommy', 2500, 'Fruta', 3),
(8, 'Yuca', 3500, 'Tuberculo', 4),
(9, 'Arveja Verde', 1000, 'Leguminosa', 2),
(10, 'Platano Dominico', 4500, 'Fruta', 3);

-- Insertar Reservas
INSERT INTO reservas (id, comprador_id, lote_id, cantidad, fecha) VALUES
(1, 5, 1, 300, '2026-07-15'),
(2, 6, 2, 500, '2026-08-01'),
(3, 7, 3, 400, '2026-07-20'),
(4, 5, 5, 200, '2026-08-25'),
(5, 9, 2, 700, '2026-08-01'),
(6, 6, 6, 200, '2026-07-05'),
(7, 7, 7, 300, '2026-10-01'),
(8, 9, 3, 400, '2026-07-20'),
(9, 5, 10, 600, '2026-07-28');

-- Insertar Historial de Seguimiento (IDs autogenerados por SERIAL)
INSERT INTO historial_seguimiento (accion, lote, producto, fecha) VALUES
('Siembra registrada', 1, 'Tomate Chonto', '2026-03-10'),
('Control de plagas aplicado', 1, 'Tomate Chonto', '2026-04-15'),
('Riego programado completado', 2, 'Aguacate Hass', '2026-04-20'),
('Inicio de floracion confirmada', 2, 'Aguacate Hass', '2026-05-01'),
('Abono organico aplicado', 3, 'Papa Pastusa', '2026-04-25'),
('Cosecha iniciada', 8, 'Yuca', '2026-06-20'),
('Entrega al comprador completada', 8, 'Yuca', '2026-06-30'),
('Siembra registrada', 4, 'Maiz Amarillo', '2026-05-12'),
('Inspección fitosanitaria aprobada', 5, 'Frijol Cargamanto', '2026-05-20'),
('Lote habilitado para reservas', 9, 'Arveja Verde', '2026-06-01'),
('Primer corte de muestra tomado', 6, 'Brocoli', '2026-06-10'),
('Cosecha estimada confirmada', 7, 'Mango Tommy', '2026-06-15');

-- Insertar Historial de Reservas (IDs autogenerados por SERIAL)
INSERT INTO historial_reservas (reserva_id, estado, fecha) VALUES
(1, 'Pendiente', '2026-06-01'),
(1, 'Confirmada', '2026-06-05'),
(2, 'Pendiente', '2026-06-02'),
(2, 'Confirmada', '2026-06-06'),
(3, 'Pendiente', '2026-06-03'),
(4, 'Confirmada', '2026-06-07'),
(5, 'Entregada', '2026-06-10'),
(6, 'Confirmada', '2026-06-08'),
(7, 'Pendiente', '2026-06-12'),
(8, 'Cancelada', '2026-06-13');

-- Insertar Compras
INSERT INTO compras (id, comprador_id, lote_id, cantidad, fecha) VALUES
(1, 5, 8, 1000, '2026-06-30'),
(2, 6, 8, 2500, '2026-06-30');

-- Insertar Ventas
INSERT INTO ventas (id, vendedor_id, lote_id, cantidad, fecha) VALUES
(1, 4, 8, 3500, '2026-06-30');