"""P14 Reporte de ventas (Gerente). Medidas y textos del Figma (1280×800). Los datos son de ejemplo."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import nueva_tabla, texto

# (código, producto, unidades, ventas)
VENTAS = [
    ("LE-1L", "Leche entera 1 litro", 300, 1440.00),
    ("QF-500", "Queso fresco 500 g", 96, 1392.00),
    ("HL-1L", "Helado de vainilla 1 litro", 36, 576.00),
    ("YG-1L", "Yogur frutado 1 litro", 54, 529.20),
    ("MJ-1K", "Manjar blanco 1 kg", 22, 396.00),
]
PEDIDOS_CONSIDERADOS = 41


class PantallaReporteVentas(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        unidades = sum(v[2] for v in VENTAS)
        ventas = round(sum(v[3] for v in VENTAS), 2)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Reporte de ventas", "Ventas por rango de fechas, producto, cliente y vendedor"))
        raiz.addWidget(self._filtros())
        raiz.addLayout(self._indicadores(ventas, unidades))
        raiz.addWidget(self._tabla(ventas, unidades))
        ayuda = QLabel("El total del reporte coincide con la suma de los pedidos considerados.")
        ayuda.setObjectName("ayuda")
        raiz.addWidget(ayuda)
        raiz.addStretch(1)

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        h.addLayout(b.etiquetado("Desde", QLineEdit("01/11/2026")), 0)
        h.addLayout(b.etiquetado("Hasta", QLineEdit("27/11/2026")), 0)
        h.addLayout(b.etiquetado("Producto", b.desplegable(["Todos"]), 160))
        h.addLayout(b.etiquetado("Cliente", b.desplegable(["Todos"]), 160))
        h.addLayout(b.etiquetado("Vendedor", b.desplegable(["Todos"]), 140))
        h.addStretch(1)
        h.addWidget(b.boton("Generar reporte"), 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def _kpi(self, titulo: str, valor: str) -> QFrame:
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(4)
        t = QLabel(titulo)
        t.setObjectName("secundario")
        n = QLabel(valor)
        n.setObjectName("total")
        v.addWidget(t)
        v.addWidget(n)
        return tarjeta

    def _indicadores(self, ventas: float, unidades: int) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(16)
        h.addWidget(self._kpi("Total vendido", f"S/ {ventas:,.2f}"), 1)
        h.addWidget(self._kpi("Pedidos considerados", str(PEDIDOS_CONSIDERADOS)), 1)
        h.addWidget(self._kpi("Unidades vendidas", str(unidades)), 1)
        return h

    def _tabla(self, ventas: float, unidades: int):
        tabla = nueva_tabla(["Código", "Producto", "Unidades", "Ventas"], len(VENTAS) + 1)
        for fila, (codigo, nombre, uds, importe) in enumerate(VENTAS):
            tabla.setItem(fila, 0, texto(codigo))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(str(uds), derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {importe:,.2f}", derecha=True))
        total = len(VENTAS)
        tabla.setItem(total, 1, texto("Total del reporte"))
        tabla.setItem(total, 2, texto(str(unidades), derecha=True))
        tabla.setItem(total, 3, texto(f"S/ {ventas:,.2f}", derecha=True))
        return tabla
