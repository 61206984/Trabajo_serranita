"""Tabla de datos del Figma (encabezado 40 px, filas 48 px) y celdas auxiliares. Sin colores propios."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QTableWidget, QTableWidgetItem, QWidget,
)

from app.estilos import tokens as t


def ajustar_columnas(tabla: QTableWidget, ancho_acciones: int = 170,
                     anchos_fijos: dict[int, int] | None = None) -> None:
    """Columnas fijas (acciones y las que tienen insignias o botones) y elásticas para el resto.

    anchos_fijos: {indice_columna: ancho_px} para columnas con widgets (insignias, botones).
    """
    h = tabla.horizontalHeader()
    h.setMinimumSectionSize(90)
    ultima = tabla.columnCount() - 1
    fijos = dict(anchos_fijos or {})
    fijos[ultima] = ancho_acciones
    for c in range(tabla.columnCount()):
        if c in fijos:
            h.setSectionResizeMode(c, QHeaderView.ResizeMode.Fixed)
            tabla.setColumnWidth(c, fijos[c])
        else:
            h.setSectionResizeMode(c, QHeaderView.ResizeMode.Stretch)


def nueva_tabla(columnas: list[str], filas: int, anchos_fijos: dict[int, int] | None = None) -> QTableWidget:
    tabla = QTableWidget(filas, len(columnas))
    tabla.setObjectName("tablaDatos")
    tabla.setHorizontalHeaderLabels(columnas)
    tabla.verticalHeader().setVisible(False)
    tabla.setShowGrid(False)
    tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
    tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
    ajustar_columnas(tabla, anchos_fijos=anchos_fijos)
    # Hasta 10 filas visibles; el resto se recorre con la barra de la tabla.
    tabla.setFixedHeight(40 + t.ROW_HEIGHT * min(max(filas, 1), 10) + 2)
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
