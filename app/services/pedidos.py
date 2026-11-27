"""Reglas de negocio de pedidos, clientes, productos y stock (RN-01 a RN-08).

La UI llama solo a estas funciones. Cada operación que modifica varias tablas
corre en una sola transacción: si algo falla, se revierte todo (D-06).
"""
import re
from decimal import Decimal

import mysql.connector

from app.db import transaccion
from app.repos import clientes, pedidos, productos


class ErrorNegocio(Exception):
    """Regla de negocio incumplida. El mensaje es apto para mostrar al usuario."""


class DocumentoDuplicado(ErrorNegocio):
    pass


class StockInsuficiente(ErrorNegocio):
    def __init__(self, nombre: str, disponible):
        self.nombre = nombre
        self.disponible = disponible
        super().__init__(f"Stock insuficiente: quedan {_fmt(disponible)} unidades de {nombre}. "
                         "Reduzca la cantidad.")


def _fmt(n) -> str:
    n = float(n)
    return str(int(n)) if n.is_integer() else f"{n:.2f}"


def _dec(valor) -> Decimal:
    return Decimal(str(valor))


# ---------- Clientes (RF-03, RF-04; RN-01, RN-07) ----------

def registrar_cliente(tipo_doc: str, nro_doc: str, nombre: str, telefono: str = "",
                      email: str = "", direccion: str = "") -> int:
    tipo_doc, nro_doc, nombre = tipo_doc.strip().upper(), nro_doc.strip(), nombre.strip()
    if not nombre:
        raise ErrorNegocio("Ingrese el nombre o razón social.")
    if tipo_doc == "DNI" and not re.fullmatch(r"\d{8}", nro_doc):
        raise ErrorNegocio("El DNI debe tener 8 dígitos.")
    if tipo_doc == "RUC" and not re.fullmatch(r"\d{11}", nro_doc):
        raise ErrorNegocio("El RUC debe tener 11 dígitos.")
    if tipo_doc not in ("DNI", "RUC"):
        raise ErrorNegocio("El tipo de documento debe ser DNI o RUC.")
    if clientes.existe_documento(nro_doc):
        raise DocumentoDuplicado("Ya existe un cliente con ese documento. Busque al cliente o corrija el número.")
    try:
        with transaccion() as conn:
            return clientes.insertar(conn, tipo_doc, nro_doc, nombre,
                                     telefono.strip() or None, email.strip() or None,
                                     direccion.strip() or None)
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:
            raise DocumentoDuplicado("Ya existe un cliente con ese documento.") from e
        raise ErrorNegocio("Los datos no cumplen las reglas de la base de datos.") from e


def dar_de_baja_cliente(id_cliente: int) -> None:
    with transaccion() as conn:
        clientes.dar_de_baja(conn, id_cliente)


# ---------- Productos y stock (RF-07, RF-08; RN-02, RN-03) ----------

def registrar_producto(codigo: str, nombre: str, categoria: str, unidad: str, precio) -> int:
    codigo, nombre = codigo.strip().upper(), nombre.strip()
    if not codigo or not nombre:
        raise ErrorNegocio("Código y nombre son obligatorios.")
    try:
        precio = _dec(precio)
    except Exception as e:
        raise ErrorNegocio("El precio debe ser un número.") from e
    if precio <= 0:
        raise ErrorNegocio("El precio debe ser mayor que cero (RN-02).")
    if productos.existe_codigo(codigo):
        raise ErrorNegocio(f"Ya existe un producto con el código {codigo}.")
    with transaccion() as conn:
        return productos.insertar(conn, codigo, nombre, categoria, precio, unidad)


def ingresar_stock(id_producto: int, cantidad) -> None:
    cantidad = _dec(cantidad)
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad a ingresar debe ser mayor que cero.")
    with transaccion() as conn:
        if productos.obtener(id_producto, conn, bloquear=True) is None:
            raise ErrorNegocio("El producto no existe.")
        productos.ajustar_stock(conn, id_producto, cantidad)


# ---------- Pedidos (RF-09 a RF-13; RN-03 a RN-08) ----------

def crear_pedido(id_cliente: int, id_vendedor: int, items: list[tuple[int, float]],
                 observaciones: str | None = None) -> tuple[int, Decimal]:
    """Registra un pedido Pendiente. El precio y el total los calcula el servidor (RN-05, RN-06).

    items: lista de (id_producto, cantidad). Un pedido Pendiente no descuenta stock (D-06),
    pero sí exige stock suficiente al registrarlo (RF-10).
    """
    if not items:
        raise ErrorNegocio("Agregue al menos un producto al pedido.")
    with transaccion() as conn:
        cliente = clientes.obtener(id_cliente, conn)
        if cliente is None:
            raise ErrorNegocio("El cliente no existe.")
        if not cliente["activo"]:
            raise ErrorNegocio("El cliente está inactivo. Seleccione otro cliente.")  # RN-08
        id_pedido = pedidos.insertar_cabecera(conn, id_cliente, id_vendedor, observaciones or None)
        for id_producto, cantidad in items:
            cantidad = _dec(cantidad)
            if cantidad <= 0:
                raise ErrorNegocio("Las cantidades deben ser mayores que cero.")
            p = productos.obtener(id_producto, conn, bloquear=True)
            if p is None or not p["activo"]:
                raise ErrorNegocio("Un producto del pedido ya no está disponible.")
            if p["stock"] < cantidad:
                raise StockInsuficiente(p["nombre"], p["stock"])
            # RN-02/precio vigente: se toma el precio de la BD, no de la pantalla (IRQ-05).
            pedidos.insertar_detalle(conn, id_pedido, id_producto, cantidad, p["precio_unit"])
        pedidos.actualizar_total(conn, id_pedido)
        total = pedidos.total_pedido(conn, id_pedido)
    return id_pedido, total


def confirmar_pedido(id_pedido: int) -> None:
    """Pendiente -> Confirmado. Descuenta el stock de cada línea en una transacción (RF-12)."""
    with transaccion() as conn:
        ped = pedidos.obtener_estado(conn, id_pedido)
        if ped is None:
            raise ErrorNegocio("El pedido no existe.")
        if ped["estado"] != "Pendiente":
            raise ErrorNegocio("Este pedido ya no puede cambiar a ese estado.")
        for linea in pedidos.lineas(conn, id_pedido):
            p = productos.obtener(linea["id_producto"], conn, bloquear=True)
            if p["stock"] < linea["cantidad"]:
                raise StockInsuficiente(p["nombre"], p["stock"])
            productos.ajustar_stock(conn, linea["id_producto"], -linea["cantidad"])
        pedidos.actualizar_estado(conn, id_pedido, "Confirmado")


def entregar_pedido(id_pedido: int) -> None:
    """Confirmado -> Entregado. Estado final (RN-04)."""
    with transaccion() as conn:
        ped = pedidos.obtener_estado(conn, id_pedido)
        if ped is None:
            raise ErrorNegocio("El pedido no existe.")
        if ped["estado"] != "Confirmado":
            raise ErrorNegocio("Solo se puede entregar un pedido confirmado.")
        pedidos.actualizar_estado(conn, id_pedido, "Entregado")


def cancelar_pedido(id_pedido: int) -> None:
    """Pendiente o Confirmado -> Cancelado. Si estaba Confirmado, restituye el stock (RF-13)."""
    with transaccion() as conn:
        ped = pedidos.obtener_estado(conn, id_pedido)
        if ped is None:
            raise ErrorNegocio("El pedido no existe.")
        if ped["estado"] not in ("Pendiente", "Confirmado"):
            raise ErrorNegocio("Un pedido entregado o cancelado no se puede cancelar.")
        if ped["estado"] == "Confirmado":
            for linea in pedidos.lineas(conn, id_pedido):
                productos.obtener(linea["id_producto"], conn, bloquear=True)
                productos.ajustar_stock(conn, linea["id_producto"], linea["cantidad"])
        pedidos.actualizar_estado(conn, id_pedido, "Cancelado")
