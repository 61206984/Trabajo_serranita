"""Construye la hoja de estilos (QSS) a partir de los tokens. No se escriben colores sueltos en las pantallas."""
from app.estilos import tokens as t


def hoja_de_estilos() -> str:
    return f"""
    QWidget {{ background: {t.BG}; color: {t.TEXT}; font-family: "{t.FONT_FAMILY}"; font-size: {t.SIZE_TABLE}px; }}
    QLabel#titulo {{ font-size: {t.SIZE_TITLE}px; font-weight: 600; }}
    QLabel#subtitulo {{ font-size: {t.SIZE_SUBTITLE}px; color: {t.TEXT_SECONDARY}; }}
    QLabel#ayuda {{ font-size: {t.SIZE_HELP}px; color: {t.TEXT_SECONDARY}; }}
    QLabel#error {{ color: {t.DANGER_TEXT}; }}

    QFrame#tarjeta {{ background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 7px; }}
    QFrame#panelMarca {{ background: {t.PRIMARY}; }}
    QFrame#barraSuperior {{ background: {t.SURFACE}; border-bottom: 1px solid {t.BORDER}; }}
    QFrame#menuLateral {{ background: {t.PRIMARY}; }}
    QFrame#avisoError {{ background: {t.DANGER_BG}; border-radius: 8px; }}
    QLabel#avisoErrorTexto {{ color: {t.DANGER_TEXT}; }}

    QLineEdit {{
        background: {t.SURFACE}; border: 1px solid {t.BORDER_INPUT}; border-radius: 5px;
        padding: 0 12px; min-height: {t.CONTROL_HEIGHT - 2}px; color: {t.TEXT};
    }}
    QLineEdit:focus {{ border: 2px solid {t.FOCUS}; }}
    QLineEdit[error="true"] {{ border: 2px solid {t.DANGER}; }}

    QPushButton {{
        border-radius: {t.RADIUS}px; min-height: {t.CONTROL_HEIGHT}px; padding: 0 16px;
        font-weight: 600; border: none;
    }}
    QPushButton[variante="primario"] {{ background: {t.PRIMARY}; color: {t.ON_PRIMARY}; }}
    QPushButton[variante="primario"]:hover {{ background: {t.PRIMARY_HOVER}; }}
    QPushButton[variante="primario"]:pressed {{ background: {t.PRIMARY_PRESSED}; }}
    QPushButton[variante="peligro"] {{ background: {t.DANGER}; color: {t.ON_PRIMARY}; }}
    QPushButton[variante="peligro"]:hover {{ background: {t.DANGER_HOVER}; }}
    QPushButton[variante="menu"] {{
        background: transparent; color: {t.ON_PRIMARY}; text-align: left; padding-left: 16px;
    }}
    QPushButton[variante="menu"]:hover {{ background: {t.PRIMARY_HOVER}; }}
    QPushButton[variante="menu"][activo="true"] {{ background: {t.PRIMARY_PRESSED}; }}
    QPushButton:disabled {{ background: {t.BORDER}; color: {t.TEXT_SECONDARY}; }}
    QPushButton:focus {{ border: 2px solid {t.FOCUS}; }}
    """
