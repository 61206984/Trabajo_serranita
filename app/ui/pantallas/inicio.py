"""P02 Panel de inicio. Igual para los tres roles; cambia el menú lateral (ventana.py).
Indicadores y pedidos recientes salen de la base de datos."""
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QHeaderView, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.estilos import tokens as t
from app.repos import pedidos as repo_pedidos
from app.repos import productos as repo_productos
from app.ui.componentes import basicos as b

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "setiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def _saludo(hora: int) -> str:
    if hora < 12:
        return "Buenos días"
    if hora < 19:
        return "Buenas tardes"
    return "Buenas noches"


def _fecha_larga(f: datetime) -> str:
    return f"{DIAS[f.weekday()].capitalize()} {f.day} de {MESES[f.month - 1]} de {f.year}"


class PantallaInicio(QWidget):
    def __init__(self, nombre: str, ir_a=None, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        ahora = datetime.now()
        primer_nombre = nombre.split()[0] if nombre else ""

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        enc = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(4)
        h1 = QLabel(f"{_saludo(ahora.hour)}, {primer_nombre}")
        h1.setObjectName("titulo")
        h2 = QLabel(f"{_fecha_larga(ahora)} · Resumen de su jornada")
        h2.setStyleSheet(f"font-size: 14px; color: {t.TEXT_SECONDARY};")
        titulos.addWidget(h1)
        titulos.addWidget(h2)
        enc.addLayout(titulos)
        enc.addStretch(1)
        nuevo = b.boton("Nuevo pedido", "primario", 134)
        nuevo.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        enc.addWidget(nuevo)
        raiz.addLayout(enc)

        indicadores = QHBoxLayout()
        indicadores.setSpacing(16)
        for titulo, valor in (
            ("Pedidos de hoy", repo_pedidos.contar(hoy=True)),
            ("Pendientes por confirmar", repo_pedidos.contar(estado="Pendiente")),
            ("Productos con stock bajo", repo_productos.contar_stock_bajo()),
        ):
            indicadores.addWidget(self._indicador(titulo, str(valor)))
        raiz.addLayout(indicadores)

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
        filas = repo_pedidos.recientes(8)
        columnas = ["N.º", "Cliente", "Estado", "Total", ""]
        tabla = QTableWidget(len(filas), len(columnas))
        tabla.setObjectName("tablaDatos")
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.verticalHeader().setVisible(False)
        tabla.setShowGrid(False)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.setFixedHeight(40 + t.ROW_HEIGHT * max(len(filas), 1) + 2)
        for fila, p in enumerate(filas):
            tabla.setItem(fila, 0, QTableWidgetItem(f"{p['id_pedido']:04d}"))
            tabla.setItem(fila, 1, QTableWidgetItem(p["cliente"]))
            tabla.setCellWidget(fila, 2, self._insignia(p["estado"]))
            item_total = QTableWidgetItem(f"S/ {float(p['total']):.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            tabla.setItem(fila, 3, item_total)
            ver = b.boton("Ver detalle", "enlace")
            ver.clicked.connect(lambda _=False, i=p["id_pedido"]: self.ir_a("Detalle del pedido", pedido_id=i))
            tabla.setCellWidget(fila, 4, ver)
        return tabla

    def _insignia(self, estado: str) -> QWidget:
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(8, 0, 8, 0)
        h.addWidget(b.insignia(estado), 0, Qt.AlignmentFlag.AlignLeft)
        h.addStretch(1)
        return cont
