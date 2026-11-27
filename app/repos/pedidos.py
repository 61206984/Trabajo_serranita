"""Acceso a datos de pedidos (RF-09 a RF-14). Solo SQL parametrizado."""
from app.db import consultar, consultar_uno


def insertar_cabecera(conn, id_cliente: int, id_vendedor: int, observaciones: str | None) -> int:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO pedido (id_cliente, id_vendedor, estado, total, observaciones)
           VALUES (%s, %s, 'Pendiente', 0, %s)""",
        (id_cliente, id_vendedor, observaciones),
    )
    return cur.lastrowid


def insertar_detalle(conn, id_pedido: int, id_producto: int, cantidad, precio_unitario) -> None:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO detalle_pedido (id_pedido, id_producto, cantidad, precio_unitario)
           VALUES (%s, %s, %s, %s)""",
        (id_pedido, id_producto, cantidad, precio_unitario),
    )


def actualizar_total(conn, id_pedido: int) -> None:
    # RN-06: el total es la suma de los subtotales del detalle.
    cur = conn.cursor()
    cur.execute(
        """UPDATE pedido p
              SET p.total = (SELECT COALESCE(SUM(d.subtotal), 0)
                               FROM detalle_pedido d WHERE d.id_pedido = p.id_pedido)
            WHERE p.id_pedido = %s""",
        (id_pedido,),
    )


def obtener_estado(conn, id_pedido: int) -> dict | None:
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_pedido, estado FROM pedido WHERE id_pedido = %s FOR UPDATE", (id_pedido,))
    return cur.fetchone()


def actualizar_estado(conn, id_pedido: int, estado: str) -> None:
    cur = conn.cursor()
    cur.execute("UPDATE pedido SET estado = %s WHERE id_pedido = %s", (estado, id_pedido))


def lineas(conn, id_pedido: int) -> list[dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """SELECT d.id_producto, d.cantidad, d.precio_unitario, p.codigo, p.nombre
             FROM detalle_pedido d JOIN producto p ON p.id_producto = d.id_producto
            WHERE d.id_pedido = %s""",
        (id_pedido,),
    )
    return cur.fetchall()


def cabecera(id_pedido: int) -> dict | None:
    return consultar_uno(
        """SELECT pe.id_pedido, pe.fecha_pedido, pe.estado, pe.total, pe.observaciones,
                  pe.id_cliente, c.nombre AS cliente, c.tipo_doc, c.nro_doc, c.telefono,
                  CONCAT(v.nombres, ' ', v.apellidos) AS vendedor
             FROM pedido pe
             JOIN cliente c ON c.id_cliente = pe.id_cliente
             JOIN vendedor v ON v.id_vendedor = pe.id_vendedor
            WHERE pe.id_pedido = %s""",
        (id_pedido,),
    )


def detalle(id_pedido: int) -> list[dict]:
    return consultar(
        """SELECT d.id_producto, p.codigo, p.nombre, d.cantidad, d.precio_unitario, d.subtotal, p.stock
             FROM detalle_pedido d JOIN producto p ON p.id_producto = d.id_producto
            WHERE d.id_pedido = %s ORDER BY d.id_detalle""",
        (id_pedido,),
    )


def listar(estado: str | None = None, texto: str = "", desde=None, hasta=None) -> list[dict]:
    condiciones, params = ["1 = 1"], []
    if estado and estado != "Todos":
        condiciones.append("pe.estado = %s")
        params.append(estado)
    if texto.strip():
        condiciones.append("(c.nombre LIKE %s OR c.nro_doc LIKE %s)")
        like = f"%{texto.strip()}%"
        params += [like, like]
    if desde:
        condiciones.append("pe.fecha_pedido >= %s")
        params.append(desde)
    if hasta:
        condiciones.append("pe.fecha_pedido < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.append(hasta)
    return consultar(
        f"""SELECT pe.id_pedido, pe.fecha_pedido, pe.estado, pe.total,
                   c.nombre AS cliente, CONCAT(v.nombres, ' ', v.apellidos) AS vendedor
              FROM pedido pe
              JOIN cliente c ON c.id_cliente = pe.id_cliente
              JOIN vendedor v ON v.id_vendedor = pe.id_vendedor
             WHERE {' AND '.join(condiciones)}
             ORDER BY pe.fecha_pedido DESC, pe.id_pedido DESC
             LIMIT 200""",
        tuple(params),
    )


def total_pedido(conn, id_pedido: int):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT total FROM pedido WHERE id_pedido = %s", (id_pedido,))
    fila = cur.fetchone()
    return fila["total"] if fila else None
