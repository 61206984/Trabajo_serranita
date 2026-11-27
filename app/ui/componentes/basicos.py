"""Componentes reutilizables del Figma (Sistema de diseño). Cada pantalla los usa; ninguna pinta colores propios."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,
)


def boton(texto: str, variante: str = "primario", ancho: int | None = None,
          deshabilitado: bool = False) -> QPushButton:
    """Botón de 40 px. variante: primario | secundario | peligro | enlace."""
    b = QPushButton(texto)
    b.setProperty("variante", variante)
    b.setEnabled(not deshabilitado)
    if ancho:
        b.setFixedWidth(ancho)
    return b


def insignia(estado: str) -> QLabel:
    """Insignia de estado: siempre lleva texto (WCAG). Estados: Pendiente, Confirmado, Entregado, Cancelado."""
    etiqueta = QLabel(estado)
    etiqueta.setObjectName("insignia")
    etiqueta.setProperty("estado", estado)
    etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
    etiqueta.setFixedHeight(28)
    return etiqueta


def pildora_activo(activo: bool) -> QLabel:
    """Píldora Activo (verde) / Inactivo (rojo) del Figma, siempre con texto."""
    etiqueta = QLabel("Activo" if activo else "Inactivo")
    etiqueta.setObjectName("pildora")
    etiqueta.setProperty("estado", "activo" if activo else "inactivo")
    etiqueta.setAlignment(Qt.AlignmentFlag.AlignCenter)
    etiqueta.setFixedHeight(28)
    return etiqueta


def campo(etiqueta: str, valor: str = "", placeholder: str = "", ayuda: str | None = None,
          obligatorio: bool = False, ancho_fijo: int | None = None) -> QWidget:
    """Campo con etiqueta, entrada de 40 px y texto de ayuda opcional."""
    cont = QWidget()
    v = QVBoxLayout(cont)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(6)
    lbl = QLabel(etiqueta + (" *" if obligatorio and not etiqueta.endswith("*") else ""))
    lbl.setStyleSheet("font-weight: 500;")
    entrada = QLineEdit(valor)
    entrada.setPlaceholderText(placeholder)
    entrada.setFixedHeight(40)
    if ancho_fijo:
        cont.setFixedWidth(ancho_fijo)
    v.addWidget(lbl)
    v.addWidget(entrada)
    if ayuda:
        a = QLabel(ayuda)
        a.setObjectName("ayuda")
        v.addWidget(a)
    cont.entrada = entrada  # acceso desde la pantalla
    return cont


def encabezado(titulo: str, subtitulo: str, pasos: list[tuple[str, str]] | None = None,
               accion: QWidget | None = None) -> QWidget:
    """Título + subtítulo a la izquierda, indicador de pasos y acción a la derecha.
    pasos: lista de (nombre, estado) con estado 'actual' | 'pendiente' | 'hecho'."""
    cont = QWidget()
    h = QHBoxLayout(cont)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(16)
    bloque = QVBoxLayout()
    bloque.setSpacing(4)
    t = QLabel(titulo)
    t.setObjectName("titulo")
    s = QLabel(subtitulo)
    s.setObjectName("subtitulo")
    s.setStyleSheet("font-size: 14px;")
    bloque.addWidget(t)
    bloque.addWidget(s)
    h.addLayout(bloque)
    h.addStretch(1)
    if pasos:
        h.addWidget(indicador_pasos(pasos))
    if accion is not None:
        h.addWidget(accion)
    return cont


def indicador_pasos(pasos: list[tuple[str, str]]) -> QWidget:
    cont = QWidget()
    h = QHBoxLayout(cont)
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(8)
    for i, (nombre, estado) in enumerate(pasos, start=1):
        if i > 1:
            linea = QFrame()
            linea.setFixedSize(32, 2)
            linea.setStyleSheet("background: #6B7280;")
            h.addWidget(linea)
        n = QLabel(str(i))
        n.setFixedSize(28, 28)
        n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if estado == "actual":
            n.setStyleSheet("background: #1F4E8C; color: white; border-radius: 14px; font-weight: 600;")
        else:
            n.setStyleSheet("background: white; color: #4B5563; border: 1px solid #6B7280; "
                            "border-radius: 14px; font-weight: 600;")
        t = QLabel(nombre)
        t.setStyleSheet("font-weight: 500;" + ("" if estado == "actual" else " color: #4B5563;"))
        h.addWidget(n)
        h.addWidget(t)
    return cont


def tarjeta() -> QFrame:
    f = QFrame()
    f.setObjectName("tarjeta")
    return f
