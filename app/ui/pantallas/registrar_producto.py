"""P12 Registrar producto (Almacenero). Medidas y textos del Figma (1280×800)."""
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget

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
        raiz.addStretch(1)

    def _formulario(self) -> QFrame:
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(32, 32, 32, 32)
        v.setSpacing(20)

        fila1 = QHBoxLayout()
        fila1.setSpacing(16)
        codigo = QLineEdit("QF-250")
        fila1.addLayout(b.etiquetado("Código del producto *", codigo, None, "Código único. Ejemplo: QF-500"), 1)
        fila1.addLayout(b.etiquetado("Categoría *", b.desplegable(
            ["Queso", "Yogur", "Leche", "Mantequilla", "Manjar", "Helado"])), 1)
        v.addLayout(fila1)

        v.addLayout(b.etiquetado("Nombre del producto *", QLineEdit("Queso fresco 250 g")))

        fila2 = QHBoxLayout()
        fila2.setSpacing(16)
        fila2.addLayout(b.etiquetado("Unidad de medida *", b.desplegable(["Unidad", "Litro", "Kg"])), 1)
        fila2.addLayout(b.etiquetado("Precio unitario *", QLineEdit("S/ 7.50"), None,
                                     "Debe ser mayor que cero"), 1)
        v.addLayout(fila2)

        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        acciones.addWidget(b.boton("Registrar"))
        cancelar = b.boton("Cancelar", "secundario")
        cancelar.clicked.connect(lambda: self.ir_a("Productos y stock"))
        acciones.addWidget(cancelar)
        acciones.addStretch(1)
        v.addLayout(acciones)
        return tarjeta
