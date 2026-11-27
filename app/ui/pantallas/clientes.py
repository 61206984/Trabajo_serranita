"""P15 Clientes (vendedor) y P16 Dar de baja cliente (diálogo). Medidas y textos del Figma (1280×800).
Dar de baja es solo del vendedor. Un cliente dado de baja no se elimina.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.estilos import tokens as t
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto

# (documento, nombre, teléfono, activo)
CLIENTES = [
    ("RUC 20601234567", "Minimarket El Mantaro S.A.C.", "964 112 233", True),
    ("DNI 41256789", "Bodega Doña Rosa", "987 654 321", True),
    ("RUC 20487654321", "Restaurante Sabor Huanca E.I.R.L.", "064 231 456", True),
    ("DNI 20458963", "Juan Pérez Quispe", "954 321 876", True),
    ("RUC 20512345678", "Panadería San José E.I.R.L.", "064 247 810", False),
]


def _fila(etiqueta: str, valor: str) -> QHBoxLayout:
    h = QHBoxLayout()
    izq = QLabel(etiqueta)
    izq.setObjectName("secundario")
    der = QLabel(valor)
    der.setObjectName("valor")
    h.addWidget(izq)
    h.addStretch(1)
    h.addWidget(der)
    return h


class DialogoDarDeBaja(QDialog):
    """P16: confirma la baja. El cliente queda inactivo y conserva su historial."""

    def __init__(self, documento: str, nombre: str, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(480)
        v = QVBoxLayout(self)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(16)

        cabecera = QHBoxLayout()
        cabecera.setSpacing(12)
        icono = QLabel("!")
        icono.setFixedSize(40, 40)
        icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono.setStyleSheet(
            f"background: {t.DANGER_BG}; color: {t.DANGER_TEXT}; border-radius: 20px; font-weight: 600;")
        titulo = QLabel("Dar de baja al cliente")
        titulo.setObjectName("subtitulo")
        cabecera.addWidget(icono)
        cabecera.addWidget(titulo)
        cabecera.addStretch(1)
        v.addLayout(cabecera)

        explicacion = QLabel(
            "El cliente quedará inactivo y no podrá asignarse a pedidos nuevos. "
            "No se elimina: conserva su historial de pedidos.")
        explicacion.setObjectName("secundario")
        explicacion.setWordWrap(True)
        v.addWidget(explicacion)

        resumen = QFrame()
        resumen.setObjectName("resumenGris")
        rv = QVBoxLayout(resumen)
        rv.setContentsMargins(16, 12, 16, 12)
        rv.setSpacing(8)
        rv.addLayout(_fila("Cliente", nombre))
        rv.addLayout(_fila("Documento", documento))
        v.addWidget(resumen)

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        acciones.addStretch(1)
        volver = b.boton("Volver", "secundario")
        volver.clicked.connect(self.reject)
        baja = b.boton("Dar de baja", "peligro")
        baja.clicked.connect(self.accept)
        acciones.addWidget(volver)
        acciones.addWidget(baja)
        v.addLayout(acciones)


class PantallaClientes(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        nuevo = b.boton("Cliente nuevo", "primario")
        nuevo.clicked.connect(lambda: self.ir_a("Registrar cliente"))
        raiz.addWidget(b.encabezado(
            "Clientes", "Consulte los clientes y dé de baja a los que ya no compran", accion=nuevo))
        raiz.addWidget(self._filtros())
        raiz.addWidget(self._tabla())
        ayuda = QLabel("Un cliente dado de baja no se elimina: conserva su historial y no puede asignarse a pedidos nuevos.")
        ayuda.setObjectName("ayuda")
        raiz.addWidget(ayuda)
        raiz.addStretch(1)

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        buscar = QLineEdit()
        buscar.setPlaceholderText("Buscar por documento o nombre")
        h.addLayout(b.etiquetado("Cliente", buscar), 1)
        h.addLayout(b.etiquetado("Estado", b.desplegable(["Todos", "Activo", "Inactivo"]), 180))
        h.addWidget(b.boton("Buscar"), 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def _tabla(self):
        tabla = nueva_tabla(["Documento", "Cliente", "Teléfono", "Estado", ""], len(CLIENTES))
        for fila, (documento, nombre, telefono, activo) in enumerate(CLIENTES):
            tabla.setItem(fila, 0, texto(documento))
            tabla.setItem(fila, 1, texto(nombre))
            tabla.setItem(fila, 2, texto(telefono))
            tabla.setCellWidget(fila, 3, celda(b.pildora_activo(activo)))
            if activo:
                accion = b.boton("Dar de baja", "secundario", 120)
                accion.clicked.connect(
                    lambda _=False, d=documento, n=nombre: DialogoDarDeBaja(d, n, self).exec())
            else:
                accion = b.boton("Dado de baja", "secundario", 120, deshabilitado=True)
            tabla.setCellWidget(fila, 4, celda(accion, derecha=True))
        return tabla
