"""P01 Inicio de sesión. Replica el Figma: panel de marca azul a la izquierda y tarjeta de formulario a la derecha.

Medidas del Figma (ventana de 1280×800):
- Panel de marca: 560 px de ancho, fondo #1F4E8C.
- Tarjeta de formulario: 399×389 en (720, 186), fondo blanco, radio 7.5, borde #E5E7EB.
- Campos: 333×39 en x=754 (y=320 y y=406), radio 5.5, borde #6B7280.
- Botón Ingresar: 334×40 en (753, 466), radio 6, fondo #1F4E8C.
"""
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)

from app.services import auth


class PantallaLogin(QWidget):
    ingreso_correcto = Signal(object)  # envía la SesionActual

    def __init__(self, parent=None):
        super().__init__(parent)
        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._panel_marca(), 0)
        raiz.addWidget(self._zona_formulario(), 1)

    # --- Panel de marca (izquierda) ---
    def _panel_marca(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panelMarca")
        panel.setFixedWidth(560)
        v = QVBoxLayout(panel)
        v.setContentsMargins(64, 184, 64, 0)
        v.setSpacing(0)

        logo = QLabel("Lácteos La Serranita")
        logo.setStyleSheet("color: white; font-size: 24px; font-weight: 600;")
        v.addWidget(logo)

        v.addSpacing(260 - 184 - 48)
        titulo = QLabel("Pedidos, clientes y stock en un solo lugar")
        titulo.setStyleSheet("color: white; font-size: 24px; font-weight: 600;")
        titulo.setWordWrap(True)
        v.addWidget(titulo)

        v.addSpacing(16)
        texto = QLabel(
            "Reemplaza las hojas de Excel y los talonarios por un sistema que trabaja "
            "sobre la base de datos de la empresa, sin depender de la nube."
        )
        texto.setStyleSheet("color: #DCE6F4; font-size: 16px;")
        texto.setWordWrap(True)
        v.addWidget(texto)

        v.addSpacing(40)
        for beneficio in (
            "Consulte el stock antes de ofrecer mercadería",
            "Siga cada pedido: pendiente, confirmado o entregado",
            "Un solo registro de clientes para todo el equipo",
        ):
            etiqueta = QLabel("•  " + beneficio)
            etiqueta.setStyleSheet("color: white; font-size: 16px;")
            v.addWidget(etiqueta)
            v.addSpacing(16)
        v.addStretch(1)
        return panel

    # --- Zona de formulario (derecha) ---
    def _zona_formulario(self) -> QWidget:
        zona = QWidget()
        h = QHBoxLayout(zona)
        h.setContentsMargins(0, 0, 0, 0)
        h.addStretch(1)
        h.addWidget(self._tarjeta(), 0)
        h.addStretch(1)
        return zona

    def _tarjeta(self) -> QFrame:
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setFixedSize(399, 389)
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(33, 33, 33, 33)
        v.setSpacing(0)

        titulo = QLabel("Iniciar sesión")
        titulo.setObjectName("titulo")
        subtitulo = QLabel("Ingrese con su usuario del sistema")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setStyleSheet("font-size: 14px;")
        v.addWidget(titulo)
        v.addWidget(subtitulo)

        v.addSpacing(40)
        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuario")
        self._campo(v, "Usuario", self.usuario)

        v.addSpacing(16)
        self.clave = QLineEdit()
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setPlaceholderText("Contraseña")
        self._campo(v, "Contraseña", self.clave)

        self.aviso = QFrame()
        self.aviso.setObjectName("avisoError")
        self.aviso.setVisible(False)
        av = QHBoxLayout(self.aviso)
        av.setContentsMargins(12, 0, 12, 0)
        self.aviso_texto = QLabel("Usuario o contraseña incorrectos.")
        self.aviso_texto.setObjectName("avisoErrorTexto")
        av.addWidget(self.aviso_texto)
        v.addSpacing(12)
        v.addWidget(self.aviso)

        v.addSpacing(16)
        self.boton = QPushButton("Ingresar")
        self.boton.setProperty("variante", "primario")
        self.boton.setDefault(True)
        self.boton.clicked.connect(self._intentar_ingresar)
        v.addWidget(self.boton)

        v.addSpacing(12)
        ayuda = QLabel("¿Olvidó su contraseña? Consulte al supervisor.")
        ayuda.setObjectName("ayuda")
        v.addWidget(ayuda)
        v.addStretch(1)

        self.usuario.returnPressed.connect(self.clave.setFocus)
        self.clave.returnPressed.connect(self._intentar_ingresar)
        return tarjeta

    def _campo(self, layout: QVBoxLayout, etiqueta: str, entrada: QLineEdit) -> None:
        lbl = QLabel(etiqueta)
        lbl.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(lbl)
        layout.addSpacing(6)
        entrada.setFixedHeight(40)
        layout.addWidget(entrada)

    def _intentar_ingresar(self) -> None:
        self.boton.setEnabled(False)  # evita doble envío
        try:
            sesion = auth.iniciar_sesion(self.usuario.text(), self.clave.text())
        except auth.CredencialesInvalidas:
            self._mostrar_error(True)
            self.clave.clear()
            self.clave.setFocus()
            return
        except Exception:
            # Error técnico: se registra con detalle en serranita.log y el usuario ve un mensaje genérico.
            logging.getLogger(__name__).exception("Fallo al iniciar sesión")
            self._mostrar_error(False, "No se pudo conectar con la base de datos local.")
            return
        finally:
            self.boton.setEnabled(True)
        self._mostrar_error(False)
        self.ingreso_correcto.emit(sesion)

    def _mostrar_error(self, invalido: bool, mensaje: str | None = None) -> None:
        for campo in (self.usuario, self.clave):
            campo.setProperty("error", invalido)
            campo.style().unpolish(campo)
            campo.style().polish(campo)
        self.aviso_texto.setText(mensaje or "Usuario o contraseña incorrectos.")
        self.aviso.setVisible(invalido or mensaje is not None)
