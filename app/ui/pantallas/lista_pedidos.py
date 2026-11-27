"""P08 Lista de pedidos (RF-14). Filtra por estado, cliente y fechas en la base de datos."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.repos import pedidos as repo_pedidos
from app.services.fechas import parse_fecha
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto


class PantallaListaPedidos(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        nuevo = b.boton("Nuevo pedido", "primario")
        nuevo.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        raiz.addWidget(b.encabezado("Pedidos", "Consulte y filtre los pedidos registrados", accion=nuevo))
        raiz.addWidget(self._filtros())
        self.zona_tabla = QVBoxLayout()
        raiz.addLayout(self.zona_tabla)
        self.info = QLabel("")
        self.info.setObjectName("secundario")
        raiz.addWidget(self.info)
        raiz.addStretch(1)
        self.filtrar()

    def _campo(self, etiqueta: str, entrada, ancho: int | None = None) -> QVBoxLayout:
        v = QVBoxLayout()
        v.setSpacing(6)
        lbl = QLabel(etiqueta)
        lbl.setObjectName("etiquetaCampo")
        entrada.setFixedHeight(40)
        if ancho:
            entrada.setFixedWidth(ancho)
        v.addWidget(lbl)
        v.addWidget(entrada)
        return v

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        self.estado = QComboBox()
        self.estado.addItems(["Todos", "Pendiente", "Confirmado", "Entregado", "Cancelado"])
        self.cliente = QLineEdit()
        self.cliente.setPlaceholderText("Buscar por nombre o documento")
        self.desde = QLineEdit("")
        self.desde.setPlaceholderText("dd/mm/aaaa")
        self.hasta = QLineEdit("")
        self.hasta.setPlaceholderText("dd/mm/aaaa")
        h.addLayout(self._campo("Estado", self.estado, 180))
        h.addLayout(self._campo("Cliente", self.cliente), 1)
        h.addLayout(self._campo("Desde", self.desde, 150))
        h.addLayout(self._campo("Hasta", self.hasta, 150))
        filtrar = b.boton("Filtrar", "primario")
        filtrar.clicked.connect(self.filtrar)
        h.addWidget(filtrar, 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def filtrar(self) -> None:
        desde = parse_fecha(self.desde.text())
        hasta = parse_fecha(self.hasta.text())
        filas = repo_pedidos.listar(self.estado.currentText(), self.cliente.text(), desde, hasta)
        while self.zona_tabla.count():
            it = self.zona_tabla.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        tabla = nueva_tabla(["N.º", "Fecha", "Cliente", "Vendedor", "Estado", "Total"], max(len(filas), 1))
        for fila, p in enumerate(filas):
            enlace = b.boton(f"{p['id_pedido']:04d}", "enlace")
            enlace.clicked.connect(lambda _=False, i=p["id_pedido"]: self.ir_a("Detalle del pedido", pedido_id=i))
            tabla.setCellWidget(fila, 0, celda(enlace))
            tabla.setItem(fila, 1, texto(p["fecha_pedido"].strftime("%d/%m/%Y")))
            tabla.setItem(fila, 2, texto(p["cliente"]))
            tabla.setItem(fila, 3, texto(p["vendedor"]))
            tabla.setCellWidget(fila, 4, celda(b.insignia(p["estado"])))
            tabla.setItem(fila, 5, texto(f"S/ {float(p['total']):.2f}", derecha=True))
        self.zona_tabla.addWidget(tabla)
        self.info.setText(f"{len(filas)} pedidos" if filas else "No hay pedidos que coincidan con los filtros.")
