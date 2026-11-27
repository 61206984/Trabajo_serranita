"""P09 Detalle del pedido y P10 Confirmar. Confirmar descuenta stock; cancelar lo restituye (RF-12, RF-13)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QWidget

from app.estilos import tokens as t
from app.repos import pedidos as repo_pedidos
from app.services import pedidos as svc
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import nueva_tabla, texto

ESTADOS = ["Pendiente", "Confirmado", "Entregado"]


class DialogoConfirmarPedido(QDialog):
    """P10: muestra el stock que se descontará antes de confirmar."""

    def __init__(self, numero: str, lineas, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(560)
        v = QVBoxLayout(self)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)
        titulo = QLabel(f"Confirmar pedido N.º {numero}")
        titulo.setObjectName("subtitulo")
        v.addWidget(titulo)
        explicacion = QLabel("Al confirmar, se descontará el siguiente stock. "
                             "Si cancela luego, el stock se restituye.")
        explicacion.setObjectName("secundario")
        explicacion.setWordWrap(True)
        v.addWidget(explicacion)
        tabla = nueva_tabla(["Producto", "Cant.", "Stock actual", "Stock luego"], max(len(lineas), 1))
        agotados = []
        for fila, l in enumerate(lineas):
            stock, cant = float(l["stock"]), float(l["cantidad"])
            luego = stock - cant
            tabla.setItem(fila, 0, texto(l["nombre"]))
            tabla.setItem(fila, 1, texto(f"{cant:g}", derecha=True))
            tabla.setItem(fila, 2, texto(f"{stock:g}", derecha=True))
            if luego == 0:
                tabla.setItem(fila, 3, texto("0 (sin stock)", derecha=True, color=t.BADGE["Pendiente"][0]))
                agotados.append(l["nombre"])
            else:
                tabla.setItem(fila, 3, texto(f"{luego:g}", derecha=True))
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


def _fila(etiqueta: str, valor: str) -> QHBoxLayout:
    h = QHBoxLayout()
    izq = QLabel(etiqueta)
    izq.setObjectName("ayuda")
    der = QLabel(valor)
    der.setObjectName("valor")
    h.addWidget(izq)
    h.addSpacing(8)
    h.addWidget(der)
    return h


class PantallaDetallePedido(QWidget):
    def __init__(self, ir_a, pedido_id: int, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        self.pedido_id = pedido_id
        cab = repo_pedidos.cabecera(pedido_id)  # None si el pedido no existe
        self.cab = cab
        self.lineas = repo_pedidos.detalle(pedido_id)

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
        izquierda.addLayout(self._total())
        izquierda.addStretch(1)
        cuerpo.addLayout(izquierda, 1)
        cuerpo.addWidget(self._panel_estado(), 0, Qt.AlignmentFlag.AlignTop)
        raiz.addLayout(cuerpo, 1)

    def _encabezado(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.setSpacing(16)
        bloque = QVBoxLayout()
        bloque.setSpacing(4)
        titulo = QLabel(f"Pedido N.º {self.pedido_id:04d}")
        titulo.setObjectName("titulo")
        detalle = QLabel(f"Registrado el {self.cab['fecha_pedido']:%d/%m/%Y} · Vendedor: {self.cab['vendedor']}")
        detalle.setObjectName("secundario")
        bloque.addWidget(titulo)
        bloque.addWidget(detalle)
        h.addLayout(bloque)
        h.addStretch(1)
        h.addWidget(b.insignia(self.cab["estado"]))
        volver = b.boton("Volver a pedidos", "secundario")
        volver.clicked.connect(lambda: self.ir_a("Pedidos"))
        h.addWidget(volver)
        return h

    def _datos_cliente(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(32)
        for etiqueta, valor in [("Cliente", self.cab["cliente"]),
                                ("Documento", f"{self.cab['tipo_doc']} {self.cab['nro_doc']}"),
                                ("Teléfono", self.cab["telefono"] or "—")]:
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
        tabla = nueva_tabla(["Código", "Producto", "Cant.", "Precio", "Subtotal", "Stock"], max(len(self.lineas), 1))
        for fila, l in enumerate(self.lineas):
            stock = float(l["stock"])
            color = t.BADGE["Pendiente"][0] if stock <= 5 else None
            tabla.setItem(fila, 0, texto(l["codigo"]))
            tabla.setItem(fila, 1, texto(l["nombre"]))
            tabla.setItem(fila, 2, texto(f"{float(l['cantidad']):g}", derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {float(l['precio_unitario']):.2f}", derecha=True))
            tabla.setItem(fila, 4, texto(f"S/ {float(l['subtotal']):.2f}", derecha=True))
            tabla.setItem(fila, 5, texto(f"{stock:g}", derecha=True, color=color))
        return tabla

    def _total(self) -> QHBoxLayout:
        h = QHBoxLayout()
        h.addStretch(1)
        etiqueta = QLabel("Total")
        etiqueta.setStyleSheet("font-size: 18px; font-weight: 600;")
        valor = QLabel(f"S/ {float(self.cab['total']):.2f}")
        valor.setStyleSheet("font-size: 18px; font-weight: 600;")
        h.addWidget(etiqueta)
        h.addSpacing(12)
        h.addWidget(valor)
        return h

    def _panel_estado(self) -> QFrame:
        estado = self.cab["estado"]
        tarjeta = b.tarjeta()
        tarjeta.setFixedWidth(320)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(16)
        titulo = QLabel("Estado del pedido")
        titulo.setStyleSheet("font-size: 18px; font-weight: 600;")
        v.addWidget(titulo)
        if estado == "Cancelado":
            v.addWidget(b.insignia("Cancelado"))
            v.addWidget(QLabel("Este pedido fue cancelado. No admite más cambios."))
            return tarjeta
        actual = ESTADOS.index(estado) if estado in ESTADOS else 0
        for i, nombre in enumerate(ESTADOS):
            fila = QHBoxLayout()
            fila.setSpacing(10)
            marca, objeto = ("✓", "pasoActivo") if i < actual else (("●", "pasoActivo") if i == actual else ("○", "pasoInactivo"))
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
        if estado == "Pendiente":
            accion = b.boton("Confirmar pedido", "primario")
            accion.clicked.connect(self._confirmar)
            ayuda_texto = "Al confirmar se descuenta el stock de cada producto."
        elif estado == "Confirmado":
            accion = b.boton("Marcar como entregado", "primario")
            accion.clicked.connect(self._entregar)
            ayuda_texto = "Si cancela, el stock se restituye."
        else:
            accion = b.boton("Entregado", "secundario", deshabilitado=True)
            ayuda_texto = "Pedido entregado: no admite cambios."
        v.addWidget(accion)
        if estado in ("Pendiente", "Confirmado"):
            cancelar = b.boton("Cancelar pedido", "peligro")
            cancelar.clicked.connect(self._cancelar)
            v.addWidget(cancelar)
        ayuda = QLabel(ayuda_texto)
        ayuda.setObjectName("ayuda")
        ayuda.setWordWrap(True)
        v.addWidget(ayuda)
        return tarjeta

    def _ejecutar(self, accion) -> None:
        try:
            accion(self.pedido_id)
        except svc.ErrorNegocio as e:
            QMessageBox.warning(self, "No se pudo completar", str(e))
            return
        self.ir_a("Detalle del pedido", pedido_id=self.pedido_id)

    def _confirmar(self) -> None:
        if DialogoConfirmarPedido(f"{self.pedido_id:04d}", self.lineas, self).exec() == QDialog.DialogCode.Accepted:
            self._ejecutar(svc.confirmar_pedido)

    def _entregar(self) -> None:
        self._ejecutar(svc.entregar_pedido)

    def _cancelar(self) -> None:
        r = QMessageBox.question(self, "Cancelar pedido",
                                 "¿Cancelar este pedido? Esta acción no se puede deshacer.")
        if r == QMessageBox.StandardButton.Yes:
            self._ejecutar(svc.cancelar_pedido)
