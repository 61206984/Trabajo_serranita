"""Servicio de autenticación (RF-01, RF-02). No muestra detalles técnicos al usuario."""
import bcrypt

from app.repos import usuarios


class CredencialesInvalidas(Exception):
    """Usuario o contraseña incorrectos. Mismo mensaje para ambos casos (no revela cuál falló)."""


class SesionActual:
    def __init__(self, username: str, rol: str, id_vendedor: int | None):
        self.username = username
        self.rol = rol
        self.id_vendedor = id_vendedor


sesion: SesionActual | None = None


def iniciar_sesion(username: str, password: str) -> SesionActual:
    global sesion
    datos = usuarios.buscar_por_username(username.strip())
    if datos is None or not datos.activo:
        raise CredencialesInvalidas()
    if not bcrypt.checkpw(password.encode("utf-8"), datos.password_hash.encode("utf-8")):
        raise CredencialesInvalidas()
    sesion = SesionActual(datos.username, datos.rol, datos.id_vendedor)
    return sesion


def cerrar_sesion() -> None:
    global sesion
    sesion = None
