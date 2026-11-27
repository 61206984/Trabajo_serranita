"""P14 Reporte de ventas (Gerente, RF-15). Totales desde la base de datos; excluye cancelados."""
from PySide6.QtCore import Qt
import csv

from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget
from datetime import date

from app.repos import reportes
from app.services.fechas import parse_fecha
from app.ui.componentes import basicos as b
from app.ui.componentes.tablas import nueva_tabla, texto


class PantallaReporteVentas(QWidget):
    def __init__(self, ir_a, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 32, 32, 32)
        raiz.setSpacing(24)
        raiz.addWidget(b.encabezado(
            "Reporte de ventas", "Ventas por rango de fechas (pedidos no cancelados)"))
        raiz.addWidget(self._filtros())
        self.zona = QVBoxLayout()
        raiz.addLayout(self.zona, 1)
        ayuda = QLabel("El total del reporte coincide con la suma de los pedidos considerados.")
        ayuda.setObjectName("ayuda")
        raiz.addWidget(ayuda)
        self._mostrar()  # al abrir la pantalla solo se muestra; no se guarda archivo

    def _filtros(self) -> QFrame:
        tarjeta = b.tarjeta()
        h = QHBoxLayout(tarjeta)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(16)
        hoy = date.today().strftime("%d/%m/%Y")
        self.desde = QLineEdit(date.today().replace(day=1).strftime("%d/%m/%Y"))
        self.hasta = QLineEdit(hoy)
        h.addLayout(b.etiquetado("Desde (dd/mm/aaaa)", self.desde, 180), 0)
        h.addLayout(b.etiquetado("Hasta (dd/mm/aaaa)", self.hasta, 180), 0)
        h.addStretch(1)
        generar = b.boton("Generar reporte")
        generar.clicked.connect(self.generar)
        self._datos = None
        h.addWidget(generar, 0, Qt.AlignmentFlag.AlignBottom)
        return tarjeta

    def _kpi(self, titulo: str, valor: str) -> QFrame:
        tarjeta = b.tarjeta()
        v = QVBoxLayout(tarjeta)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(4)
        t = QLabel(titulo)
        t.setObjectName("secundario")
        n = QLabel(valor)
        n.setObjectName("total")
        v.addWidget(t)
        v.addWidget(n)
        return tarjeta

    def generar(self) -> None:
        """Botón «Generar reporte»: muestra el reporte y pide dónde guardar el CSV."""
        if self._mostrar():
            self._guardar_csv()

    def _mostrar(self) -> bool:
        while self.zona.count():
            it = self.zona.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    sub = it.layout().takeAt(0)
                    if sub.widget():
                        sub.widget().deleteLater()
        desde, hasta = parse_fecha(self.desde.text()), parse_fecha(self.hasta.text())
        if desde is None or hasta is None or desde > hasta:
            self.zona.addWidget(b.aviso("Ingrese un rango válido en formato dd/mm/aaaa.", "error"))
            return False
        self._datos = None
        resumen = reportes.resumen(desde, hasta)
        filas = reportes.ventas_por_producto(desde, hasta)
        total = float(resumen["total"])
        unidades = sum(float(f["unidades"]) for f in filas)

        indicadores = QHBoxLayout()
        indicadores.setSpacing(16)
        indicadores.addWidget(self._kpi("Total vendido", f"S/ {total:,.2f}"), 1)
        indicadores.addWidget(self._kpi("Pedidos considerados", str(resumen["pedidos"])), 1)
        indicadores.addWidget(self._kpi("Unidades vendidas", f"{unidades:g}"), 1)
        self.zona.addLayout(indicadores)

        tabla = nueva_tabla(["Código", "Producto", "Unidades", "Ventas"], len(filas) + 1)
        for fila, f in enumerate(filas):
            tabla.setItem(fila, 0, texto(f["codigo"]))
            tabla.setItem(fila, 1, texto(f["nombre"]))
            tabla.setItem(fila, 2, texto(f"{float(f['unidades']):g}", derecha=True))
            tabla.setItem(fila, 3, texto(f"S/ {float(f['ventas']):,.2f}", derecha=True))
        n = len(filas)
        tabla.setItem(n, 1, texto("Total del reporte"))
        tabla.setItem(n, 2, texto(f"{unidades:g}", derecha=True))
        tabla.setItem(n, 3, texto(f"S/ {total:,.2f}", derecha=True))
        self.zona.addWidget(tabla)
        self.zona.addStretch(1)
        self._datos = (desde, hasta, filas, total, unidades, resumen["pedidos"])
        return True


    def _guardar_csv(self) -> None:
        """Al generar el reporte se pregunta dónde guardar el CSV. Cancelar solo omite el archivo."""
        desde, hasta, filas, total, unidades, pedidos = self._datos
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte de ventas",
            f"reporte_ventas_{desde:%Y%m%d}_{hasta:%Y%m%d}.csv", "CSV (*.csv)")
        if not ruta:
            return
        if not ruta.lower().endswith(".csv"):
            ruta += ".csv"
        # utf-8-sig: Excel en Windows abre las tildes correctamente.
        with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Reporte de ventas Lácteos La Serranita"])
            w.writerow(["Desde", desde.strftime("%d/%m/%Y"), "Hasta", hasta.strftime("%d/%m/%Y")])
            w.writerow(["Pedidos considerados (sin cancelados)", pedidos])
            w.writerow([])
            w.writerow(["Código", "Producto", "Unidades", "Ventas (S/)"])
            for f_ in filas:
                w.writerow([f_["codigo"], f_["nombre"], f"{float(f_['unidades']):g}", f"{float(f_['ventas']):.2f}"])
            w.writerow(["", "Total del reporte", f"{unidades:g}", f"{total:.2f}"])
        QMessageBox.information(self, "Reporte guardado", f"Archivo guardado en:\n{ruta}")
