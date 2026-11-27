"""P09 Detalle del pedido, estado Pendiente. Medidas y textos del Figma (1280×800).
Los datos son de ejemplo del Figma. «Confirmar pedido» y «Cancelar pedido» cambian el estado;
la lógica (descuento de stock, RN-04 y RN-05) se conectará en el módulo de pedidos.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.estilos import tokens as t
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

CLIENTE = [("Cliente", "Minimarket El Mantaro S.A.C."), ("Documento", "RUC 20601234567"), ("Teléfono", "964 112 233")]

# (código, producto, cantidad, precio, stock)
LINEAS = [
    ("QF-500", "Queso fresco 500 g", 12, 14.50, 120),
    ("YG-1L", "Yogur frutado 1 litro", 3, 9.80, 3),
    ("LE-1L", "Leche entera 1 litro", 24, 4.80, 210),
]
ESTADOS = ["Pendiente", "Confirmado", "Entregado"]
STOCK_BAJO = 5


class PantallaDetallePedido(QWidget):
    def __init__(self, ir_a, numero: str = "0042", parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        total = round(sum(cant * precio for _, _, cant, precio, _ in LINEAS), 2)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addLayout(self._encabezado(numero))

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(24)
        izquierda = QVBoxLayout()
        izquierda.setSpacing(16)
        izquierda.addWidget(self._datos_cliente())
        izquierda.addWidget(self._lineas())
        izquierda.addLayout(self._total(total))
        izquierda.addStretch(1)
        cuerpo.addLayout(izquierda, 1)
        cuerpo.addWidget(self._estado(), 0, Qt.AlignmentFlag.AlignTop)
        raiz.addLayout(cuerpo, 1)

    def _encabezado(self, numero: str) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(16)
        bloque = QVBoxLayout()
        bloque.setSpacing(4)
        titulo = QLabel(f"Pedido N.º {numero}")
        titulo.setObjectName("titulo")
        detalle = QLabel("Registrado el 27/11/2026 · Vendedor: Luis Cárdenas")
        detalle.setObjectName("secundario")
        bloque.addWidget(titulo)
        bloque.addWidget(detalle)
        h.addLayout(bloque)
        h.addStretch(1)
        h.addWidget(b.insignia("Pendiente"))
        volver = b.boton("Volver a pedidos", "secundario")
        volver.clicked.connect(lambda: self.ir_a("Pedidos"))
        h.addWidget(volver)
        return h

    def _datos_cliente(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(32)
        for etiqueta, valor in CLIENTE:
            v = QVBoxLayout()
            v.setSpacing(2)
            lbl = QLabel(etiqueta)
            lbl.setObjectName("ayuda")
            val = QLabel(valor)
            val.setObjectName("valor")
            v.addWidget(lbl)
            v.addWidget(val)
            h.addLayout(v)
        h.addStretch(1)
        return tarjeta

    def _lineas(self):
        tabla = nueva_tabla(["Código", "Producto", "Cant.", "Precio", "Subtotal", "Stock"], len(LINEAS))
        for fila, (codigo, nombre, cant, precio, stock) in enumerate(LINEAS):
            color = t.BADGE["Pendiente"][0] if stock <= STOCK_BAJO else None
            tabla.setItem(fila, 0, texto(codigo))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(str(cant), derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {precio:.2f}", derecha=True))
            tabla.setItem(fila, 4, texto(f"S/ {cant * precio:.2f}", derecha=True))
            tabla.setItem(fila, 5, texto(str(stock), derecha=True, color=color))
        return tabla

    def _total(self, total: float) -> QHBoxLayout:
        h = QHBoxLayout()
        h.addStretch(1)
        etiqueta = QLabel("Total")
        etiqueta.setStyleSheet("font-size: 18px; font-weight: 600;")
        valor = QLabel(f"S/ {total:.2f}")
        valor.setStyleSheet("font-size: 18px; font-weight: 600;")
        h.addWidget(etiqueta)
        h.addSpacing(12)
        h.addWidget(valor)
        return h

    def _estado(self) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(320)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(16)

        titulo = QLabel("Estado del pedido")
        titulo.setStyleSheet("font-size: 18px; font-weight: 600;")
        v.addWidget(titulo)
        for i, nombre in enumerate(ESTADOS):
            fila = QHBoxLayout()
            fila.setSpacing(10)
            marca = QLabel("●" if i == 0 else "○")
            marca.setObjectName("pasoActivo" if i == 0 else "pasoInactivo")
            etiqueta = QLabel(nombre)
            etiqueta.setObjectName("valor" if i == 0 else "secundario")
            fila.addWidget(marca)
            fila.addWidget(etiqueta)
            fila.addStretch(1)
            v.addLayout(fila)

        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet(f"background: {t.BORDER};")
        v.addWidget(separador)

        confirmar = b.boton("Confirmar pedido", "primario")
        confirmar.clicked.connect(lambda: self.ir_a("Confirmar estado"))
        v.addWidget(confirmar)
        v.addWidget(b.boton("Cancelar pedido", "peligro"))

        ayuda = QLabel("Al confirmar se descuenta el stock de cada producto.")
        ayuda.setObjectName("ayuda")
        ayuda.setWordWrap(True)
        v.addWidget(ayuda)
        return tarjeta
