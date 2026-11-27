"""Ventana principal (P02): barra superior, menú lateral según el rol (RF-02) y área de contenido.

El inicio es el mismo para los tres roles. Cambia el menú lateral y el nombre de la persona.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

from app.services import auth
from app.ui.pantallas.agregar_productos import PantallaAgregarProductos
from app.ui.pantallas.buscar_cliente import PantallaBuscarCliente
from app.ui.pantallas.detalle_pedido import PantallaDetallePedido
from app.ui.pantallas.inicio import PantallaInicio
from app.ui.pantallas.lista_pedidos import PantallaListaPedidos
from app.ui.pantallas.pedido_registrado import PantallaPedidoRegistrado
from app.ui.pantallas.registrar_cliente import PantallaRegistrarCliente
from app.ui.pantallas.resumen_pedido import PantallaResumenPedido

# Menú por rol (informe, RF-02). Una opción no permitida no se muestra.
MENU_POR_ROL = {
    "Vendedor": ["Inicio", "Nuevo pedido", "Clientes", "Pedidos"],
    "Almacenero": ["Inicio", "Productos y stock"],
    "Gerente": ["Inicio", "Pedidos", "Reporte de ventas"],
}


def _iniciales(nombre: str) -> str:
    partes = [p for p in nombre.split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[1][0]).upper()


class VentanaPrincipal(QWidget):
    cerrar_sesion_solicitada = Signal()

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
        self.contenido.setObjectName("contenido")
        cuerpo.addWidget(self.contenido, 1)
        raiz.addLayout(cuerpo, 1)

        self._pantallas = {}
        self._ir_a("Inicio")

    # --- Barra superior (Figma: Barra superior, 64 px) ---
    def _barra_superior(self) -> QFrame:
        barra = QFrame()
        barra.setObjectName("barraSuperior")
        barra.setFixedHeight(64)
        h = QHBoxLayout(barra)
        h.setContentsMargins(24, 0, 24, 0)
        h.setSpacing(16)

        marca = QLabel("La Serranita")
        marca.setObjectName("marca")
        subtitulo = QLabel("Sistema de pedidos y ventas")
        subtitulo.setObjectName("ayuda")
        bloque = QVBoxLayout()
        bloque.setSpacing(0)
        bloque.addWidget(marca)
        bloque.addWidget(subtitulo)
        h.addLayout(bloque)
        h.addStretch(1)

        estado_bd = QLabel("Base de datos local")
        estado_bd.setObjectName("pillaExito")
        h.addWidget(estado_bd)

        usuario = QHBoxLayout()
        usuario.setSpacing(10)
        avatar = QLabel(_iniciales(self.sesion.nombre))
        avatar.setObjectName("avatar")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFixedSize(36, 36)
        datos = QVBoxLayout()
        datos.setSpacing(0)
        nombre = QLabel(self.sesion.nombre)
        nombre.setStyleSheet("font-weight: 500;")
        rol = QLabel(self.sesion.rol)
        rol.setObjectName("ayuda")
        datos.addWidget(nombre)
        datos.addWidget(rol)
        usuario.addWidget(avatar)
        usuario.addLayout(datos)
        h.addLayout(usuario)

        salir = QPushButton("Cerrar sesión")
        salir.setProperty("variante", "secundario")
        salir.clicked.connect(self.cerrar_sesion_solicitada.emit)
        h.addWidget(salir)
        return barra

    # --- Menú lateral (Figma: Menú lateral, 240 px, fondo primario) ---
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

        pie = QFrame()
        pie.setObjectName("estadoLocal")
        pv = QVBoxLayout(pie)
        pv.setContentsMargins(12, 12, 12, 12)
        pv.setSpacing(4)
        titulo = QLabel("Datos en este equipo")
        titulo.setObjectName("estadoLocalTitulo")
        texto = QLabel("Sin conexión a la nube. Respaldo diario a las 06:00.")
        texto.setObjectName("estadoLocalTexto")
        texto.setWordWrap(True)
        pv.addWidget(titulo)
        pv.addWidget(texto)
        v.addWidget(pie)
        return menu

    def _ir_a(self, opcion: str) -> None:
        for nombre, b in self._botones_menu.items():
            b.setProperty("activo", nombre == opcion)
            b.style().unpolish(b)
            b.style().polish(b)
        if opcion not in self._pantallas:
            self._pantallas[opcion] = self._crear(opcion)
            self.contenido.addWidget(self._pantallas[opcion])
        self.contenido.setCurrentWidget(self._pantallas[opcion])

    def _crear(self, nombre: str) -> QWidget:
        """Crea la pantalla. Las que aún no están diseñadas en código muestran un marcador."""
        if nombre == "Inicio":
            return PantallaInicio(self.sesion.nombre)
        if nombre == "Nuevo pedido":
            return PantallaBuscarCliente(self._ir_a)
        if nombre == "Registrar cliente":
            return PantallaRegistrarCliente(self._ir_a)
        if nombre == "Agregar productos":
            return PantallaAgregarProductos(self._ir_a)
        if nombre == "Resumen del pedido":
            return PantallaResumenPedido(self._ir_a)
        if nombre == "Pedido registrado":
            return PantallaPedidoRegistrado(self._ir_a)
        if nombre == "Pedidos":
            return PantallaListaPedidos(self._ir_a)
        if nombre == "Detalle del pedido":
            return PantallaDetallePedido(self._ir_a)
        marcador = QLabel(f"{nombre} · pendiente de copiar desde Figma")
        marcador.setContentsMargins(32, 32, 32, 32)
        return marcador
