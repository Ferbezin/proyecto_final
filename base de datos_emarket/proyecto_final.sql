
DROP TABLE IF EXISTS auditoria_precios CASCADE;
DROP TABLE IF EXISTS factura_pago CASCADE;
DROP TABLE IF EXISTS pedido_articulo CASCADE;
DROP TABLE IF EXISTS pedido CASCADE;
DROP TABLE IF EXISTS inventario_bodega CASCADE;
DROP TABLE IF EXISTS articulo CASCADE;
DROP TABLE IF EXISTS bodega CASCADE;
DROP TABLE IF EXISTS proveedor CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;
DROP TABLE IF EXISTS estado_envio CASCADE;
DROP TABLE IF EXISTS usuario CASCADE;

DROP TYPE IF EXISTS metodo_pago_enum CASCADE;


CREATE TYPE metodo_pago_enum AS ENUM ('Tarjeta', 'PSE', 'Efectivo');



CREATE TABLE usuario (
    cc INT NOT NULL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    telefono VARCHAR(20) NOT NULL,
    clave VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE estado_envio (
    estado_id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(200) DEFAULT NULL
);


CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT DEFAULT NULL
);


CREATE TABLE proveedor (
    nit VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    ciudad VARCHAR(100) NOT NULL
);


CREATE TABLE bodega (
    id_bodega SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(200) NOT NULL
);


CREATE TABLE articulo (
    codigo_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio_lista DECIMAL(10,2) NOT NULL CHECK (precio_lista >= 0),
    cantidad_disponible INT NOT NULL DEFAULT 0 CHECK (cantidad_disponible >= 0),
    id_categoria INT,
    nit_proveedor VARCHAR(20),
    CONSTRAINT fk_art_cat FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria) ON DELETE SET NULL,
    CONSTRAINT fk_art_prov FOREIGN KEY (nit_proveedor) REFERENCES proveedor (nit) ON DELETE SET NULL
);


CREATE TABLE inventario_bodega (
    codigo_producto INT NOT NULL,
    id_bodega INT NOT NULL,
    stock_actual INT NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    PRIMARY KEY (codigo_producto, id_bodega),
    CONSTRAINT fk_inv_art FOREIGN KEY (codigo_producto) REFERENCES articulo (codigo_producto) ON DELETE CASCADE,
    CONSTRAINT fk_inv_bod FOREIGN KEY (id_bodega) REFERENCES bodega (id_bodega) ON DELETE CASCADE
);


CREATE TABLE pedido (
    id_pedido SERIAL PRIMARY KEY,
    f_transaccion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK (total >= 0),
    cc_usuario INT NOT NULL,
    estado_id INT NOT NULL,
    CONSTRAINT fk_ped_usu FOREIGN KEY (cc_usuario) REFERENCES usuario (cc),
    CONSTRAINT fk_ped_est FOREIGN KEY (estado_id) REFERENCES estado_envio (estado_id)
);


CREATE TABLE pedido_articulo (
    id_pedido INT NOT NULL,
    codigo_producto INT NOT NULL,
    cantidad_vendida INT NOT NULL CHECK (cantidad_vendida > 0),
    precio_facturado DECIMAL(10,2) NOT NULL CHECK (precio_facturado >= 0),
    subtotal DECIMAL(12,2) GENERATED ALWAYS AS (cantidad_vendida * precio_facturado) STORED,
    PRIMARY KEY (id_pedido, codigo_producto),
    CONSTRAINT fk_pa_ped FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido) ON DELETE CASCADE,
    CONSTRAINT fk_pa_art FOREIGN KEY (codigo_producto) REFERENCES articulo (codigo_producto)
);


CREATE TABLE factura_pago (
    id_factura SERIAL PRIMARY KEY,
    id_pedido INT NOT NULL UNIQUE,
    metodo_pago metodo_pago_enum NOT NULL,
    fecha_pago TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_pagado DECIMAL(12,2) NOT NULL CHECK (valor_pagado >= 0),
    estado_pago VARCHAR(30) NOT NULL DEFAULT 'Aprobado',
    CONSTRAINT fk_fac_ped FOREIGN KEY (id_pedido) REFERENCES pedido (id_pedido) ON DELETE CASCADE
);


CREATE TABLE auditoria_precios (
    id_auditoria SERIAL PRIMARY KEY,
    codigo_producto INT NOT NULL,
    precio_anterior DECIMAL(10,2) NOT NULL,
    precio_nuevo DECIMAL(10,2) NOT NULL,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_sistema VARCHAR(100) DEFAULT CURRENT_USER
);


CREATE INDEX idx_usuario_correo ON usuario (correo);
CREATE INDEX idx_pedido_fecha ON pedido (f_transaccion);
CREATE INDEX idx_articulo_categoria ON articulo (id_categoria);


INSERT INTO usuario (cc, nombre, correo, telefono, clave) VALUES
(11223344, 'Juan Pérez', 'juan.perez@email.com', '3001234567', 'pass123'),
(22334455, 'María López', 'maria.lopez@email.com', '3109876543', 'pass456'),
(33445566, 'Carlos Ruiz', 'carlos.ruiz@email.com', '3204567890', 'pass789');

INSERT INTO estado_envio (nombre, descripcion) VALUES
('Pendiente', 'Pedido recibido y pendiente de preparación'),
('En Proceso', 'Empacando en bodega'),
('En Tránsito', 'En camino con la transportadora'),
('Entregado', 'Entregado al cliente satisfactoriamente'),
('Devuelto', 'Devuelto por novedad en entrega');

INSERT INTO categoria (nombre, descripcion) VALUES
('Tecnología', 'Equipos de cómputo y periféricos'),
('Muebles Gamer', 'Sillas y escritorios ergonómicos');

INSERT INTO proveedor (nit, nombre, contacto, ciudad) VALUES
('900123456-1', 'TechSupplier S.A.', 'Pedro Gomez', 'Bogotá'),
('900987654-2', 'Muebles Express Ltda', 'Ana Martinez', 'Medellín');

INSERT INTO bodega (nombre, ubicacion) VALUES
('Bodega Principal Centro', 'Calle 26 #13-45, Bogotá'),
('Bodega Norte', 'Autopista Norte Km 19, Chía');

INSERT INTO articulo (nombre, precio_lista, cantidad_disponible, id_categoria, nit_proveedor) VALUES
('Laptop Gamer Pro', 3500000.00, 10, 1, '900123456-1'),
('Silla Gamer RGB', 850000.00, 15, 2, '900987654-2'),
('Pad Mouse Gigante', 60000.00, 40, 1, '900123456-1');

INSERT INTO inventario_bodega (codigo_producto, id_bodega, stock_actual) VALUES
(1, 1, 7), (1, 2, 3),
(2, 1, 10), (2, 2, 5),
(3, 1, 40);

CREATE OR REPLACE FUNCTION fn_validar_stock_pedido()
RETURNS TRIGGER AS $$
DECLARE
    v_stock INT;
BEGIN
    SELECT cantidad_disponible INTO v_stock 
    FROM articulo 
    WHERE codigo_producto = NEW.codigo_producto;
    
    IF v_stock IS NULL OR v_stock < NEW.cantidad_vendida THEN
        RAISE EXCEPTION 'Error de Negocio: Stock insuficiente en inventario para el producto %.', NEW.codigo_producto;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_stock_pedido
BEFORE INSERT ON pedido_articulo
FOR EACH ROW
EXECUTE FUNCTION fn_validar_stock_pedido();



CREATE OR REPLACE FUNCTION fn_auditoria_precio_articulo()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.precio_lista <> NEW.precio_lista THEN
        INSERT INTO auditoria_precios (codigo_producto, precio_anterior, precio_nuevo)
        VALUES (OLD.codigo_producto, OLD.precio_lista, NEW.precio_lista);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auditoria_precio_articulo
AFTER UPDATE ON articulo
FOR EACH ROW
EXECUTE FUNCTION fn_auditoria_precio_articulo();



CREATE OR REPLACE PROCEDURE sp_registrar_pedido_completo(
    p_cc_usuario INT,
    p_codigo_producto INT,
    p_cantidad INT,
    p_metodo_pago VARCHAR(20),
    INOUT p_id_pedido INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_precio DECIMAL(10,2);
    v_stock INT;
    v_total DECIMAL(12,2);
    v_estado_id INT;
BEGIN

    SELECT precio_lista, cantidad_disponible INTO v_precio, v_stock
    FROM articulo 
    WHERE codigo_producto = p_codigo_producto 
    FOR UPDATE;

    IF v_stock < p_cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para procesar la transacción.';
    END IF;

    SELECT estado_id INTO v_estado_id FROM estado_envio WHERE nombre = 'Pendiente' LIMIT 1;
    v_total := v_precio * p_cantidad;


    INSERT INTO pedido (f_transaccion, total, cc_usuario, estado_id)
    VALUES (CURRENT_TIMESTAMP, v_total, p_cc_usuario, v_estado_id)
    RETURNING id_pedido INTO p_id_pedido;


    INSERT INTO pedido_articulo (id_pedido, codigo_producto, cantidad_vendida, precio_facturado)
    VALUES (p_id_pedido, p_codigo_producto, p_cantidad, v_precio);


    UPDATE articulo 
    SET cantidad_disponible = cantidad_disponible - p_cantidad
    WHERE codigo_producto = p_codigo_producto;


    INSERT INTO factura_pago (id_pedido, metodo_pago, fecha_pago, valor_pagado, estado_pago)
    VALUES (p_id_pedido, p_metodo_pago::metodo_pago_enum, CURRENT_TIMESTAMP, v_total, 'Aprobado');

END;
$$;



CREATE OR REPLACE PROCEDURE sp_actualizar_inventario_bodega(
    p_codigo_producto INT,
    p_id_bodega_origen INT,
    p_id_bodega_destino INT,
    p_cantidad INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_stock_origen INT;
BEGIN
    SELECT stock_actual INTO v_stock_origen 
    FROM inventario_bodega
    WHERE codigo_producto = p_codigo_producto AND id_bodega = p_id_bodega_origen 
    FOR UPDATE;

    IF v_stock_origen IS NULL OR v_stock_origen < p_cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente en la bodega de origen.';
    END IF;


    UPDATE inventario_bodega 
    SET stock_actual = stock_actual - p_cantidad
    WHERE codigo_producto = p_codigo_producto AND id_bodega = p_id_bodega_origen;

    INSERT INTO inventario_bodega (codigo_producto, id_bodega, stock_actual)
    VALUES (p_codigo_producto, p_id_bodega_destino, p_cantidad)
    ON CONFLICT (codigo_producto, id_bodega)
    DO UPDATE SET stock_actual = inventario_bodega.stock_actual + EXCLUDED.stock_actual;

END;
$$;



DROP USER IF EXISTS admin_db;
DROP USER IF EXISTS cajero_app;
DROP ROLE IF EXISTS rol_administrador_db;
DROP ROLE IF EXISTS rol_cajero_app;


CREATE ROLE rol_administrador_db SUPERUSER CREATEDB CREATEROLE;
CREATE ROLE rol_cajero_app;


GRANT USAGE ON SCHEMA public TO rol_cajero_app;
GRANT SELECT, INSERT, UPDATE ON TABLE pedido TO rol_cajero_app;
GRANT SELECT, INSERT, UPDATE ON TABLE pedido_articulo TO rol_cajero_app;
GRANT SELECT, INSERT ON TABLE factura_pago TO rol_cajero_app;
GRANT SELECT ON TABLE articulo TO rol_cajero_app;
GRANT SELECT ON TABLE usuario TO rol_cajero_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO rol_cajero_app;


CREATE USER admin_db WITH PASSWORD 'AdminPass2026!';
CREATE USER cajero_app WITH PASSWORD 'CajeroPass2026!';


GRANT rol_administrador_db TO admin_db;
GRANT rol_cajero_app TO cajero_app;


CALL sp_registrar_pedido_completo(11223344, 1, 2, 'Tarjeta', NULL);


SELECT * FROM pedido;
SELECT * FROM pedido_articulo;
SELECT * FROM factura_pago;


UPDATE articulo SET precio_lista = 3600000.00 WHERE codigo_producto = 1;
SELECT * FROM auditoria_precios;
