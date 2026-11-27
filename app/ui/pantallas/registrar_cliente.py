"""P04 Registrar cliente (Nuevo pedido, paso 1). Medidas y textos del Figma (1280×800).

Valida RN-01 (documento único, 8 dígitos DNI / 11 RUC) y RN-02 antes de guardar.
La inserción real en la base de datos se conecta en el módulo de clientes.
"""
import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget,
)

from app.ui.componentes import basicos as b

PASOS = [("Cliente", "actual"), ("Productos", "pendiente"), ("Resumen", "pendiente"), ("Registrado", "pendiente")]


class PantallaRegistrarCliente(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)

        raiz.addWidget(b.encabezado(
            "Registrar cliente",
            "Complete los datos del nuevo cliente. Los campos con * son obligatorios.",
            pasos=PASOS))

        form = b.tarjeta()
        fv = QVBoxLayout(form)
        fv.setContentsMargins(32, 32, 32, 32)
        fv.setSpacing(20)

        # Fila 1: tipo y número de documento
        f1 = QHBoxLayout()
        f1.setSpacing(16)
        self.tipo = QComboBox()
        self.tipo.addItems(["RUC", "DNI"])
        self.tipo.setFixedHeight(40)
        self.tipo.currentIndexChanged.connect(self._validar_documento)
        self.documento = QLineEdit("")
        self.documento.setFixedHeight(40)
        self.documento.setPlaceholderText("Número de documento")
        self.documento.textChanged.connect(self._validar_documento)
        self.ayuda_doc = QLabel("11 dígitos para RUC · 8 dígitos para DNI")
        self.ayuda_doc.setObjectName("ayuda")
        f1.addLayout(self._bloque("Tipo de documento *", self.tipo))
        f1.addLayout(self._bloque("Número de documento *", self.documento, self.ayuda_doc))
        fv.addLayout(f1)

        # Fila 2: nombre o razón social
        self.nombre = QLineEdit()
        self.nombre.setFixedHeight(40)
        fv.addLayout(self._bloque("Nombre o razón social *", self.nombre))

        # Fila 3: teléfono y correo
        f3 = QHBoxLayout()
        f3.setSpacing(16)
        self.telefono = QLineEdit()
        self.telefono.setFixedHeight(40)
        self.correo = QLineEdit()
        self.correo.setFixedHeight(40)
        f3.addLayout(self._bloque("Teléfono", self.telefono))
        f3.addLayout(self._bloque("Correo electrónico", self.correo))
        fv.addLayout(f3)

        # Fila 4: dirección
        self.direccion = QLineEdit()
        self.direccion.setFixedHeight(40)
        fv.addLayout(self._bloque("Dirección", self.direccion))

        # Acciones
        acciones = QHBoxLayout()
        acciones.setSpacing(12)
        self.btn_registrar = b.boton("Registrar", "primario")
        self.btn_registrar.clicked.connect(self._registrar)
        cancelar = b.boton("Cancelar", "secundario")
        cancelar.clicked.connect(lambda: self.ir_a("Nuevo pedido"))
        acciones.addWidget(self.btn_registrar)
        acciones.addWidget(cancelar)
        acciones.addStretch(1)
        fv.addLayout(acciones)

        raiz.addWidget(form)
        raiz.addStretch(1)

    def _bloque(self, etiqueta: str, entrada: QWidget, ayuda: QWidget | None = None) -> QVBoxLayout:
        v = QVBoxLayout()
        v.setSpacing(6)
        lbl = QLabel(etiqueta)
        lbl.setStyleSheet("font-weight: 500;")
        v.addWidget(lbl)
        v.addWidget(entrada)
        if ayuda is not None:
            v.addWidget(ayuda)
        return v

    def _longitud_esperada(self) -> int:
        return 11 if self.tipo.currentText() == "RUC" else 8

    def _validar_documento(self) -> None:
        texto = self.documento.text().strip()
        valido = bool(re.fullmatch(r"\d+", texto)) and len(texto) == self._longitud_esperada()
        if texto == "":
            valido = True  # no marca error antes de escribir
        self.documento.setProperty("error", not valido)
        self.documento.style().unpolish(self.documento)
        self.documento.style().polish(self.documento)
        self.ayuda_doc.setStyleSheet("" if valido else "color: #991B1B;")
        self.ayuda_doc.setText(
            "11 dígitos para RUC · 8 dígitos para DNI" if valido
            else f"Debe tener {self._longitud_esperada()} dígitos para {self.tipo.currentText()}."
        )

    def _registrar(self) -> None:
        # Validación de RN-01 y RN-02 en el formulario; la BD también lo valida.
        if not self.nombre.text().strip():
            self.nombre.setProperty("error", True)
            self.nombre.style().unpolish(self.nombre)
            self.nombre.style().polish(self.nombre)
            return
        self._validar_documento()
        if self.documento.property("error"):
            return
        self.ir_a("Agregar productos")
