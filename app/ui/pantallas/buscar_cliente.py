"""P03 Buscar cliente (Nuevo pedido, paso 1). Medidas y textos del Figma (1280×800).

Los clientes recientes son de ejemplo del Figma; se reemplazarán con la consulta a la base de datos
cuando exista el módulo de clientes. Los inactivos no se pueden seleccionar (RF-05, RN-07).
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.estilos import tokens as t
from app.ui.componentes import basicos as b

PASOS = [("Cliente", "actual"), ("Productos", "pendiente"), ("Resumen", "pendiente"), ("Registrado", "pendiente")]

CLIENTES_RECIENTES = [
    ("RUC 20601234567", "Minimarket El Mantaro S.A.C.", "964 112 233", True),
    ("DNI 41256789", "Bodega Doña Rosa", "987 654 321", True),
    ("RUC 20487654321", "Restaurante Sabor Huanca E.I.R.L.", "064 231 456", True),
    ("DNI 20458963", "Juan Pérez Quispe", "954 321 876", True),
    ("RUC 20512345678", "Panadería San José E.I.R.L.", "064 247 810", False),
]


class PantallaBuscarCliente(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        nuevo = b.boton("Cliente nuevo", "secundario", 136)
        nuevo.clicked.connect(lambda: self.ir_a("Registrar cliente"))
        raiz.addWidget(b.encabezado(
            "Nuevo pedido", "Busque al cliente por número de documento o nombre",
            pasos=PASOS, accion=None))

        # Barra de búsqueda (tarjeta de 16 px de padding)
        barra = b.tarjeta()
        bl = QHBoxLayout(barra)
        bl.setContentsMargins(16, 16, 16, 16)
        bl.setSpacing(12)
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por documento o nombre")
        self.buscar.setFixedHeight(40)
        bl.addWidget(self.buscar, 1)
        bl.addWidget(b.boton("Buscar", "primario", 88))
        bl.addWidget(nuevo)
        raiz.addWidget(barra)

        raiz.addWidget(self._sub("Clientes recientes"))
        raiz.addWidget(self._tabla())
        raiz.addWidget(self._ayuda("Los clientes inactivos no se pueden asignar a un pedido nuevo."))
        raiz.addStretch(1)

    def _sub(self, texto: str) -> QLabel:
        l = QLabel(texto)
        l.setStyleSheet("font-size: 18px; font-weight: 600;")
        return l

    def _ayuda(self, texto: str) -> QLabel:
        l = QLabel(texto)
        l.setObjectName("ayuda")
        return l

    def _tabla(self) -> QTableWidget:
        columnas = ["Documento", "Cliente", "Teléfono", "Estado", ""]
        tabla = QTableWidget(len(CLIENTES_RECIENTES), len(columnas))
        tabla.setObjectName("tablaDatos")
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.verticalHeader().setVisible(False)
        tabla.setShowGrid(False)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.setFixedHeight(40 + t.ROW_HEIGHT * len(CLIENTES_RECIENTES) + 2)

        for fila, (doc, nombre, tel, activo) in enumerate(CLIENTES_RECIENTES):
            tabla.setItem(fila, 0, QTableWidgetItem(doc))
            tabla.setItem(fila, 1, QTableWidgetItem(nombre))
            tabla.setItem(fila, 2, QTableWidgetItem(tel))
            tabla.setCellWidget(fila, 3, self._celda(b.pildora_activo(activo)))
            if activo:
                accion = b.boton("Seleccionar", "secundario", 123)
                accion.clicked.connect(lambda _=False: self.ir_a("Agregar productos"))
            else:
                accion = b.boton("No disponible", "secundario", 133, deshabilitado=True)
            tabla.setCellWidget(fila, 4, self._celda(accion, alinear_derecha=True))
        return tabla

    def _celda(self, widget: QWidget, alinear_derecha: bool = False) -> QWidget:
        cont = QWidget()
        h = QHBoxLayout(cont)
        h.setContentsMargins(8, 0, 8, 0)
        h.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight if alinear_derecha else Qt.AlignmentFlag.AlignLeft)
        if not alinear_derecha:
            h.addStretch(1)
        return cont
