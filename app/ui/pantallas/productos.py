"""P11 Productos y stock (Almacenero y Gerente) y P13 Ingresar stock (RF-06, RF-08)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget

from app.repos import productos as repo_productos
from app.services import pedidos as svc
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto


class DialogoIngresarStock(QDialog):
    def __init__(self, producto: dict, parent=None):
        super().__init__(parent)
        self.producto = producto
        self._stock = float(producto["stock"])
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
        rv.addWidget(QLabel(f"{producto['nombre']} · {producto['codigo']}"))
        rv.addWidget(QLabel(f"Stock actual: {self._stock:g} unidades"))
        v.addWidget(resumen)
        self.cantidad = QLineEdit("1")
        self.cantidad.setFixedHeight(40)
        self.cantidad.textChanged.connect(self._actualizar)
        v.addLayout(b.etiquetado("Cantidad a ingresar *", self.cantidad))
        self.pie = QLabel("")
        self.pie.setObjectName("ayuda")
        v.addWidget(self.pie)
        self._actualizar(self.cantidad.text())
        self.cantidad_valor = None
        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        acciones.addStretch(1)
        cancelar = b.boton("Cancelar", "secundario")
        cancelar.clicked.connect(self.reject)
        registrar = b.boton("Registrar ingreso")
        registrar.clicked.connect(self._aceptar)
        acciones.addWidget(cancelar)
        acciones.addWidget(registrar)
        v.addLayout(acciones)

    def _actualizar(self, valor: str) -> None:
        try:
            n = float(valor.replace(",", "."))
        except ValueError:
            n = 0
        if n > 0:
            self.pie.setText(f"Stock luego del ingreso: {self._stock + n:g} unidades")
        else:
            self.pie.setText("Ingrese una cantidad mayor que cero")

    def _aceptar(self) -> None:
        try:
            svc.ingresar_stock(self.producto["id_producto"], self.cantidad.text().replace(",", "."))
        except svc.ErrorNegocio as e:
            QMessageBox.warning(self, "No se pudo registrar", str(e))
            return
        self.accept()


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
        self.zona_tabla = QVBoxLayout()
        raiz.addLayout(self.zona_tabla)
        self.info = QLabel("")
        self.info.setObjectName("secundario")
        raiz.addWidget(self.info)
        raiz.addStretch(1)
        self.filtrar()

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por código o nombre")
        self.categoria = b.desplegable(["Todas"] + repo_productos.categorias())
        self.estado = b.desplegable(["Todos", "Disponible", "Stock bajo", "Sin stock"])
        h.addLayout(b.etiquetado("Producto", self.buscar), 1)
        h.addLayout(b.etiquetado("Categoría", self.categoria, 180))
        h.addLayout(b.etiquetado("Estado de stock", self.estado, 180))
        filtrar = b.boton("Filtrar", "primario")
        filtrar.clicked.connect(self.filtrar)
        h.addWidget(filtrar, 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def filtrar(self) -> None:
        estado = None if self.estado.currentText() == "Todos" else self.estado.currentText()
        filas = repo_productos.listar(self.buscar.text(), self.categoria.currentText(), estado)
        while self.zona_tabla.count():
            it = self.zona_tabla.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        tabla = nueva_tabla(["Código", "Producto", "Categoría", "Unidad", "Precio", "Stock", "Estado", ""],
                            max(len(filas), 1))
        for fila, p in enumerate(filas):
            tabla.setItem(fila, 0, texto(p["codigo"]))
            tabla.setItem(fila, 1, texto(p["nombre"]))
            tabla.setItem(fila, 2, texto(p["categoria"] or "—"))
            tabla.setItem(fila, 3, texto(p["unidad_medida"]))
            tabla.setItem(fila, 4, texto(f"S/ {float(p['precio_unit']):.2f}", derecha=True))
            tabla.setItem(fila, 5, texto(f"{float(p['stock']):g}", derecha=True))
            tabla.setCellWidget(fila, 6, celda(b.estado_stock(int(float(p["stock"])))))
            ingresar = b.boton("Ingresar stock", "secundario", 130)
            ingresar.clicked.connect(lambda _=False, p=p: self._ingresar(p))
            tabla.setCellWidget(fila, 7, celda(ingresar, derecha=True))
        self.zona_tabla.addWidget(tabla)
        self.info.setText(f"{len(filas)} productos" if filas else "No hay productos que coincidan con los filtros.")

    def _ingresar(self, producto: dict) -> None:
        if DialogoIngresarStock(producto, self).exec() == QDialog.DialogCode.Accepted:
            self.filtrar()
