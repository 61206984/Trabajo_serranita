"""P06 Resumen del pedido (Nuevo pedido, paso 3). Medidas y textos del Figma (1280×800).
El total se calcula a partir de las líneas; el estado inicial del pedido es Pendiente (RN-03)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

PASOS = [("Cliente", "hecho"), ("Productos", "hecho"), ("Resumen", "actual"), ("Registrado", "pendiente")]
CLIENTE_NOMBRE = "Minimarket El Mantaro S.A.C."
CLIENTE_DATOS = "RUC 20601234567 · 964 112 233 · Jr. Real 845, Huancayo"
OBSERVACION = "Entregar antes de las 10:00 a. m. en el local de Jr. Real 845."

# (código, producto, cantidad, precio unitario)
LINEAS = [
    ("QF-500", "Queso fresco 500 g", 12, 14.50),
    ("YG-1L", "Yogur frutado 1 litro", 3, 9.80),
    ("LE-1L", "Leche entera 1 litro", 24, 4.80),
]


class PantallaResumenPedido(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        total = round(sum(cant * precio for _, _, cant, precio in LINEAS), 2)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Resumen del pedido", "Revise las líneas y el total antes de registrar", pasos=PASOS))
        raiz.addWidget(self._cliente())
        raiz.addWidget(self._lineas())

        pie = QHBoxLayout()
        pie.setSpacing(24)
        pie.addWidget(self._observaciones(), 1, Qt.AlignmentFlag.AlignTop)
        pie.addWidget(self._total(total), 0, Qt.AlignmentFlag.AlignTop)
        raiz.addLayout(pie)

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        registrar = b.boton("Registrar pedido", "primario")
        registrar.clicked.connect(lambda: self.ir_a("Pedido registrado"))
        volver = b.boton("Volver", "secundario")
        volver.clicked.connect(lambda: self.ir_a("Agregar productos"))
        acciones.addWidget(registrar)
        acciones.addWidget(volver)
        acciones.addStretch(1)
        raiz.addLayout(acciones)
        raiz.addStretch(1)

    def _cliente(self) -> QFrame:
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(2)
        nombre = QLabel(CLIENTE_NOMBRE)
        nombre.setStyleSheet("font-size: 18px; font-weight: 600;")
        detalle = QLabel(CLIENTE_DATOS)
        detalle.setObjectName("secundario")
        v.addWidget(nombre)
        v.addWidget(detalle)
        return tarjeta

    def _lineas(self):
        tabla = nueva_tabla(["Código", "Producto", "Cant.", "Precio unit.", "Subtotal"], len(LINEAS))
        for fila, (codigo, nombre, cant, precio) in enumerate(LINEAS):
            tabla.setItem(fila, 0, texto(codigo))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(str(cant), derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {precio:.2f}", derecha=True))
            tabla.setItem(fila, 4, texto(f"S/ {cant * precio:.2f}", derecha=True))
        return tabla

    def _observaciones(self) -> QWidget:
        cont = QWidget()
        v = QVBoxLayout(cont)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        etiqueta = QLabel("Observaciones")
        etiqueta.setObjectName("etiquetaCampo")
        self.observaciones = QPlainTextEdit(OBSERVACION)
        self.observaciones.setFixedHeight(72)
        v.addWidget(etiqueta)
        v.addWidget(self.observaciones)
        return cont

    def _total(self, total: float) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(360)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(4)
        etiqueta = QLabel("Total del pedido")
        etiqueta.setObjectName("secundario")
        valor = QLabel(f"S/ {total:.2f}")
        valor.setObjectName("total")
        detalle = QLabel(f"{len(LINEAS)} líneas · Estado inicial: Pendiente")
        detalle.setObjectName("ayuda")
        v.addWidget(etiqueta)
        v.addWidget(valor)
        v.addWidget(detalle)
        return tarjeta
