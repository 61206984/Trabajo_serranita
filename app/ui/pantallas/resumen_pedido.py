"""P06 Resumen del pedido (Nuevo pedido, paso 3). Registra el pedido en la base de datos (RN-03 a RN-06)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget

from app.services import pedidos as svc
from app.services.carrito import carrito
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

PASOS = [("Cliente", "hecho"), ("Productos", "hecho"), ("Resumen", "actual"), ("Registrado", "pendiente")]

# Identificador del vendedor que registra: se toma de la sesión (RN-08).
from app.services import auth  # noqa: E402


class PantallaResumenPedido(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Resumen del pedido", "Revise las líneas y el total antes de registrar", pasos=PASOS))
        raiz.addWidget(self._cliente())
        raiz.addWidget(self._lineas())

        self.aviso = b.aviso("", "error")
        self.aviso.hide()
        raiz.addWidget(self.aviso)

        pie = QHBoxLayout()
        pie.setSpacing(24)
        pie.addWidget(self._observaciones(), 1, Qt.AlignmentFlag.AlignTop)
        pie.addWidget(self._total(), 0, Qt.AlignmentFlag.AlignTop)
        raiz.addLayout(pie)

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        self.btn_registrar = b.boton("Registrar pedido", "primario")
        self.btn_registrar.clicked.connect(self._registrar)
        volver = b.boton("Volver", "secundario")
        volver.clicked.connect(lambda: self.ir_a("Agregar productos"))
        acciones.addWidget(self.btn_registrar)
        acciones.addWidget(volver)
        acciones.addStretch(1)
        raiz.addLayout(acciones)
        raiz.addStretch(1)

    def _cliente(self) -> QFrame:
        c = carrito.cliente
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(2)
        nombre = QLabel(c.nombre)
        nombre.setStyleSheet("font-size: 18px; font-weight: 600;")
        partes = [c.documento] + ([c.telefono] if c.telefono else []) + ([c.direccion] if c.direccion else [])
        detalle = QLabel(" · ".join(partes))
        detalle.setObjectName("secundario")
        v.addWidget(nombre)
        v.addWidget(detalle)
        return tarjeta

    def _lineas(self):
        lineas = list(carrito.lineas.values())
        tabla = nueva_tabla(["Código", "Producto", "Cant.", "Precio unit.", "Subtotal"], len(lineas))
        for fila, l in enumerate(lineas):
            tabla.setItem(fila, 0, texto(l.codigo))
            tabla.setItem(fila, 1, texto(l.nombre))
            tabla.setItem(fila, 2, texto(f"{l.cantidad:g}", derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {l.precio:.2f}", derecha=True))
            tabla.setItem(fila, 4, texto(f"S/ {l.subtotal:.2f}", derecha=True))
        return tabla

    def _observaciones(self) -> QWidget:
        cont = QWidget()
        v = QVBoxLayout(cont)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(6)
        etiqueta = QLabel("Observaciones")
        etiqueta.setObjectName("etiquetaCampo")
        self.observaciones = QPlainTextEdit(carrito.observaciones)
        self.observaciones.setFixedHeight(72)
        v.addWidget(etiqueta)
        v.addWidget(self.observaciones)
        return cont

    def _total(self) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(360)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(4)
        etiqueta = QLabel("Total del pedido")
        etiqueta.setObjectName("secundario")
        valor = QLabel(f"S/ {carrito.total():.2f}")
        valor.setObjectName("total")
        detalle = QLabel(f"{len(carrito.lineas)} líneas · Estado inicial: Pendiente")
        detalle.setObjectName("ayuda")
        v.addWidget(etiqueta)
        v.addWidget(valor)
        v.addWidget(detalle)
        return tarjeta

    def _registrar(self) -> None:
        sesion = auth.sesion
        if sesion is None or sesion.id_vendedor is None:
            self.aviso.setText("Su usuario no tiene un vendedor asociado. Consulte al gerente.")
            self.aviso.show()
            return
        items = [(l.id_producto, l.cantidad) for l in carrito.lineas.values()]
        try:
            id_pedido, total = svc.crear_pedido(
                carrito.cliente.id_cliente, sesion.id_vendedor, items,
                self.observaciones.toPlainText().strip() or None)
        except svc.ErrorNegocio as e:
            self.aviso.setText(str(e))
            self.aviso.show()
            return
        numero = f"{id_pedido:04d}"
        cliente = carrito.cliente.nombre
        carrito.limpiar()
        self.ir_a("Pedido registrado", numero=numero, cliente=cliente, total=float(total))
