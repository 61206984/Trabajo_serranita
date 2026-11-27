"""P07 Pedido registrado (Nuevo pedido, paso 4). Medidas y textos del Figma (1280×800)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.componentes import basicos as b

PASOS = [("Cliente", "hecho"), ("Productos", "hecho"), ("Resumen", "hecho"), ("Registrado", "actual")]


class PantallaPedidoRegistrado(QWidget):
    def __init__(self, ir_a, numero: str, cliente: str, total: float, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Pedido registrado", "El pedido fue guardado correctamente", pasos=PASOS))

        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(560)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        circulo = QLabel("✓")
        circulo.setObjectName("circuloExito")
        circulo.setFixedSize(72, 72)
        circulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(circulo, 0, Qt.AlignmentFlag.AlignHCenter)

        titulo = QLabel(f"Pedido {numero} registrado")
        titulo.setObjectName("titulo")
        v.addWidget(titulo, 0, Qt.AlignmentFlag.AlignHCenter)

        cuerpo = QLabel(f"Pedido {numero} registrado. Estado: Pendiente.")
        cuerpo.setObjectName("cuerpo")
        v.addWidget(cuerpo, 0, Qt.AlignmentFlag.AlignHCenter)

        resumen = QFrame()
        resumen.setObjectName("resumenGris")
        rv = QVBoxLayout(resumen)
        rv.setContentsMargins(16, 16, 16, 16)
        rv.setSpacing(8)
        rv.addLayout(self._fila("Cliente", cliente))
        rv.addLayout(self._fila("Total", f"S/ {total:.2f}"))
        estado = QHBoxLayout()
        etiqueta = QLabel("Estado")
        etiqueta.setObjectName("secundario")
        estado.addWidget(etiqueta)
        estado.addStretch(1)
        estado.addWidget(b.insignia("Pendiente"))
        rv.addLayout(estado)
        v.addWidget(resumen)

        v.addWidget(b.aviso("El stock se descuenta al confirmar el pedido.", "info"))

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        ver = b.boton("Ver pedidos", "primario")
        ver.clicked.connect(lambda: self.ir_a("Pedidos"))
        nuevo = b.boton("Nuevo pedido", "secundario")
        nuevo.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        acciones.addStretch(1)
        acciones.addWidget(ver)
        acciones.addWidget(nuevo)
        acciones.addStretch(1)
        v.addLayout(acciones)

        centro = QHBoxLayout()
        centro.addStretch(1)
        centro.addWidget(tarjeta)
        centro.addStretch(1)
        raiz.addLayout(centro)
        raiz.addStretch(1)

    def _fila(self, etiqueta: str, valor: str) -> QHBoxLayout:
        h = QHBoxLayout()
        izq = QLabel(etiqueta)
        izq.setObjectName("secundario")
        der = QLabel(valor)
        der.setObjectName("valor")
        h.addWidget(izq)
        h.addStretch(1)
        h.addWidget(der)
        return h
