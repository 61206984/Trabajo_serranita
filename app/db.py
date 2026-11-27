"""Conexión a MySQL y helper de transacciones. Solo esta capa habla con la base de datos."""
from contextlib import contextmanager

import mysql.connector

from app.config import cargar_config


def conectar():
    cfg = cargar_config()
    return mysql.connector.connect(
        host=cfg.db_host,
        port=cfg.db_port,
        database=cfg.db_name,
        user=cfg.db_user,
        password=cfg.db_pass,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
        autocommit=False,
    )


@contextmanager
def transaccion():
    """Abre una conexión, confirma si todo sale bien y revierte si hay error."""
    conn = conectar()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def consultar(sql: str, params: tuple = ()) -> list[dict]:
    """Lectura simple: abre, consulta y cierra la conexión. Devuelve filas como diccionarios."""
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def consultar_uno(sql: str, params: tuple = ()) -> dict | None:
    filas = consultar(sql, params)
    return filas[0] if filas else None
