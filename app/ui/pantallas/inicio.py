"""P02 Panel de inicio. Es la misma pantalla para los tres roles (Vendedor, Almacenero y Gerente);
lo que cambia es el menú lateral y el nombre de la persona (ventana.py).

Medidas del Figma: contenido con padding 32, encabezado de 56 px, tres indicadores de 126 px
de alto con borde #E5E7EB y radio 8, tabla de pedidos con encabezado de 40 px y filas de 48 px.

Los números y filas son de ejemplo del Figma: se reemplazarán cuando exista el módulo de pedidos.
"""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.estilos import tokens as t

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "setiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

PEDIDOS_EJEMPLO = [
    ("0042", "Minimarket El Mantaro S.A.C.", "Pendiente", "S/ 318.60"),
    ("0041", "Bodega Doña Rosa", "Confirmado", "S/ 96.40"),
    ("0040", "Restaurante Sabor Huanca E.I.R.L.", "Entregado", "S/ 742.00"),
    ("0039", "Juan Pérez Quispe", "Entregado", "S/ 58.00"),
]


def _saludo(hora: int) -> str:
    if hora < 12:
        return "Buenos días"
    if hora < 19:
        return "Buenas tardes"
    return "Buenas noches"


def _fecha_larga(f: datetime) -> str:
    return f"{DIAS[f.weekday()].capitalize()} {f.day} de {MESES[f.month - 1]} de {f.year}"


class PantallaInicio(QWidget):
    def __init__(self, nombre: str, parent=None):
        super().__init__(parent)
        ahora = datetime.now()
        primer_nombre = nombre.split()[0] if nombre else ""

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        # Encabezado: saludo + botón de acción principal
        enc = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(4)
        h1 = QLabel(f"{_saludo(ahora.hour)}, {primer_nombre}")
        h1.setObjectName("titulo")
        h2 = QLabel(f"{_fecha_larga(ahora)} · Resumen de su jornada")
        h2.setObjectName("subtitulo")
        h2.setStyleSheet(f"font-size: 14px; color: {t.TEXT_SECONDARY};")
        titulos.addWidget(h1)
        titulos.addWidget(h2)
        enc.addLayout(titulos)
        enc.addStretch(1)
        nuevo = QPushButton("Nuevo pedido")
        nuevo.setProperty("variante", "primario")
        nuevo.setFixedWidth(134)
        enc.addWidget(nuevo)
        raiz.addLayout(enc)

        # Indicadores
        indicadores = QHBoxLayout()
        indicadores.setSpacing(16)
        for titulo, valor in (("Pedidos de hoy", "12"),
                              ("Pendientes por confirmar", "8"),
                              ("Productos con stock bajo", "3")):
            indicadores.addWidget(self._indicador(titulo, valor))
        raiz.addLayout(indicadores)

        # Pedidos recientes
        sub = QLabel("Pedidos recientes")
        sub.setStyleSheet("font-size: 18px; font-weight: 600;")
        raiz.addWidget(sub)
        raiz.addWidget(self._tabla_pedidos())
        raiz.addStretch(1)

    def _indicador(self, titulo: str, valor: str) -> QFrame:
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedHeight(126)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(12)
        etiqueta = QLabel(titulo)
        etiqueta.setStyleSheet(f"color: {t.TEXT_SECONDARY};")
        numero = QLabel(valor)
        numero.setStyleSheet("font-size: 24px; font-weight: 600;")
        v.addWidget(etiqueta)
        v.addWidget(numero)
        v.addStretch(1)
        return tarjeta

    def _tabla_pedidos(self) -> QTableWidget:
        columnas = ["N.º", "Cliente", "Estado", "Total", ""]
        tabla = QTableWidget(len(PEDIDOS_EJEMPLO), len(columnas))
        tabla.setObjectName("tablaDatos")
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.verticalHeader().setVisible(False)
        tabla.setShowGrid(False)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
        encabezado = tabla.horizontalHeader()
        encabezado.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.setFixedHeight(40 + t.ROW_HEIGHT * len(PEDIDOS_EJEMPLO) + 2)

        for fila, (numero, cliente, estado, total) in enumerate(PEDIDOS_EJEMPLO):
            tabla.setItem(fila, 0, QTableWidgetItem(numero))
            tabla.setItem(fila, 1, QTableWidgetItem(cliente))
            tabla.setCellWidget(fila, 2, self._insignia(estado))
            item_total = QTableWidgetItem(total)
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabla.setItem(fila, 3, item_total)
            ver = QPushButton("Ver detalle")
            ver.setProperty("variante", "enlace")
            tabla.setCellWidget(fila, 4, ver)
        return tabla

    def _insignia(self, estado: str) -> QWidget:
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(8, 0, 8, 0)
        etiqueta = QLabel(estado)
        etiqueta.setObjectName("insignia")
        etiqueta.setProperty("estado", estado)
        etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        etiqueta.setFixedHeight(28)
        h.addWidget(etiqueta, 0, Qt.AlignmentFlag.AlignLeft)
        h.addStretch(1)
        return cont
