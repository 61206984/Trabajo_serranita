"""P05 Agregar productos (Nuevo pedido, paso 2). Catálogo y stock desde la base de datos.
RF-06, RF-09, RF-10: no deja agregar más de lo que hay en stock."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.estilos import tokens as t
from app.repos import productos as repo_productos
from app.services.carrito import Linea, carrito
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

PASOS = [("Cliente", "hecho"), ("Productos", "actual"), ("Resumen", "pendiente"), ("Registrado", "pendiente")]


class PantallaAgregarProductos(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Agregar productos", "Seleccione los productos y las cantidades del pedido", pasos=PASOS))

        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por código o nombre")
        self.buscar.setFixedHeight(40)
        self.buscar.returnPressed.connect(self._refrescar)

        cuerpo = QHBoxLayout()
        cuerpo.setSpacing(24)
        self.izquierda = QVBoxLayout()
        self.izquierda.setSpacing(16)
        self.izquierda.addWidget(self._cliente())
        self.izquierda.addWidget(self.buscar)
        self.zona_aviso = QVBoxLayout()
        self.izquierda.addLayout(self.zona_aviso)
        self.zona_tabla = QVBoxLayout()
        self.izquierda.addLayout(self.zona_tabla)
        self.izquierda.addStretch(1)
        cuerpo.addLayout(self.izquierda, 1)
        self.lateral = QVBoxLayout()
        cuerpo.addLayout(self.lateral)
        raiz.addLayout(cuerpo, 1)
        self._refrescar()

    # --- Secciones ---
    def _refrescar(self) -> None:
        self._limpiar(self.zona_tabla)
        self._limpiar(self.zona_aviso)
        self._limpiar(self.lateral)
        self.zona_tabla.addWidget(self._tabla(self.buscar.text().strip()))
        self.zona_aviso.addWidget(self._aviso())
        self.lateral.addWidget(self._pedido_actual(), 0, Qt.AlignmentFlag.AlignTop)

    def _limpiar(self, layout) -> None:
        while layout.count():
            it = layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
            elif it.layout():
                self._limpiar(it.layout())

    def _cliente(self) -> QFrame:
        c = carrito.cliente
        tarjeta = b.tarjeta()
        tarjeta.setFixedHeight(100)
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        datos = QVBoxLayout()
        datos.setSpacing(2)
        nombre = QLabel(c.nombre)
        nombre.setStyleSheet("font-size: 18px; font-weight: 600;")
        detalle = QLabel(f"{c.documento}" + (f" · {c.telefono}" if c.telefono else ""))
        detalle.setObjectName("secundario")
        datos.addWidget(nombre)
        datos.addWidget(detalle)
        h.addLayout(datos)
        h.addStretch(1)
        cambiar = b.boton("Cambiar cliente", "secundario", 170, icono="users")
        cambiar.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        h.addWidget(cambiar)
        return tarjeta

    def _excedidos(self):
        return [l for l in carrito.lineas.values() if l.cantidad > l.stock]

    def _aviso(self) -> QFrame:
        excedidos = self._excedidos()
        if excedidos:
            l = excedidos[0]
            return b.aviso(f"Stock insuficiente: quedan {int(l.stock)} unidades de {l.nombre}. "
                           "Reduzca la cantidad.", "error")
        return b.aviso("El stock puede cambiar hasta que el pedido se confirme.", "advertencia")

    def _tabla(self, filtro: str):
        filas = repo_productos.listar(texto=filtro)
        tabla = nueva_tabla(["Código", "Producto", "Precio", "Stock", "Cant.", ""], max(len(filas), 1))
        for fila, p in enumerate(filas):
            stock = float(p["stock"])
            en_pedido = p["id_producto"] in carrito.lineas
            tabla.setItem(fila, 0, texto(p["codigo"]))
            tabla.setItem(fila, 1, texto(p["nombre"]))
            tabla.setItem(fila, 2, texto(f"S/ {float(p['precio_unit']):.2f}", derecha=True))
            color = t.BADGE["Pendiente"][0] if stock <= repo_productos.UMBRAL_STOCK_BAJO else None
            tabla.setItem(fila, 3, texto(f"{stock:g}", derecha=True, color=color))
            if en_pedido:
                cant = carrito.lineas[p["id_producto"]].cantidad
                campo = QLineEdit(f"{cant:g}")
                campo.setObjectName("cantidad")
                campo.setFixedSize(64, 32)
                campo.setAlignment(Qt.AlignmentFlag.AlignCenter)
                campo.setProperty("error", cant > stock)
                campo.editingFinished.connect(lambda p=p, c=campo: self._cambiar_cantidad(p, c))
                tabla.setCellWidget(fila, 4, celda(campo, derecha=True))
                accion = b.boton("Quitar", "secundario", 106)
                accion.clicked.connect(lambda _=False, p=p: self._quitar(p))
            else:
                tabla.setCellWidget(fila, 4, celda(QLabel(""), derecha=True))
                accion = b.boton("Agregar", "secundario", 106, deshabilitado=stock <= 0)
                accion.clicked.connect(lambda _=False, p=p: self._agregar(p))
            tabla.setCellWidget(fila, 5, celda(accion, derecha=True))
        return tabla

    def _agregar(self, p) -> None:
        carrito.lineas[p["id_producto"]] = Linea(
            id_producto=p["id_producto"], codigo=p["codigo"], nombre=p["nombre"],
            precio=float(p["precio_unit"]), stock=float(p["stock"]), cantidad=1)
        self._refrescar()

    def _quitar(self, p) -> None:
        carrito.lineas.pop(p["id_producto"], None)
        self._refrescar()

    def _cambiar_cantidad(self, p, campo: QLineEdit) -> None:
        try:
            cant = float(campo.text().replace(",", "."))
        except ValueError:
            cant = 0
        if cant <= 0:
            carrito.lineas.pop(p["id_producto"], None)
        elif p["id_producto"] in carrito.lineas:
            carrito.lineas[p["id_producto"]].cantidad = cant
        self._refrescar()

    def _pedido_actual(self) -> QFrame:
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(320)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(16)
        cabecera = QHBoxLayout()
        titulo = QLabel("Pedido actual")
        titulo.setStyleSheet("font-size: 18px; font-weight: 600;")
        conteo = QLabel(f"{len(carrito.lineas)} líneas")
        conteo.setObjectName("secundario")
        cabecera.addWidget(titulo)
        cabecera.addStretch(1)
        cabecera.addWidget(conteo)
        v.addLayout(cabecera)
        for l in carrito.lineas.values():
            v.addLayout(self._linea(l.nombre, f"{l.cantidad:g} × S/ {l.precio:.2f}", l.subtotal))
        separador = QFrame()
        separador.setFixedHeight(1)
        separador.setStyleSheet(f"background: {t.BORDER};")
        v.addWidget(separador)
        fila_total = QHBoxLayout()
        etiqueta = QLabel("Total")
        etiqueta.setStyleSheet("font-size: 18px; font-weight: 600;")
        valor = QLabel(f"S/ {carrito.total():.2f}")
        valor.setStyleSheet("font-size: 18px; font-weight: 600;")
        fila_total.addWidget(etiqueta)
        fila_total.addStretch(1)
        fila_total.addWidget(valor)
        v.addLayout(fila_total)
        continuar = b.boton("Continuar", "primario")
        continuar.setEnabled(bool(carrito.lineas) and not self._excedidos())
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
