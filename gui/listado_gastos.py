from PySide6.QtWidgets import QComboBox, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QTableWidget
from db.consultas import listar_gastos
from db.db import borrar_gasto
from gui.componentes import (
    Pagina, abrir_en_dialogo, celda, configurar_tabla, crear_boton, formatear_euros, formatear_fecha,
    plural, poner_botones_fila,
)
from gui.nuevo_gasto import VentanaGenerarGasto
from informes.estadisticas import anios_con_datos


class VentanaListadoGastos(Pagina):
    def __init__(self, cursor):
        super().__init__("Gastos", "Gastos registrados del año seleccionado.")
        self.cursor = cursor

        self.combo_anio = QComboBox()
        self.combo_anio.setMinimumWidth(110)

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")

        fila = QHBoxLayout()
        fila.addWidget(QLabel("Año:"))
        fila.addWidget(self.combo_anio)
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        fila.addWidget(crear_boton("+ Nuevo gasto", self.nuevo_gasto))
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Fecha", "Concepto", "Categoría", "Importe", ""])
        # El concepto se queda con el espacio que sobra; el resto, lo que necesita
        for columna in (0, 2, 3):
            self.tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        self.layout_pagina.addWidget(self.tabla, 1)

        self.combo_anio.currentIndexChanged.connect(self.cargar_gastos)

    def recargar(self):
        anio_anterior = self.combo_anio.currentData()
        self.combo_anio.blockSignals(True)       # que no cargue la tabla con cada addItem
        self.combo_anio.clear()
        for anio in anios_con_datos(self.cursor):
            self.combo_anio.addItem(str(anio), anio)
        self.combo_anio.setCurrentIndex(max(self.combo_anio.findData(anio_anterior), 0))
        self.combo_anio.blockSignals(False)
        self.cargar_gastos()

    def cargar_gastos(self, *args):
        anio = self.combo_anio.currentData()
        filas = listar_gastos(self.cursor, anio)
        total = 0
        self.tabla.setRowCount(0)                # vacía también los botones anteriores
        self.tabla.setRowCount(len(filas))
        for fila_idx, (id_gasto, fecha, concepto, categoria, importe) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(formatear_fecha(fecha)))
            self.tabla.setItem(fila_idx, 1, celda(concepto))
            self.tabla.setItem(fila_idx, 2, celda(categoria))
            self.tabla.setItem(fila_idx, 3, celda(formatear_euros(importe), a_la_derecha=True))
            poner_botones_fila(self.tabla, fila_idx, 4, id_gasto,
                               ("📝", self.editar_gasto, "secundario", "Editar gasto"),
                               ("🗑️", self.eliminar_gasto, "peligro", "Eliminar gasto"))
            total += importe

        if filas:
            self.etiqueta_resumen.setText(
                f"{plural(len(filas), 'gasto', 'gastos')} · {formatear_euros(total)} en {anio}")
        else:
            self.etiqueta_resumen.setText(f"No hay gastos en {anio}.")

    def nuevo_gasto(self):
        if abrir_en_dialogo(self, VentanaGenerarGasto(self.cursor), "Nuevo gasto"):
            self.recargar()

    def editar_gasto(self, id_gasto):
        pagina = VentanaGenerarGasto(self.cursor)
        pagina.cargar_gasto(id_gasto)
        if abrir_en_dialogo(self, pagina, "Editar gasto"):
            self.recargar()

    def eliminar_gasto(self, id_gasto):
        respuesta = QMessageBox.question(
            self, "Eliminar gasto", "¿Seguro que quieres eliminar este gasto?",
            QMessageBox.Yes | QMessageBox.No)
        if respuesta != QMessageBox.Yes:
            return
        if borrar_gasto(self.cursor, id_gasto) is not True:
            QMessageBox.critical(self, "Error", "No se pudo eliminar el gasto.")
        self.recargar()
