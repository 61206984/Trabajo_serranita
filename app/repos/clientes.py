"""Acceso a datos de clientes (RF-03 a RF-05). Solo SQL parametrizado."""
from app.db import consultar, consultar_uno

_COLUMNAS = "id_cliente, tipo_doc, nro_doc, nombre, telefono, email, direccion, activo"


def buscar(texto: str = "", limite: int = 50) -> list[dict]:
    like = f"%{texto.strip()}%"
    return consultar(
        f"""SELECT {_COLUMNAS} FROM cliente
             WHERE nro_doc LIKE %s OR nombre LIKE %s
             ORDER BY activo DESC, fecha_registro DESC, nombre
             LIMIT %s""",
        (like, like, limite),
    )


def obtener(id_cliente: int, conn=None) -> dict | None:
    sql = f"SELECT {_COLUMNAS} FROM cliente WHERE id_cliente = %s"
    if conn is None:
        return consultar_uno(sql, (id_cliente,))
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, (id_cliente,))
    return cur.fetchone()


def existe_documento(nro_doc: str) -> bool:
    return consultar_uno("SELECT 1 AS x FROM cliente WHERE nro_doc = %s", (nro_doc,)) is not None


def insertar(conn, tipo_doc, nro_doc, nombre, telefono, email, direccion) -> int:
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO cliente (tipo_doc, nro_doc, nombre, telefono, email, direccion)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (tipo_doc, nro_doc, nombre, telefono, email, direccion),
    )
    return cur.lastrowid


def dar_de_baja(conn, id_cliente: int) -> None:
    # Baja lógica (RN-07): nunca se elimina un cliente con historial.
    cur = conn.cursor()
    cur.execute("UPDATE cliente SET activo = FALSE WHERE id_cliente = %s", (id_cliente,))
