"""Genera hashes bcrypt reales para los usuarios de prueba del seed.

Uso:  python scripts/crear_usuarios.py
Lee la conexión de .env (DB_HOST, DB_NAME, DB_USER, DB_PASS).
Las contraseñas de prueba son solo para el prototipo local.
"""
import os
import sys

# Permite ejecutarlo como `python scripts/crear_usuarios.py` desde cualquier carpeta.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bcrypt  # noqa: E402
import mysql.connector  # noqa: E402

from app.config import cargar_config  # noqa: E402

# Contraseñas de prueba (solo prototipo local). Ver README.
CONTRASENAS = {
    "crios": "vendedor2026",
    "lparedes": "vendedor2026",
    "almacen1": "almacen2026",
    "gerencia1": "gerencia2026",
}


def main() -> None:
    cfg = cargar_config()
    conn = mysql.connector.connect(
        host=cfg.db_host, database=cfg.db_name,
        user=cfg.db_user, password=cfg.db_pass,
    )
    try:
        cur = conn.cursor()
        for usuario, clave in CONTRASENAS.items():
            hash_ = bcrypt.hashpw(clave.encode("utf-8"), bcrypt.gensalt(rounds=10))
            cur.execute(
                "UPDATE usuario SET password_hash = %s WHERE username = %s",
                (hash_.decode("utf-8"), usuario),
            )
            print(f"{usuario}: hash actualizado ({cur.rowcount} fila)")
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
