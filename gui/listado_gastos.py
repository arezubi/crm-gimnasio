from datetime import date
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QTableWidget
from db.consultas import listar_gastos
from gui.componentes import Pagina, celda, configurar_tabla, formatear_euros, formatear_fecha, plural


class VentanaListadoGastos(Pagina):
    def __init__(self, cursor):
        super().__init__("Gastos", "Gastos registrados del año seleccionado.")
        self.cursor = cursor

        self.combo_anio = QComboBox()
        anio_actual = date.today().year
        for anio in range(anio_actual, anio_actual - 5, -1):     # este año y los 4 anteriores
            self.combo_anio.addItem(str(anio), anio)
        self.combo_anio.currentIndexChanged.connect(self.recargar)

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")

        fila = QHBoxLayout()
        fila.addWidget(QLabel("Año:"))
        fila.addWidget(self.combo_anio)
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Fecha", "Concepto", "Categoría", "Importe"])
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self, *args):
        anio = self.combo_anio.currentData()
        filas = listar_gastos(self.cursor, anio)
        total = 0
        self.tabla.setRowCount(len(filas))
        for fila_idx, (fecha, concepto, categoria, importe) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(formatear_fecha(fecha)))
            self.tabla.setItem(fila_idx, 1, celda(concepto))
            self.tabla.setItem(fila_idx, 2, celda(categoria))
            self.tabla.setItem(fila_idx, 3, celda(formatear_euros(importe), a_la_derecha=True))
            total += importe
        if filas:
            self.etiqueta_resumen.setText(
            f"{plural(len(filas), 'gasto', 'gastos')} · {formatear_euros(total)} en {anio}")
        else:
            self.etiqueta_resumen.setText(f"No hay gastos en {anio}.")
        
