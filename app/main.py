"""Arranque de la aplicación: python -m app.main"""
import logging
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from app.estilos.tema import hoja_de_estilos
from app.services import auth
from app.ui.pantallas.login import PantallaLogin
from app.ui.ventana import VentanaPrincipal

logging.basicConfig(filename="serranita.log", level=logging.ERROR,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")


class Aplicacion(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lácteos La Serranita")
        self.resize(1280, 800)
        self.pila = QStackedWidget()
        self.setCentralWidget(self.pila)
        self.login = PantallaLogin()
        self.login.ingreso_correcto.connect(self._al_ingresar)
        self.pila.addWidget(self.login)

    def _al_ingresar(self, sesion: auth.SesionActual) -> None:
        principal = VentanaPrincipal(sesion)
        self.pila.addWidget(principal)
        self.pila.setCurrentWidget(principal)

    def cerrar_sesion(self) -> None:
        auth.cerrar_sesion()
        self.pila.setCurrentWidget(self.login)
        self.login.clave.clear()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(hoja_de_estilos())
    ventana = Aplicacion()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
