"""Iconos SVG (familia Lucide, licencia ISC) pintados con los colores del sistema de diseño.

Los archivos están en app/ui/recursos/iconos/. El SVG usa currentColor; aquí se reemplaza por el color pedido.
"""
from pathlib import Path

from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from app.estilos import tokens as t

RUTA = Path(__file__).resolve().parent.parent / "recursos" / "iconos"


def icono(nombre: str, color: str = t.TEXT, tamano: int = 18) -> QIcon:
    svg = (RUTA / f"{nombre}.svg").read_text(encoding="utf-8").replace("currentColor", color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    escala = 2  # nítido en pantallas de alta densidad
    pix = QPixmap(tamano * escala, tamano * escala)
    pix.setDevicePixelRatio(escala)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    renderer.render(p, QRectF(0, 0, tamano, tamano))
    p.end()
    return QIcon(pix)


def tamano_icono(tamano: int = 18) -> QSize:
    return QSize(tamano, tamano)
