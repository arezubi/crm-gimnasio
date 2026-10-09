"""Tema oscuro común para todos los gráficos de matplotlib y página base de gráficos."""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from gui.componentes import Pagina
from informes.estadisticas import anios_con_datos

# Mismos colores que resources/estilo.qss
COLOR_FONDO = "#1f1f1f"
COLOR_TEXTO = "#f2f2f2"
COLOR_SECUNDARIO = "#9a9a9a"
COLOR_REJILLA = "#2c2c2c"
COLOR_ACENTO = "#ff6a00"


def aplicar_estilo(figura, ejes):
    figura.set_facecolor(COLOR_FONDO)
    ejes.set_facecolor(COLOR_FONDO)
    for lado in ("top", "right", "left"):
        ejes.spines[lado].set_visible(False)
    ejes.spines["bottom"].set_color(COLOR_REJILLA)
    ejes.tick_params(colors=COLOR_SECUNDARIO, length=0, labelsize=10)
    ejes.yaxis.grid(True, color=COLOR_REJILLA, linewidth=0.8)
    ejes.set_axisbelow(True)                # la rejilla queda detrás de las barras
    ejes.xaxis.label.set_color(COLOR_SECUNDARIO)
    ejes.yaxis.label.set_color(COLOR_SECUNDARIO)


def sin_datos(ejes):
    ejes.text(0.5, 0.5, "Todavía no hay datos", ha="center", va="center",
              transform=ejes.transAxes, color=COLOR_SECUNDARIO, fontsize=12)
    ejes.set_xticks([])
    ejes.set_yticks([])
    ejes.spines["bottom"].set_visible(False)


def dibujar_barras(ejes, etiquetas, valores, formato=lambda v: f"{v:g}"):
    """Barras verticales naranjas con el valor encima de cada una."""
    etiquetas = [str(e) for e in etiquetas]
    valores = [float(v) for v in valores]
    if not any(valores):
        sin_datos(ejes)
        return
    barras = ejes.bar(etiquetas, valores, color=COLOR_ACENTO, width=0.6)
    ejes.bar_label(barras, labels=[formato(v) if v else "" for v in valores],
                   color=COLOR_TEXTO, padding=4, fontsize=9)
    ejes.margins(y=0.15)
    if son_enteros(valores):
        ejes.yaxis.set_major_locator(MaxNLocator(integer=True))   # nada de "2.5 alumnos"                    # deja hueco para el texto de la barra más alta


def dibujar_barras_horizontales(ejes, etiquetas, valores, formato=lambda v: f"{v:g}"):
    """Barras horizontales, la mayor arriba. Se leen mejor que una tarta."""
    etiquetas = [str(e) for e in etiquetas]
    valores = [float(v) for v in valores]
    if not any(valores):
        sin_datos(ejes)
        return
    barras = ejes.barh(etiquetas, valores, color=COLOR_ACENTO, height=0.6)
    ejes.invert_yaxis()
    ejes.yaxis.grid(False)
    ejes.xaxis.grid(True, color=COLOR_REJILLA, linewidth=0.8)
    ejes.tick_params(axis="y", labelsize=11, labelcolor=COLOR_TEXTO)
    ejes.bar_label(barras, labels=[formato(v) for v in valores],
                   color=COLOR_TEXTO, padding=6, fontsize=10)
    ejes.margins(x=0.12)
    if son_enteros(valores):
        ejes.xaxis.set_major_locator(MaxNLocator(integer=True))


def son_enteros(valores):
    return all(float(v).is_integer() for v in valores)


def euros_cortos(valor):
    return f"{valor:g} €"


class PaginaGrafico(Pagina):
    """Página con un gráfico dentro de una tarjeta y, opcionalmente, un selector de año.
    Las clases hijas solo tienen que implementar dibujar()."""

    def __init__(self, cursor, titulo, subtitulo="", con_selector_anio=False):
        super().__init__(titulo, subtitulo)
        self.cursor = cursor

        self.combo_anio = None
        if con_selector_anio:
            self.combo_anio = QComboBox()
            self.combo_anio.setMinimumWidth(110)
            self.combo_anio.currentIndexChanged.connect(self.redibujar)
            fila = QHBoxLayout()
            fila.addWidget(QLabel("Año:"))
            fila.addWidget(self.combo_anio)
            fila.addStretch()
            self.layout_pagina.addLayout(fila)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(16, 16, 16, 16)

        self.figura = Figure(figsize=(8, 4.5))
        self.ejes = self.figura.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figura)
        layout_tarjeta.addWidget(self.canvas)
        self.layout_pagina.addWidget(tarjeta, 1)

    def anio_seleccionado(self):
        return self.combo_anio.currentData()

    def recargar(self):
        if self.combo_anio is not None:
            anio_anterior = self.combo_anio.currentData()
            self.combo_anio.blockSignals(True)      # que no redibuje con cada addItem
            self.combo_anio.clear()
            for anio in anios_con_datos(self.cursor):
                self.combo_anio.addItem(str(anio), anio)
            indice = self.combo_anio.findData(anio_anterior)
            self.combo_anio.setCurrentIndex(max(indice, 0))
            self.combo_anio.blockSignals(False)
        self.redibujar()

    def redibujar(self, *args):
        self.ejes.clear()
        aplicar_estilo(self.figura, self.ejes)
        self.dibujar()
        self.figura.tight_layout()
        self.canvas.draw_idle()

    def dibujar(self):
        raise NotImplementedError("Cada gráfico tiene que implementar dibujar()")
