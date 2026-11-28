"""P15 Clientes (vendedor) y P16 Dar de baja cliente. Baja lógica (RN-07): nunca se elimina."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget

from app.repos import clientes as repo_clientes
from app.services import pedidos as svc
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import celda, nueva_tabla, texto


class PantallaClientes(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        nuevo = b.boton("Cliente nuevo", "primario", icono="user-plus")
        nuevo.clicked.connect(lambda: self.ir_a("Registrar cliente"))
        raiz.addWidget(b.encabezado("Clientes", "Consulte y gestione los clientes", accion=nuevo))
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText("Buscar por documento o nombre")
        self.buscar.setFixedHeight(40)
        self.buscar.returnPressed.connect(self.filtrar)
        raiz.addWidget(self.buscar)
        self.zona = QVBoxLayout()
        raiz.addLayout(self.zona)
        raiz.addStretch(1)
        self.filtrar()

    def filtrar(self) -> None:
        filas = repo_clientes.buscar(self.buscar.text(), limite=100)
        while self.zona.count():
            it = self.zona.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        tabla = nueva_tabla(["Documento", "Cliente", "Teléfono", "Estado", ""], max(len(filas), 1), anchos_fijos={3: 120})
        for fila, c in enumerate(filas):
            tabla.setItem(fila, 0, texto(f"{c['tipo_doc']} {c['nro_doc']}"))
            tabla.setItem(fila, 1, texto(c["nombre"]))
            tabla.setItem(fila, 2, texto(c["telefono"] or "—"))
            tabla.setCellWidget(fila, 3, celda(b.pildora_activo(bool(c["activo"]))))
            if c["activo"]:
                baja = b.boton("Dar de baja", "secundario", 150, icono="ban")
                baja.clicked.connect(lambda _=False, c=c: self._dar_de_baja(c))
                tabla.setCellWidget(fila, 4, celda(baja, derecha=True))
        self.zona.addWidget(tabla)

    def _dar_de_baja(self, c: dict) -> None:
        r = QMessageBox.question(
            self, "Dar de baja al cliente",
            f"¿Dar de baja a {c['nombre']}? Quedará inactivo y no podrá asignarse a pedidos nuevos. "
            "Su historial se conserva.")
        if r == QMessageBox.StandardButton.Yes:
            svc.dar_de_baja_cliente(c["id_cliente"])
            self.filtrar()
