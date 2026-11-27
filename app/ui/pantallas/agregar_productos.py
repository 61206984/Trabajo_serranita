"""P05 Agregar productos (Nuevo pedido, paso 2) y su variante con stock insuficiente (P05b).
Medidas y textos del Figma (1280×800). Los productos son de ejemplo del Figma; se reemplazarán
con la consulta a la base de datos. El aviso y el borde rojo salen de comparar cantidad y stock.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.estilos import tokens as t
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

PASOS = [("Cliente", "hecho"), ("Productos", "actual"), ("Resumen", "pendiente"), ("Registrado", "pendiente")]
CLIENTE_NOMBRE = "Minimarket El Mantaro S.A.C."
CLIENTE_DATOS = "RUC 20601234567 · 964 112 233"
STOCK_BAJO = 5

# (código, producto, precio, stock, cantidad inicial, ya está en el pedido)
CATALOGO = [
    ("QF-500", "Queso fresco 500 g", 14.50, 120, 12, True),
    ("YG-1L", "Yogur frutado 1 litro", 9.80, 3, 3, True),
    ("MT-200", "Mantequilla 200 g", 8.50, 64, 1, False),
    ("MJ-1K", "Manjar blanco 1 kg", 18.00, 35, 1, False),
    ("LE-1L", "Leche entera 1 litro", 4.80, 210, 24, True),
    ("HL-1L", "Helado de vainilla 1 litro", 16.00, 48, 1, False),
]


class PantallaAgregarProductos(QWidget):
    def __init__(self, ir_a, stock_insuficiente: bool = False, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        self.cantidades = {codigo: cant for codigo, _, _, _, cant, _ in CATALOGO}
        if stock_insuficiente:
            self.cantidades["YG-1L"] = 5  # P05b: el vendedor pide más de lo que hay

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Agregar productos", "Seleccione los productos y las cantidades del pedido", pasos=PASOS))

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(24)
        izquierda = QVBoxLayout()
        izquierda.setSpacing(16)
        izquierda.addWidget(self._cliente())
        izquierda.addWidget(self._aviso())
        izquierda.addWidget(self._tabla())
        izquierda.addStretch(1)
        cuerpo.addLayout(izquierda, 1)
        cuerpo.addWidget(self._pedido_actual(), 0, Qt.AlignmentFlag.AlignTop)
        raiz.addLayout(cuerpo, 1)

    def _cliente(self) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedHeight(100)
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        datos = QVBoxLayout()
        datos.setSpacing(2)
        nombre = QLabel(CLIENTE_NOMBRE)
        nombre.setStyleSheet("font-size: 18px; font-weight: 600;")
        detalle = QLabel(CLIENTE_DATOS)
        detalle.setObjectName("secundario")
        datos.addWidget(nombre)
        datos.addWidget(detalle)
        h.addLayout(datos)
        h.addStretch(1)
        cambiar = b.boton("Cambiar cliente", "secundario", 150)
        cambiar.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        h.addWidget(cambiar)
        return tarjeta

    def _aviso(self) -> QFrame:
        for codigo, nombre, _, stock, _, _ in CATALOGO:
            if self.cantidades[codigo] > stock:
                return b.aviso(
                    f"Stock insuficiente: quedan {stock} unidades de {nombre}. Reduzca la cantidad.", "error")
        return b.aviso("El stock puede cambiar hasta que el pedido se confirme.", "advertencia")

    def _tabla(self):
        tabla = nueva_tabla(["Código", "Producto", "Precio", "Stock", "Cant.", ""], len(CATALOGO))
        for fila, (codigo, nombre, precio, stock, _, en_pedido) in enumerate(CATALOGO):
            cant = self.cantidades[codigo]
            tabla.setItem(fila, 0, texto(codigo))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(f"S/ {precio:.2f}", derecha=True))
            color = t.BADGE["Pendiente"][0] if stock <= STOCK_BAJO else None
            tabla.setItem(fila, 3, texto(str(stock), derecha=True, color=color))
            tabla.setCellWidget(fila, 4, celda(self._cantidad(cant, cant > stock), derecha=True))
            if en_pedido:
                accion = b.boton("Agregado", "secundario", 106, deshabilitado=True)
            else:
                accion = b.boton("Agregar", "secundario", 106)
            tabla.setCellWidget(fila, 5, celda(accion, derecha=True))
        return tabla

    def _cantidad(self, valor: int, error: bool) -> QLineEdit:
        campo = QLineEdit(str(valor))
        campo.setObjectName("cantidad")
        campo.setFixedSize(64, 32)
        campo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        campo.setProperty("error", error)
        return campo

    def _pedido_actual(self) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(320)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(16)

        lineas = [(c, n, p, self.cantidades[c]) for c, n, p, _, _, en in CATALOGO if en]
        cabecera = QHBoxLayout()
        titulo = QLabel("Pedido actual")
        titulo.setStyleSheet("font-size: 18px; font-weight: 600;")
        conteo = QLabel(f"{len(lineas)} líneas")
        conteo.setObjectName("secundario")
        cabecera.addWidget(titulo)
        cabecera.addStretch(1)
        cabecera.addWidget(conteo)
        v.addLayout(cabecera)

        total = 0.0
        for _, nombre, precio, cant in lineas:
            subtotal = round(precio * cant, 2)
            total += subtotal
            v.addLayout(self._linea(nombre, f"{cant} × S/ {precio:.2f}", subtotal))

        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet(f"background: {t.BORDER};")
        v.addWidget(separador)

        fila_total = QHBoxLayout()
        etiqueta = QLabel("Total")
        etiqueta.setStyleSheet("font-size: 18px; font-weight: 600;")
        valor = QLabel(f"S/ {total:.2f}")
        valor.setStyleSheet("font-size: 18px; font-weight: 600;")
        fila_total.addWidget(etiqueta)
        fila_total.addStretch(1)
        fila_total.addWidget(valor)
        v.addLayout(fila_total)

        continuar = b.boton("Continuar", "primario")
        continuar.clicked.connect(lambda: self.ir_a("Resumen del pedido"))
        v.addWidget(continuar)
        return tarjeta

    def _linea(self, nombre: str, detalle: str, importe: float) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(8)
        bloque = QVBoxLayout()
        bloque.setSpacing(2)
        n = QLabel(nombre)
        n.setObjectName("valor")
        d = QLabel(detalle)
        d.setObjectName("ayuda")
        bloque.addWidget(n)
        bloque.addWidget(d)
        h.addLayout(bloque)
        h.addStretch(1)
        v = QLabel(f"S/ {importe:.2f}")
        v.setObjectName("valor")
        h.addWidget(v)
        return h
