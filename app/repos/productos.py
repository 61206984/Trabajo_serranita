"""Acceso a datos de productos y stock (RF-06 a RF-08). Solo SQL parametrizado."""
from app.db import consultar, consultar_uno

UMBRAL_STOCK_BAJO = 5
_COLUMNAS = "id_producto, codigo, nombre, categoria, precio_unit, unidad_medida, stock, activo"


def listar(texto: str = "", categoria: str | None = None, estado: str | None = None) -> list[dict]:
    condiciones, params = ["activo = TRUE"], []
    if texto.strip():
        condiciones.append("(codigo LIKE %s OR nombre LIKE %s)")
        like = f"%{texto.strip()}%"
        params += [like, like]
    if categoria and categoria != "Todas":
        condiciones.append("categoria = %s")
        params.append(categoria)
    if estado == "Disponible":
        condiciones.append("stock > %s")
        params.append(UMBRAL_STOCK_BAJO)
    elif estado == "Stock bajo":
        condiciones.append("stock > 0 AND stock <= %s")
        params.append(UMBRAL_STOCK_BAJO)
    elif estado == "Sin stock":
        condiciones.append("stock = 0")
    return consultar(
        f"SELECT {_COLUMNAS} FROM producto WHERE {' AND '.join(condiciones)} ORDER BY nombre",
        tuple(params),
    )


def categorias() -> list[str]:
    return [f["categoria"] for f in consultar(
        "SELECT DISTINCT categoria FROM producto WHERE categoria IS NOT NULL ORDER BY categoria")]


def obtener(id_producto: int, conn=None, bloquear: bool = False) -> dict | None:
    sql = f"SELECT {_COLUMNAS} FROM producto WHERE id_producto = %s"
    if bloquear:
        sql += " FOR UPDATE"  # bloqueo de fila dentro de la transacción (evita carreras de stock)
    if conn is None:
        return consultar_uno(sql, (id_producto,))
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, (id_producto,))
    return cur.fetchone()


def existe_codigo(codigo: str) -> bool:
    return consultar_uno("SELECT 1 AS x FROM producto WHERE codigo = %s", (codigo,)) is not None


def insertar(conn, codigo, nombre, categoria, precio_unit, unidad_medida) -> int:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO producto (codigo, nombre, categoria, precio_unit, unidad_medida, stock)
           VALUES (%s, %s, %s, %s, %s, 0)""",
        (codigo, nombre, categoria, precio_unit, unidad_medida),
    )
    return cur.lastrowid


def ajustar_stock(conn, id_producto: int, delta) -> None:
    """Suma (delta > 0) o resta (delta < 0) stock. El CHECK stock >= 0 de la BD también lo protege."""
    cur = conn.cursor()
    cur.execute("UPDATE producto SET stock = stock + %s WHERE id_producto = %s", (delta, id_producto))
