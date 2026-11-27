"""P12 Registrar producto (Almacenero). Valida RN-02 y código único (RF-07)."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget

from app.services import pedidos as svc
from app.ui.componentes import basicos as b


class PantallaRegistrarProducto(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Registrar producto", "Complete los datos del nuevo producto. Los campos con * son obligatorios."))
        raiz.addWidget(self._formulario())
        self.aviso = b.aviso("", "error")
        self.aviso.hide()
        raiz.addWidget(self.aviso)
        raiz.addStretch(1)

    def _formulario(self) -> QFrame:
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(20)
        fila1 = QHBoxLayout()
        fila1.setSpacing(16)
        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Ejemplo: QF-500")
        self.categoria = b.desplegable(["Queso", "Yogur", "Leche", "Mantequilla", "Manjar", "Helado", "Otro"])
        fila1.addLayout(b.etiquetado("Código del producto *", self.codigo, None, "Código único."), 1)
        fila1.addLayout(b.etiquetado("Categoría *", self.categoria), 1)
        v.addLayout(fila1)
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ejemplo: Queso fresco 250 g")
        v.addLayout(b.etiquetado("Nombre del producto *", self.nombre))
        fila2 = QHBoxLayout()
        fila2.setSpacing(16)
        self.unidad = b.desplegable(["unidad", "litro", "kg"])
        self.precio = QLineEdit()
        self.precio.setPlaceholderText("Ejemplo: 7.50")
        fila2.addLayout(b.etiquetado("Unidad de medida *", self.unidad), 1)
        fila2.addLayout(b.etiquetado("Precio unitario *", self.precio, None, "Debe ser mayor que cero"), 1)
        v.addLayout(fila2)
        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        registrar = b.boton("Registrar")
        registrar.clicked.connect(self._registrar)
        cancelar = b.boton("Cancelar", "secundario")
        cancelar.clicked.connect(lambda: self.ir_a("Productos y stock"))
        acciones.addWidget(registrar)
        acciones.addWidget(cancelar)
        acciones.addStretch(1)
        v.addLayout(acciones)
        return tarjeta

    def _registrar(self) -> None:
        precio = self.precio.text().replace("S/", "").replace(",", ".").strip()
        try:
            svc.registrar_producto(self.codigo.text(), self.nombre.text(), self.categoria.currentText(),
                                   self.unidad.currentText(), precio)
        except svc.ErrorNegocio as e:
            self.aviso.setText(str(e))
            self.aviso.show()
            return
        self.ir_a("Productos y stock")
