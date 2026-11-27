-- Usuario propio de la aplicación (no root). Cambie la contraseña antes de usarlo.
CREATE USER IF NOT EXISTS 'serranita_app'@'127.0.0.1' IDENTIFIED BY 'CAMBIAR_ESTA_CLAVE';
GRANT SELECT, INSERT, UPDATE, DELETE ON serranita_ventas.* TO 'serranita_app'@'127.0.0.1';
FLUSH PRIVILEGES;
