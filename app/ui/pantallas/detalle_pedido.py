"""P09 Detalle del pedido (variantes Pendiente y Confirmado) y P10 Confirmar estado (diálogo).
Medidas y textos del Figma (1280×800). Los datos son de ejemplo del Figma.
«Confirmar» solo cambia el estado (heurística 4). La lógica de stock (RN-04 y RN-05) se conectará
en el módulo de pedidos.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

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


class DialogoConfirmarPedido(QDialog):
    """P10: muestra el stock que se descontará antes de confirmar el pedido."""

    def __init__(self, numero: str, lineas, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(560)
        v = QVBoxLayout(self)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        cabecera = QHBoxLayout()
        cabecera.setSpacing(12)
        icono = QLabel("i")
        icono.setFixedSize(40, 40)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono.setStyleSheet(
            f"background: {t.PRIMARY_SOFT}; color: {t.PRIMARY}; border-radius: 20px; font-weight: 600;")
        titulo = QLabel(f"Confirmar pedido N.º {numero}")
        titulo.setObjectName("subtitulo")
        cabecera.addWidget(icono)
        cabecera.addWidget(titulo)
        cabecera.addStretch(1)
        v.addLayout(cabecera)

        explicacion = QLabel("Al confirmar, se descontará el siguiente stock. Esta acción no se puede deshacer.")
        explicacion.setObjectName("secundario")
        explicacion.setWordWrap(True)
        v.addWidget(explicacion)

        tabla = nueva_tabla(["Producto", "Cant.", "Stock actual", "Stock luego"], len(lineas))
        agotados = []
        for fila, (_, nombre, cant, _, stock) in enumerate(lineas):
            luego = stock - cant
            tabla.setItem(fila, 0, texto(nombre))
            tabla.setItem(fila, 1, texto(str(cant), derecha=True))
            tabla.setItem(fila, 2, texto(str(stock), derecha=True))
            if luego == 0:
                tabla.setItem(fila, 3, texto("0 (sin stock)", derecha=True, color=t.BADGE["Pendiente"][0]))
                agotados.append(nombre)
            else:
                tabla.setItem(fila, 3, texto(str(luego), derecha=True))
        v.addWidget(tabla)

        if agotados:
            v.addWidget(b.aviso(f"{', '.join(agotados)} quedará sin stock.", "advertencia"))

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        acciones.addStretch(1)
        volver = b.boton("Volver", "secundario")
        volver.clicked.connect(self.reject)
        confirmar = b.boton("Confirmar")
        confirmar.clicked.connect(self.accept)
        acciones.addWidget(volver)
        acciones.addWidget(confirmar)
        v.addLayout(acciones)


class PantallaDetallePedido(QWidget):
    def __init__(self, ir_a, numero: str = "0042", estado: str = "Pendiente", parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        self.numero = numero
        self.estado = estado
        total = round(sum(cant * precio for _, _, cant, precio, _ in LINEAS), 2)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addLayout(self._encabezado())

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

    def _encabezado(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(16)
        bloque = QVBoxLayout()
        bloque.setSpacing(4)
        titulo = QLabel(f"Pedido N.º {self.numero}")
        titulo.setObjectName("titulo")
        detalle = QLabel("Registrado el 27/11/2026 · Vendedor: Luis Cárdenas")
        detalle.setObjectName("secundario")
        bloque.addWidget(titulo)
        bloque.addWidget(detalle)
        h.addLayout(bloque)
        h.addStretch(1)
        h.addWidget(b.insignia(self.estado))
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

        actual = ESTADOS.index(self.estado)
        for i, nombre in enumerate(ESTADOS):
            fila = QHBoxLayout()
            fila.setSpacing(10)
            if i < actual:
                marca, objeto = "✓", "pasoActivo"
            elif i == actual:
                marca, objeto = "●", "pasoActivo"
            else:
                marca, objeto = "○", "pasoInactivo"
            m = QLabel(marca)
            m.setObjectName(objeto)
            etiqueta = QLabel(nombre)
            etiqueta.setObjectName("valor" if i <= actual else "secundario")
            fila.addWidget(m)
            fila.addWidget(etiqueta)
            fila.addStretch(1)
            v.addLayout(fila)

        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet(f"background: {t.BORDER};")
        v.addWidget(separador)

        if self.estado == "Pendiente":
            confirmar = b.boton("Confirmar pedido", "primario")
            confirmar.clicked.connect(self._abrir_confirmacion)
            ayuda_texto = "Al confirmar se descuenta el stock de cada producto."
        else:
            confirmar = b.boton("Confirmar entrega", "primario")
            ayuda_texto = "Si cancela, el stock se restituye."
        v.addWidget(confirmar)
        v.addWidget(b.boton("Cancelar pedido", "peligro"))

        ayuda = QLabel(ayuda_texto)
        ayuda.setObjectName("ayuda")
        ayuda.setWordWrap(True)
        v.addWidget(ayuda)
        return tarjeta

    def _abrir_confirmacion(self) -> None:
        if DialogoConfirmarPedido(self.numero, LINEAS, self).exec() == QDialog.DialogCode.Accepted:
            self.ir_a("Detalle del pedido Confirmado")
