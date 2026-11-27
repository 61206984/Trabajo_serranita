"""Construye la hoja de estilos (QSS) a partir de los tokens. No se escriben colores sueltos en las pantallas."""
from app.estilos import tokens as t


def _insignias() -> str:
    reglas = []
    for estado, (texto, fondo) in t.BADGE.items():
        reglas.append(
            f'QLabel#insignia[estado="{estado}"] {{ color: {texto}; background: {fondo}; '
            f'border-radius: 14px; padding: 0 12px 0 10px; font-weight: 500; }}'
        )
    return "\n    ".join(reglas)


def hoja_de_estilos() -> str:
    return f"""
    QWidget {{ background: {t.BG}; color: {t.TEXT}; font-family: "{t.FONT_FAMILY}"; font-size: {t.SIZE_TABLE}px; }}
    QLabel {{ background: transparent; }}
    QLabel#titulo {{ font-size: {t.SIZE_TITLE}px; font-weight: 600; }}
    QLabel#subtitulo {{ font-size: {t.SIZE_SUBTITLE}px; color: {t.TEXT_SECONDARY}; }}
    QLabel#ayuda {{ font-size: {t.SIZE_HELP}px; color: {t.TEXT_SECONDARY}; }}
    QLabel#error {{ color: {t.DANGER_TEXT}; }}
    QLabel#marca {{ font-size: 18px; font-weight: 600; }}
    QLabel#avatar {{ background: {t.PRIMARY_SOFT}; color: {t.PRIMARY}; border-radius: 18px; font-weight: 600; }}
    QLabel#pillaExito {{
        background: {t.BADGE_OK_BG}; color: {t.BADGE["Entregado"][0]}; border-radius: 16px; padding: 6px 12px; font-weight: 500;
    }}
    QLabel#estadoLocalTitulo {{ color: {t.ON_PRIMARY}; font-size: 14px; font-weight: 500; }}
    QLabel#estadoLocalTexto {{ color: {t.ON_PRIMARY}; font-size: 12px; }}
    {_insignias()}
    QLabel#pildora[estado="activo"] {{ background: {t.BADGE_OK_BG}; color: {t.BADGE["Entregado"][0]}; border-radius: 14px; padding: 0 12px 0 10px; font-weight: 500; }}
    QLabel#pildora[estado="inactivo"] {{ background: {t.DANGER_BG}; color: {t.DANGER_TEXT}; border-radius: 14px; padding: 0 12px 0 10px; font-weight: 500; }}

    QFrame#tarjeta {{ background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 8px; }}
    QFrame#panelMarca {{ background: {t.PRIMARY}; }}
    QFrame#barraSuperior {{ background: {t.SURFACE}; border-bottom: 1px solid {t.BORDER}; }}
    QFrame#menuLateral {{ background: {t.PRIMARY}; }}
    QFrame#estadoLocal {{ background: rgba(255, 255, 255, 0.12); border-radius: 8px; }}
    QFrame#avisoError {{ background: {t.DANGER_BG}; border-radius: 8px; }}
    QLabel#avisoErrorTexto {{ color: {t.DANGER_TEXT}; }}

    QTableWidget#tablaDatos {{
        background: {t.SURFACE}; border: 1px solid {t.BORDER}; border-radius: 8px; gridline-color: {t.BORDER};
    }}
    QTableWidget#tablaDatos QHeaderView::section {{
        background: {t.BG}; color: {t.TEXT_SECONDARY}; border: none;
        border-bottom: 1px solid {t.BORDER}; padding: 0 16px; height: 40px; font-weight: 500;
    }}
    QTableWidget#tablaDatos::item {{ padding: 0 16px; border-bottom: 1px solid {t.BORDER}; }}

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
    QPushButton[variante="secundario"] {{
        background: {t.SURFACE}; color: {t.PRIMARY}; border: 1.5px solid {t.PRIMARY};
    }}
    QPushButton[variante="secundario"]:hover {{ background: {t.PRIMARY_SOFT}; }}
    QPushButton[variante="peligro"] {{ background: {t.DANGER}; color: {t.ON_PRIMARY}; }}
    QPushButton[variante="peligro"]:hover {{ background: {t.DANGER_HOVER}; }}
    QPushButton[variante="enlace"] {{ background: transparent; color: {t.PRIMARY}; font-weight: 500; }}
    QPushButton[variante="enlace"]:hover {{ text-decoration: underline; }}
    QPushButton[variante="menu"] {{
        background: transparent; color: {t.ON_PRIMARY}; text-align: left; padding-left: 12px;
        font-weight: 500; min-height: 44px;
    }}
    QPushButton[variante="menu"]:hover {{ background: {t.PRIMARY_HOVER}; }}
    QPushButton[variante="menu"][activo="true"] {{ background: rgba(255, 255, 255, 0.16); }}
    QPushButton:disabled {{ background: {t.BORDER}; color: {t.TEXT_SECONDARY}; }}
    QPushButton:focus {{ border: 2px solid {t.FOCUS}; }}
    """
