"""P08 Lista de pedidos (vendedor). Medidas y textos del Figma (1280×800).
Los pedidos son de ejemplo del Figma; se reemplazarán con la consulta a la base de datos.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

# (número, fecha, cliente, vendedor, estado, total)
PEDIDOS = [
    ("0042", "27/11/2026", "Minimarket El Mantaro S.A.C.", "Luis Cárdenas", "Pendiente", 318.60),
    ("0041", "27/11/2026", "Bodega Doña Rosa", "Luis Cárdenas", "Confirmado", 96.40),
    ("0040", "26/11/2026", "Restaurante Sabor Huanca E.I.R.L.", "Ana Quispe", "Entregado", 742.00),
    ("0039", "26/11/2026", "Juan Pérez Quispe", "Ana Quispe", "Entregado", 58.00),
    ("0038", "25/11/2026", "Minimarket El Mantaro S.A.C.", "Luis Cárdenas", "Entregado", 410.30),
    ("0037", "25/11/2026", "Panadería San José E.I.R.L.", "Ana Quispe", "Cancelado", 135.00),
    ("0036", "24/11/2026", "Bodega Doña Rosa", "Luis Cárdenas", "Entregado", 87.20),
]


class PantallaListaPedidos(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        nuevo = b.boton("Nuevo pedido", "primario")
        nuevo.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        raiz.addWidget(b.encabezado("Pedidos", "Consulte y filtre los pedidos registrados", accion=nuevo))
        raiz.addWidget(self._filtros())
        raiz.addWidget(self._tabla())
        raiz.addLayout(self._pie())
        raiz.addStretch(1)

    def _campo(self, etiqueta: str, entrada, ancho: int | None = None) -> QVBoxLayout:
        v = QVBoxLayout()
        v.setSpacing(6)
        lbl = QLabel(etiqueta)
        lbl.setObjectName("etiquetaCampo")
        entrada.setFixedHeight(40)
        if ancho:
            entrada.setFixedWidth(ancho)
        v.addWidget(lbl)
        v.addWidget(entrada)
        return v

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        estado = QComboBox()
        estado.addItems(["Todos", "Pendiente", "Confirmado", "Entregado", "Cancelado"])
        cliente = QLineEdit()
        cliente.setPlaceholderText("Buscar por nombre o documento")
        desde = QLineEdit("01/11/2026")
        hasta = QLineEdit("27/11/2026")
        h.addLayout(self._campo("Estado", estado, 180))
        h.addLayout(self._campo("Cliente", cliente), 1)
        h.addLayout(self._campo("Desde", desde, 150))
        h.addLayout(self._campo("Hasta", hasta, 150))
        h.addWidget(b.boton("Filtrar", "primario"), 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def _tabla(self):
        tabla = nueva_tabla(["N.º", "Fecha", "Cliente", "Vendedor", "Estado", "Total"], len(PEDIDOS))
        for fila, (numero, fecha, cliente, vendedor, estado, total) in enumerate(PEDIDOS):
            enlace = b.boton(numero, "enlace")
            enlace.clicked.connect(lambda _=False: self.ir_a("Detalle del pedido"))
            tabla.setCellWidget(fila, 0, celda(enlace))
            tabla.setItem(fila, 1, texto(fecha))
            tabla.setItem(fila, 2, texto(cliente))
            tabla.setItem(fila, 3, texto(vendedor))
            tabla.setCellWidget(fila, 4, celda(b.insignia(estado)))
            tabla.setItem(fila, 5, texto(f"S/ {total:.2f}", derecha=True))
        return tabla

    def _pie(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(8)
        info = QLabel("Mostrando 1–7 de 64 pedidos")
        info.setObjectName("secundario")
        h.addWidget(info)
        h.addStretch(1)
        h.addWidget(b.boton("Anterior", "secundario", deshabilitado=True))
        siguiente = b.boton("Siguiente", "secundario")
        h.addWidget(siguiente)
        return h
