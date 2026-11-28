"""P03 Buscar cliente (Nuevo pedido, paso 1). Datos de la base de datos (RF-05).
Los inactivos se muestran pero no se pueden seleccionar (RN-07, RN-08)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from app.estilos import tokens as t
from app.repos import clientes as repo_clientes
from app.services.carrito import Cliente, carrito
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import ajustar_columnas

PASOS = [("Cliente", "actual"), ("Productos", "pendiente"), ("Resumen", "pendiente"), ("Registrado", "pendiente")]


class PantallaBuscarCliente(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        nuevo = b.boton("Cliente nuevo", "secundario", 150, icono="user-plus")
        nuevo.clicked.connect(lambda: self.ir_a("Registrar cliente"))
        raiz.addWidget(b.encabezado(
            "Nuevo pedido", "Busque al cliente por número de documento o nombre",
            pasos=PASOS, accion=None))

        barra = b.tarjeta()
        bl = QHBoxLayout(barra)
        bl.setContentsMargins(16, 16, 16, 16)
        bl.setSpacing(12)
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por documento o nombre")
        self.buscar.setFixedHeight(40)
        self.buscar.returnPressed.connect(self._cargar)
        bl.addWidget(self.buscar, 1)
        buscar = b.boton("Buscar", "primario", 88)
        buscar.clicked.connect(self._cargar)
        bl.addWidget(buscar)
        bl.addWidget(nuevo)
        raiz.addWidget(barra)

        self.titulo_tabla = QLabel("Clientes recientes")
        self.titulo_tabla.setStyleSheet("font-size: 18px; font-weight: 600;")
        raiz.addWidget(self.titulo_tabla)
        self.tabla = QTableWidget(0, 5)
        raiz.addWidget(self.tabla)
        self.vacio = QLabel("")
        self.vacio.setObjectName("ayuda")
        raiz.addWidget(self.vacio)
        ayuda = QLabel("Los clientes inactivos no se pueden asignar a un pedido nuevo.")
        ayuda.setObjectName("ayuda")
        raiz.addWidget(ayuda)
        raiz.addStretch(1)
        self._cargar()

    def _cargar(self) -> None:
        texto = self.buscar.text().strip()
        self.titulo_tabla.setText("Resultados" if texto else "Clientes recientes")
        filas = repo_clientes.buscar(texto, limite=20)
        self._llenar(filas)
        self.vacio.setText("No hay clientes que coincidan con la búsqueda." if not filas else "")

    def _llenar(self, filas) -> None:
        columnas = ["Documento", "Cliente", "Teléfono", "Estado", ""]
        tabla = self.tabla
        tabla.clear()
        tabla.setRowCount(len(filas))
        tabla.setColumnCount(len(columnas))
        tabla.setObjectName("tablaDatos")
        tabla.setHorizontalHeaderLabels(columnas)
        tabla.verticalHeader().setVisible(False)
        tabla.setShowGrid(False)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        tabla.verticalHeader().setDefaultSectionSize(t.ROW_HEIGHT)
        ajustar_columnas(tabla, anchos_fijos={3: 120})
        tabla.setFixedHeight(40 + t.ROW_HEIGHT * max(len(filas), 1) + 2)
        for fila, c in enumerate(filas):
            tabla.setItem(fila, 0, QTableWidgetItem(f"{c['tipo_doc']} {c['nro_doc']}"))
            tabla.setItem(fila, 1, QTableWidgetItem(c["nombre"]))
            tabla.setItem(fila, 2, QTableWidgetItem(c["telefono"] or "—"))
            tabla.setCellWidget(fila, 3, self._celda(b.pildora_activo(bool(c["activo"]))))
            if c["activo"]:
                accion = b.boton("Seleccionar", "secundario", 123)
                accion.clicked.connect(lambda _=False, c=c: self._seleccionar(c))
            else:
                accion = b.boton("No disponible", "secundario", 133, deshabilitado=True)
            tabla.setCellWidget(fila, 4, self._celda(accion, alinear_derecha=True))

    def _seleccionar(self, c: dict) -> None:
        carrito.seleccionar_cliente(Cliente(
            id_cliente=c["id_cliente"], tipo_doc=c["tipo_doc"], nro_doc=c["nro_doc"],
            nombre=c["nombre"], telefono=c["telefono"], direccion=c["direccion"]))
        self.ir_a("Agregar productos")

    def _celda(self, widget: QWidget, alinear_derecha: bool = False) -> QWidget:
        from PySide6.QtWidgets import QWidget as W
        cont = W()
        h = QHBoxLayout(cont)
        h.setContentsMargins(8, 0, 8, 0)
        h.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight if alinear_derecha else Qt.AlignmentFlag.AlignLeft)
        if not alinear_derecha:
            h.addStretch(1)
        return cont
