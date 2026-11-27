-- Lácteos La Serranita: esquema de la base de datos (Cap. V del informe, 7 tablas)
-- Motor: MySQL 8.4 LTS (compatible con MariaDB 10.11). Juego de caracteres utf8mb4.

CREATE DATABASE IF NOT EXISTS serranita_ventas
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE serranita_ventas;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS detalle_pedido;
DROP TABLE IF EXISTS pedido;
DROP TABLE IF EXISTS producto;
DROP TABLE IF EXISTS cliente;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS vendedor;
DROP TABLE IF EXISTS rol;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE rol (
  id_rol      INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(30) NOT NULL UNIQUE          -- Vendedor, Almacenero, Gerente
) ENGINE=InnoDB;

CREATE TABLE vendedor (
  id_vendedor INT AUTO_INCREMENT PRIMARY KEY,
  dni         CHAR(8) NOT NULL UNIQUE,
  nombres     VARCHAR(80) NOT NULL,
  apellidos   VARCHAR(80) NOT NULL,
  telefono    VARCHAR(15) NULL,
  activo      BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT ck_vendedor_dni CHECK (dni REGEXP '^[0-9]{8}$')
) ENGINE=InnoDB;

-- Un usuario tiene un solo rol (SUP-03) y como máximo un vendedor (1 : 0..1).
CREATE TABLE usuario (
  id_usuario    INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(40) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,            -- bcrypt; nunca texto plano (RNF-02)
  id_rol        INT NOT NULL,
  id_vendedor   INT NULL UNIQUE,                  -- solo el rol Vendedor lo usa
  activo        BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_usuario_rol      FOREIGN KEY (id_rol)      REFERENCES rol(id_rol),
  CONSTRAINT fk_usuario_vendedor FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor),
  CONSTRAINT ck_usuario_vendedor CHECK (
    (id_rol = 1 AND id_vendedor IS NOT NULL) OR (id_rol <> 1 AND id_vendedor IS NULL)
  )
) ENGINE=InnoDB;

CREATE TABLE cliente (
  id_cliente     INT AUTO_INCREMENT PRIMARY KEY,
  tipo_doc       CHAR(3) NOT NULL,                -- 'DNI' o 'RUC'
  nro_doc        VARCHAR(11) NOT NULL UNIQUE,     -- RN-01
  nombre         VARCHAR(100) NOT NULL,
  telefono       VARCHAR(15) NULL,
  email          VARCHAR(100) NULL,
  direccion      VARCHAR(200) NULL,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  activo         BOOLEAN NOT NULL DEFAULT TRUE,   -- baja lógica (RN-07)
  CONSTRAINT ck_cliente_doc CHECK (
    (tipo_doc = 'DNI' AND nro_doc REGEXP '^[0-9]{8}$') OR
    (tipo_doc = 'RUC' AND nro_doc REGEXP '^[0-9]{11}$')
  )
) ENGINE=InnoDB;

CREATE TABLE producto (
  id_producto  INT AUTO_INCREMENT PRIMARY KEY,
  codigo       VARCHAR(20) NOT NULL UNIQUE,
  nombre       VARCHAR(100) NOT NULL,
  categoria    VARCHAR(50) NULL,
  precio_unit  DECIMAL(10,2) NOT NULL,
  unidad_medida VARCHAR(20) NOT NULL,
  stock        DECIMAL(10,2) NOT NULL DEFAULT 0,
  activo       BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT ck_producto_precio CHECK (precio_unit > 0),   -- RN-02
  CONSTRAINT ck_producto_stock  CHECK (stock >= 0)          -- RN-03
) ENGINE=InnoDB;

CREATE TABLE pedido (
  id_pedido    INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente   INT NOT NULL,
  id_vendedor  INT NOT NULL,
  fecha_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado       ENUM('Pendiente','Confirmado','Entregado','Cancelado')
               NOT NULL DEFAULT 'Pendiente',                -- RN-04
  total        DECIMAL(12,2) NOT NULL DEFAULT 0,            -- RN-06
  observaciones TEXT NULL,
  CONSTRAINT ck_pedido_total CHECK (total >= 0),
  CONSTRAINT fk_pedido_cliente  FOREIGN KEY (id_cliente)  REFERENCES cliente(id_cliente)   ON DELETE RESTRICT,
  CONSTRAINT fk_pedido_vendedor FOREIGN KEY (id_vendedor) REFERENCES vendedor(id_vendedor) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_pedido_estado_fecha ON pedido (estado, fecha_pedido);

CREATE TABLE detalle_pedido (
  id_detalle      INT AUTO_INCREMENT PRIMARY KEY,
  id_pedido       INT NOT NULL,
  id_producto     INT NOT NULL,
  cantidad        DECIMAL(10,2) NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal        DECIMAL(12,2) AS (cantidad * precio_unitario) STORED,   -- RN-05
  CONSTRAINT uq_detalle_pedido_producto UNIQUE (id_pedido, id_producto),
  CONSTRAINT ck_detalle_cantidad CHECK (cantidad > 0),
  CONSTRAINT ck_detalle_precio   CHECK (precio_unitario > 0),
  CONSTRAINT fk_detalle_pedido   FOREIGN KEY (id_pedido)   REFERENCES pedido(id_pedido)     ON DELETE RESTRICT,
  CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto) ON DELETE RESTRICT
) ENGINE=InnoDB;
