"""Consultas del reporte de ventas (RF-15). Excluye pedidos Cancelados."""
from app.db import consultar, consultar_uno


def resumen(desde, hasta) -> dict:
    return consultar_uno(
        """SELECT COUNT(*) AS pedidos, COALESCE(SUM(total), 0) AS total
             FROM pedido
            WHERE estado <> 'Cancelado'
              AND fecha_pedido >= %s AND fecha_pedido < DATE_ADD(%s, INTERVAL 1 DAY)""",
        (desde, hasta),
    )


def ventas_por_producto(desde, hasta) -> list[dict]:
    return consultar(
        """SELECT pr.codigo, pr.nombre, SUM(d.cantidad) AS unidades, SUM(d.subtotal) AS ventas
             FROM pedido pe
             JOIN detalle_pedido d ON d.id_pedido = pe.id_pedido
             JOIN producto pr ON pr.id_producto = d.id_producto
            WHERE pe.estado <> 'Cancelado'
              AND pe.fecha_pedido >= %s AND pe.fecha_pedido < DATE_ADD(%s, INTERVAL 1 DAY)
            GROUP BY pr.id_producto, pr.codigo, pr.nombre
            ORDER BY ventas DESC""",
        (desde, hasta),
    )
