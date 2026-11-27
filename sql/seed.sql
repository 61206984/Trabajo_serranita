-- Datos de ejemplo (ficticios, RES-04). Base: DML del Anexo A del informe.
-- Los hashes de contraseña se reemplazan con scripts/crear_usuarios.py (bcrypt real).
USE serranita_ventas;

INSERT INTO rol (id_rol, nombre) VALUES
  (1, 'Vendedor'),
  (2, 'Almacenero'),
  (3, 'Gerente');

INSERT INTO vendedor (id_vendedor, dni, nombres, apellidos, telefono) VALUES
  (1, '40000001', 'Carla',  'Ríos Soto',   '900000001'),
  (2, '40000002', 'Luis',   'Paredes Vega', '900000002');

-- password_hash provisional: lo reemplaza scripts/crear_usuarios.py
INSERT INTO usuario (id_usuario, username, password_hash, id_rol, id_vendedor) VALUES
  (1, 'crios',     'PENDIENTE', 1, 1),
  (2, 'lparedes',  'PENDIENTE', 1, 2),
  (3, 'almacen1',  'PENDIENTE', 2, NULL),
  (4, 'gerencia1', 'PENDIENTE', 3, NULL);

INSERT INTO cliente (id_cliente, tipo_doc, nro_doc, nombre, telefono, direccion) VALUES
  (1, 'DNI', '70000001',    'Cliente Ficticio Uno',     '910000001', 'Av. Ejemplo 100, Huancayo'),
  (2, 'RUC', '20000000011', 'Bodega Ficticia S.A.C.',   '910000002', 'Jr. Ejemplo 200, Huancayo'),
  (3, 'DNI', '70000003',    'Cliente Ficticio Tres',    NULL,        NULL);

-- Precios del informe. YOG-001 usa 9.80 (la tabla del informe dice 7.50, pero la
-- línea del pedido de ejemplo usa 9.80; se toma el valor coherente con el pedido).
INSERT INTO producto (id_producto, codigo, nombre, categoria, precio_unit, unidad_medida, stock) VALUES
  (1, 'QSO-001', 'Queso fresco 500 g',    'Queso',   18.50, 'unidad', 120),
  (2, 'YOG-001', 'Yogur frutado 1 litro', 'Yogur',    9.80, 'unidad',   3),   -- stock 3 para probar RF-10 (informe: 60)
  (3, 'MJB-001', 'Manjar blanco 250 g',   'Manjar',   7.50, 'unidad',  80),
  (4, 'HEL-001', 'Helado artesanal balde','Helado', 45.00, 'unidad',  25);

INSERT INTO pedido (id_pedido, id_cliente, id_vendedor, estado, total) VALUES
  (1, 1, 1, 'Pendiente', 0);

INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario) VALUES
  (1, 1, 4, 18.50),
  (1, 2, 6,  9.80);

-- Recalcula el total (RN-06) a partir de los subtotales
UPDATE pedido p
   SET p.total = (SELECT COALESCE(SUM(d.subtotal), 0) FROM detalle_pedido d WHERE d.id_pedido = p.id_pedido)
 WHERE p.id_pedido = 1;
