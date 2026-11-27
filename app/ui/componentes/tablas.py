"""Tabla de datos del Figma (encabezado 40 px, filas 48 px) y celdas auxiliares. Sin colores propios."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem, QWidget,
)

from app.estilos import tokens as t


def nueva_tabla(columnas: list[str], filas: int) -> QTableWidget:
    tabla = QTableWidget(filas, len(columnas))
    tabla.setObjectName("tablaDatos")
    tabla.setHorizontalHeaderLabels(columnas)
    tabla.verticalHeader().setVisible(False)
    tabla.setShowGrid(False)
    tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
    tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    tabla.setFixedHeight(40 + t.ROW_HEIGHT * filas + 2)
    return tabla


def texto(valor: str, derecha: bool = False, color: str | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(valor)
    alineacion = Qt.AlignmentFlag.AlignVCenter | (
        Qt.AlignmentFlag.AlignRight if derecha else Qt.AlignmentFlag.AlignLeft)
    item.setTextAlignment(alineacion)
    if color:
        item.setForeground(QColor(color))
    return item


def celda(widget: QWidget, derecha: bool = False) -> QWidget:
    cont = QWidget()
    h = QHBoxLayout(cont)
    h.setContentsMargins(8, 0, 8, 0)
    if derecha:
        h.addStretch(1)
    h.addWidget(widget)
    if not derecha:
        h.addStretch(1)
    return cont
