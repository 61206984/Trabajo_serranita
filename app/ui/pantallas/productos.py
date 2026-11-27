"""P11 Productos y stock (Almacenero y Gerente) y P13 Ingresar stock (diálogo).
Medidas y textos del Figma (1280×800). Los productos son de ejemplo del Figma.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

# (código, producto, categoría, unidad, precio, stock)
PRODUCTOS = [
    ("QF-500", "Queso fresco 500 g", "Queso", "Unidad", 14.50, 120),
    ("YG-1L", "Yogur frutado 1 litro", "Yogur", "Litro", 9.80, 3),
    ("MT-200", "Mantequilla 200 g", "Mantequilla", "Unidad", 8.50, 64),
    ("MJ-1K", "Manjar blanco 1 kg", "Manjar", "Kg", 18.00, 35),
    ("LE-1L", "Leche entera 1 litro", "Leche", "Litro", 4.80, 210),
    ("HL-1L", "Helado de vainilla 1 litro", "Helado", "Litro", 16.00, 48),
    ("QP-1K", "Queso paria 1 kg", "Queso", "Kg", 32.00, 0),
]


class DialogoIngresarStock(QDialog):
    """P13: registra la mercadería que ingresa. La cantidad se suma al stock actual."""

    def __init__(self, producto, parent=None):
        super().__init__(parent)
        codigo, nombre, _, _, _, stock = producto
        self._stock = stock
        self.setMinimumWidth(480)

        v = QVBoxLayout(self)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        titulo = QLabel("Ingresar stock")
        titulo.setObjectName("subtitulo")
        ayuda = QLabel("Registre la mercadería que ingresó al almacén. La cantidad se suma al stock actual.")
        ayuda.setObjectName("secundario")
        ayuda.setWordWrap(True)
        v.addWidget(titulo)
        v.addWidget(ayuda)

        resumen = QFrame()
        resumen.setObjectName("resumenGris")
        rv = QVBoxLayout(resumen)
        rv.setContentsMargins(16, 12, 16, 12)
        rv.setSpacing(8)
        rv.addLayout(self._fila("Producto", f"{nombre} · {codigo}"))
        rv.addLayout(self._fila("Stock actual", f"{stock} unidades"))
        v.addWidget(resumen)

        self.cantidad = QLineEdit("40")
        self.cantidad.setFixedHeight(40)
        self.cantidad.textChanged.connect(self._actualizar)
        v.addLayout(b.etiquetado("Cantidad a ingresar *", self.cantidad))
        self.pie = QLabel("")
        self.pie.setObjectName("ayuda")
        v.addWidget(self.pie)
        self._actualizar(self.cantidad.text())

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        acciones.addStretch(1)
        cancelar = b.boton("Cancelar", "secundario")
        cancelar.clicked.connect(self.reject)
        registrar = b.boton("Registrar ingreso")
        registrar.clicked.connect(self.accept)
        acciones.addWidget(cancelar)
        acciones.addWidget(registrar)
        v.addLayout(acciones)

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

    def _actualizar(self, valor: str) -> None:
        try:
            n = int(valor)
        except ValueError:
            n = 0
        if n > 0:
            self.pie.setText(f"Stock luego del ingreso: {self._stock + n} unidades")
        else:
            self.pie.setText("Ingrese una cantidad mayor que cero")


class PantallaProductos(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        registrar = b.boton("Registrar producto", "primario")
        registrar.clicked.connect(lambda: self.ir_a("Registrar producto"))
        raiz.addWidget(b.encabezado(
            "Productos y stock", "Consulte el catálogo, registre productos y ingrese mercadería",
            accion=registrar))
        raiz.addWidget(self._filtros())
        raiz.addWidget(self._tabla())
        raiz.addLayout(self._pie())
        raiz.addStretch(1)

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        buscar = QLineEdit()
        buscar.setPlaceholderText("Buscar por código o nombre")
        h.addLayout(b.etiquetado("Producto", buscar), 1)
        h.addLayout(b.etiquetado("Categoría", b.desplegable(
            ["Todas", "Queso", "Yogur", "Leche", "Mantequilla", "Manjar", "Helado"]), 180))
        h.addLayout(b.etiquetado("Estado de stock", b.desplegable(
            ["Todos", "Disponible", "Stock bajo", "Sin stock"]), 180))
        h.addWidget(b.boton("Filtrar", "primario"), 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def _tabla(self):
        tabla = nueva_tabla(
            ["Código", "Producto", "Categoría", "Unidad", "Precio", "Stock", "Estado", ""], len(PRODUCTOS))
        for fila, producto in enumerate(PRODUCTOS):
            codigo, nombre, categoria, unidad, precio, stock = producto
            tabla.setItem(fila, 0, texto(codigo))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(categoria))
            tabla.setItem(fila, 3, texto(unidad))
            tabla.setItem(fila, 4, texto(f"S/ {precio:.2f}", derecha=True))
            tabla.setItem(fila, 5, texto(str(stock), derecha=True))
            tabla.setCellWidget(fila, 6, celda(b.estado_stock(stock)))
            ingresar = b.boton("Ingresar stock", "secundario", 130)
            ingresar.clicked.connect(lambda _=False, p=producto: self._ingresar(p))
            tabla.setCellWidget(fila, 7, celda(ingresar, derecha=True))
        return tabla

    def _ingresar(self, producto) -> None:
        DialogoIngresarStock(producto, self).exec()

    def _pie(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(8)
        info = QLabel(f"Mostrando 1–{len(PRODUCTOS)} de 24 productos")
        info.setObjectName("secundario")
        h.addWidget(info)
        h.addStretch(1)
        h.addWidget(b.boton("Anterior", "secundario", deshabilitado=True))
        h.addWidget(b.boton("Siguiente", "secundario"))
        return h
