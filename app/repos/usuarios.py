"""Acceso a datos de usuarios. Solo SQL parametrizado."""
from dataclasses import dataclass

from app.db import conectar


@dataclass(frozen=True)
class UsuarioDatos:
    id_usuario: int
    username: str
    password_hash: str
    rol: str
    id_vendedor: int | None
    activo: bool


def buscar_por_username(username: str) -> UsuarioDatos | None:
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT u.id_usuario, u.username, u.password_hash, r.nombre AS rol,
                      u.id_vendedor, u.activo
                 FROM usuario u JOIN rol r ON r.id_rol = u.id_rol
                WHERE u.username = %s""",
            (username,),
        )
        fila = cur.fetchone()
    finally:
        conn.close()
    if fila is None:
        return None
    return UsuarioDatos(
        id_usuario=fila["id_usuario"],
        username=fila["username"],
        password_hash=fila["password_hash"],
        rol=fila["rol"],
        id_vendedor=fila["id_vendedor"],
        activo=bool(fila["activo"]),
    )
