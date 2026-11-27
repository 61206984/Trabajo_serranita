"""Conversión de fechas de la UI (dd/mm/aaaa) a objetos date. Devuelve None si el texto es inválido."""
from datetime import date, datetime


def parse_fecha(texto: str) -> date | None:
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        return None
