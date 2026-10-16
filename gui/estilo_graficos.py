"""Tema oscuro común para todos los gráficos de matplotlib y página base de gráficos."""
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout

from gui.componentes import Pagina, formatear_numero
from informes.estadisticas import anios_con_datos

# Mismos colores que resources/estilo.qss
COLOR_FONDO = "#1f1f1f"
COLOR_TEXTO = "#f2f2f2"
COLOR_SECUNDARIO = "#9a9a9a"
COLOR_REJILLA = "#2c2c2c"
COLOR_ACENTO = "#ff6a00"
COLOR_TOTAL = "#ffa45c"          # el total del año, en un naranja más claro que los meses


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


def dibujar_barras(ejes, etiquetas, valores, formato=None):
    """Barras verticales naranjas con el valor encima de cada una."""
    etiquetas = [str(e) for e in etiquetas]
    valores = [float(v) for v in valores]
    if not any(valores):
        sin_datos(ejes)
        return
    formato = formato or numero_corto
    barras = ejes.bar(etiquetas, valores, color=COLOR_ACENTO, width=0.6)
    ejes.bar_label(barras, labels=[formato(v) if v else "" for v in valores],
                   color=COLOR_TEXTO, padding=4, fontsize=9)
    ejes.margins(y=0.15)  # deja hueco para el texto de la barra más alta
    ejes.yaxis.set_major_formatter(FORMATO_EJE)
    if son_enteros(valores):
        ejes.yaxis.set_major_locator(MaxNLocator(integer=True))   # nada de "2.5 alumnos"


def dibujar_barras_horizontales(ejes, etiquetas, valores, formato=None):
    """Barras horizontales, la mayor arriba. Se leen mejor que una tarta."""
    etiquetas = [str(e) for e in etiquetas]
    valores = [float(v) for v in valores]
    if not any(valores):
        sin_datos(ejes)
        return
    formato = formato or numero_corto
    barras = ejes.barh(etiquetas, valores, color=COLOR_ACENTO, height=0.6)
    ejes.invert_yaxis()
    ejes.yaxis.grid(False)
    ejes.xaxis.grid(True, color=COLOR_REJILLA, linewidth=0.8)
    ejes.tick_params(axis="y", labelsize=11, labelcolor=COLOR_TEXTO)
    ejes.bar_label(barras, labels=[formato(v) for v in valores],
                   color=COLOR_TEXTO, padding=6, fontsize=10)
    ejes.margins(x=0.12)
    ejes.xaxis.set_major_formatter(FORMATO_EJE)
    if son_enteros(valores):
        ejes.xaxis.set_major_locator(MaxNLocator(integer=True))


def son_enteros(valores):
    return all(float(v).is_integer() for v in valores)


def numero_corto(valor):
    """Sin decimales si es entero: 12000 -> '12.000'   2.5 -> '2,50'."""
    return formatear_numero(valor, 0 if float(valor).is_integer() else 2)


def euros_cortos(valor):
    return f"{numero_corto(valor)} €"


# Números del eje de valores en formato español: 12.000 en vez de 12000
FORMATO_EJE = FuncFormatter(lambda valor, _: numero_corto(valor))


def dibujar_total(ejes, etiqueta, valor, formato=None):
    """Una sola barra con el total. Tiene su propia escala: con la de los meses,
    el total aplastaría las barras de cada mes."""
    formato = formato or numero_corto
    barra = ejes.bar([etiqueta], [valor], color=COLOR_TOTAL, width=0.6)
    ejes.bar_label(barra, labels=[formato(valor)], color=COLOR_TEXTO, padding=4,
                   fontsize=10, fontweight="bold")
    ejes.margins(y=0.15)
    ejes.set_yticks([])                  # el valor ya está encima de la barra
    ejes.yaxis.grid(False)


class PaginaGrafico(Pagina):
    """Página con un gráfico dentro de una tarjeta y, opcionalmente, un selector de año.
    Las clases hijas solo tienen que implementar dibujar()."""

    def __init__(self, cursor, titulo, subtitulo="", con_selector_anio=False, con_total=False):
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
        self.ejes_total = None
        if con_total:
            # Dos gráficos en la misma figura: los meses (ancho) y el total del año (estrecho)
            self.ejes, self.ejes_total = self.figura.subplots(
                1, 2, gridspec_kw={"width_ratios": [12, 1.6]})
        else:
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
        if self.ejes_total is not None:
            self.ejes_total.clear()
            aplicar_estilo(self.figura, self.ejes_total)
        self.dibujar()
        self.figura.tight_layout()
        self.canvas.draw_idle()

    def dibujar(self):
        raise NotImplementedError("Cada gráfico tiene que implementar dibujar()")
