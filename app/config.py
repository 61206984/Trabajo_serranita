"""Lee la configuración de la base de datos desde .env (nunca credenciales en el código)."""
from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str


def cargar_config() -> Config:
    load_dotenv()
    cfg = Config(
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "3306")),
        db_name=os.getenv("DB_NAME", "serranita_ventas"),
        db_user=os.getenv("DB_USER", ""),
        db_pass=os.getenv("DB_PASS", ""),
    )
    if not cfg.db_user or not cfg.db_pass:
        raise RuntimeError("Falta DB_USER o DB_PASS en .env (vea .env.example)")
    if cfg.db_host not in ("127.0.0.1", "localhost"):
        # El prototipo es local: no se conecta a ningún otro equipo.
        raise RuntimeError("DB_HOST debe ser 127.0.0.1 en el prototipo local")
    return cfg
