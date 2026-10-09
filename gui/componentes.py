"""Piezas reutilizables de la interfaz: páginas, formularios, tablas y formatos."""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView, QFormLayout, QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTableWidgetItem, QVBoxLayout, QWidget,
)

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MESES_CORTOS = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


# ---------- Formatos ----------

def formatear_euros(valor):
    """45 -> '45,00 €'   1234.5 -> '1.234,50 €'"""
    texto = f"{float(valor):,.2f}"                      # '1,234.50'
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{texto} €"


def plural(cantidad, singular, en_plural):
    """plural(1, 'alumno', 'alumnos') -> '1 alumno'   plural(3, ...) -> '3 alumnos'"""
    return f"{cantidad} {singular if cantidad == 1 else en_plural}"


def formatear_mes(fecha_iso):
    """'2026-08-01' o '2026-08' -> 'Ago 2026'"""
    anio, mes = fecha_iso[:4], int(fecha_iso[5:7])
    return f"{MESES_CORTOS[mes - 1]} {anio}"


def formatear_fecha(fecha_iso):
    """'2026-10-08' -> '08/10/2026'"""
    if not fecha_iso:
        return ""
    anio, mes, dia = fecha_iso[:10].split("-")
    return f"{dia}/{mes}/{anio}"


def fecha_larga(dia):
    """date(2026, 10, 8) -> 'Jueves, 8 de octubre de 2026'"""
    texto = f"{DIAS_SEMANA[dia.weekday()]}, {dia.day} de {MESES[dia.month - 1]} de {dia.year}"
    return texto.capitalize()


# ---------- Botones y estilos ----------

def crear_boton(texto, accion, tipo="primario"):
    """tipo: 'primario' (naranja), 'secundario' (gris) o 'peligro' (rojo). Ver estilo.qss."""
    boton = QPushButton(texto)
    if tipo != "primario":
        boton.setObjectName(tipo)
    boton.setCursor(Qt.PointingHandCursor)
    boton.clicked.connect(accion)
    return boton


def abrir_archivo(ruta):
    """Abre un archivo (por ejemplo un PDF) con el programa predeterminado del sistema."""
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta)))


def refrescar_estilo(widget):
    """Qt no vuelve a aplicar el QSS solo al cambiar una propiedad; hay que forzarlo."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)


def marcar_error(campo, hay_error):
    """Pone el borde del campo en rojo (ver QLineEdit[error="true"] en estilo.qss)."""
    campo.setProperty("error", hay_error)
    refrescar_estilo(campo)


# ---------- Páginas ----------

class Pagina(QWidget):
    """Pantalla con título y subtítulo. Todas las pantallas de la app heredan de aquí."""

    def __init__(self, titulo, subtitulo=""):
        super().__init__()
        self.layout_pagina = QVBoxLayout(self)
        self.layout_pagina.setContentsMargins(32, 24, 32, 24)
        self.layout_pagina.setSpacing(16)

        self.etiqueta_titulo = QLabel(titulo)
        self.etiqueta_titulo.setObjectName("titulo_pagina")
        self.etiqueta_subtitulo = QLabel(subtitulo)
        self.etiqueta_subtitulo.setObjectName("subtitulo_pagina")

        cabecera = QVBoxLayout()
        cabecera.setSpacing(2)
        cabecera.addWidget(self.etiqueta_titulo)
        cabecera.addWidget(self.etiqueta_subtitulo)
        self.layout_pagina.addLayout(cabecera)

    def recargar(self):
        """Vuelve a leer los datos de la base de datos.
        La ventana principal la llama cada vez que se muestra la página."""
        pass


class FormularioBase(Pagina):
    """Página con una tarjeta que contiene un formulario y una fila de botones a la derecha."""

    def __init__(self, titulo, subtitulo=""):
        super().__init__(titulo, subtitulo)

        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        tarjeta.setMaximumWidth(560)

        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(24, 24, 24, 24)
        layout_tarjeta.setSpacing(20)

        self.formulario = QFormLayout()
        self.formulario.setRowWrapPolicy(QFormLayout.WrapAllRows)   # etiqueta encima del campo
        self.formulario.setVerticalSpacing(14)
        layout_tarjeta.addLayout(self.formulario)

        self.botonera = QHBoxLayout()
        self.botonera.addStretch()
        layout_tarjeta.addLayout(self.botonera)

        self.layout_pagina.addWidget(tarjeta)
        self.layout_pagina.addStretch()

    def agregar_campo(self, texto, widget):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("etiqueta_campo")
        self.formulario.addRow(etiqueta, widget)
        if isinstance(widget, QLineEdit):
            # en cuanto el usuario escribe, quitamos el borde rojo
            widget.textEdited.connect(lambda: marcar_error(widget, False))

    def agregar_boton(self, texto, accion, tipo="primario"):
        boton = crear_boton(texto, accion, tipo)
        self.botonera.addWidget(boton)
        return boton

    def leer_obligatorios(self, campos):
        """campos: lista de (QLineEdit, 'Nombre visible').
        Devuelve la lista de textos sin espacios sobrantes, o None si falta alguno."""
        valores = []
        vacios = []
        for campo, nombre in campos:
            texto = campo.text().strip()
            marcar_error(campo, texto == "")
            if texto == "":
                vacios.append(nombre)
            valores.append(texto)

        if vacios:
            QMessageBox.warning(self, "Faltan datos",
                                "Rellena estos campos:\n• " + "\n• ".join(vacios))
            return None
        return valores

    def limpiar_campos(self, campos):
        for campo in campos:
            campo.clear()
            marcar_error(campo, False)


# ---------- Tablas ----------

def configurar_tabla(tabla, cabeceras):
    tabla.setColumnCount(len(cabeceras))
    tabla.setHorizontalHeaderLabels(cabeceras)
    tabla.verticalHeader().hide()
    tabla.verticalHeader().setDefaultSectionSize(40)
    tabla.setAlternatingRowColors(True)
    tabla.setShowGrid(False)
    tabla.setWordWrap(False)            # si no cabe, se corta con "…" en vez de partir la línea
    tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
    tabla.setSelectionMode(QAbstractItemView.SingleSelection)
    tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
    tabla.setFocusPolicy(Qt.NoFocus)
    cabecera = tabla.horizontalHeader()
    cabecera.setSectionResizeMode(QHeaderView.Stretch)
    cabecera.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    cabecera.setHighlightSections(False)


def celda(texto, a_la_derecha=False):
    item = QTableWidgetItem(str(texto))
    if a_la_derecha:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return item
