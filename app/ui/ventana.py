"""Ventana principal: barra superior, menú lateral según el rol (RF-02) y área de contenido."""
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from app.services import auth

# Menú por rol (informe, RF-02). Una opción no permitida no se muestra.
MENU_POR_ROL = {
    "Vendedor": ["Inicio", "Nuevo pedido", "Clientes", "Pedidos"],
    "Almacenero": ["Inicio", "Productos y stock"],
    "Gerente": ["Inicio", "Pedidos", "Reporte de ventas"],
}


class VentanaPrincipal(QWidget):
    def __init__(self, sesion: auth.SesionActual, parent=None):
        super().__init__(parent)
        self.sesion = sesion
        self.setMinimumSize(1024, 768)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)
        raiz.addWidget(self._barra_superior())

        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(0, 0, 0, 0)
        cuerpo.setSpacing(0)
        cuerpo.addWidget(self._menu_lateral())
        self.contenido = QStackedWidget()
        cuerpo.addWidget(self.contenido, 1)
        raiz.addLayout(cuerpo, 1)

        self._pantallas = {}
        self._ir_a("Inicio")

    def _barra_superior(self) -> QFrame:
        barra = QFrame()
        barra.setObjectName("barraSuperior")
        barra.setFixedHeight(64)
        h = QHBoxLayout(barra)
        h.setContentsMargins(24, 0, 24, 0)
        titulo = QLabel("La Serranita")
        titulo.setStyleSheet("font-size: 18px; font-weight: 600;")
        h.addWidget(titulo)
        h.addStretch(1)
        h.addWidget(QLabel(f"{self.sesion.username} · {self.sesion.rol}"))
        salir = QPushButton("Cerrar sesión")
        salir.setProperty("variante", "primario")
        salir.clicked.connect(self.window().cerrar_sesion)
        h.addWidget(salir)
        return barra

    def _menu_lateral(self) -> QFrame:
        menu = QFrame()
        menu.setObjectName("menuLateral")
        menu.setFixedWidth(240)
        v = QVBoxLayout(menu)
        v.setContentsMargins(16, 16, 16, 16)
        v.setSpacing(4)
        self._botones_menu = {}
        for opcion in MENU_POR_ROL.get(self.sesion.rol, ["Inicio"]):
            b = QPushButton(opcion)
            b.setProperty("variante", "menu")
            b.setProperty("activo", False)
            b.clicked.connect(lambda _=False, o=opcion: self._ir_a(o))
            v.addWidget(b)
            self._botones_menu[opcion] = b
        v.addStretch(1)
        return menu

    def _ir_a(self, opcion: str) -> None:
        for nombre, b in self._botones_menu.items():
            b.setProperty("activo", nombre == opcion)
            b.style().unpolish(b)
            b.style().polish(b)
        if opcion not in self._pantallas:
            # Pantallas de los demás módulos se agregan en pasos posteriores del plan.
            self._pantallas[opcion] = QLabel(f"{opcion} · en construcción")
            self.contenido.addWidget(self._pantallas[opcion])
        self.contenido.setCurrentWidget(self._pantallas[opcion])
