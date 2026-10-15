from datetime import date

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QTableWidget
from db.consultas import listar_cuotas_del_mes
from logica.cuotas import eliminar_cuota, marcar_cuota_pagada
from gui.componentes import (MESES, Pagina, celda, configurar_tabla,formatear_euros, formatear_fecha, poner_botones_fila)

COLOR_PAGADA = QColor("#3fb950")
COLOR_PENDIENTE = QColor("#e5484d")


class VentanaCuotasPendientes(Pagina):
    def __init__(self, cursor):
        super().__init__("Cuotas del mes", "Cobra o elimina las cuotas de cada mes.")
        self.cursor = cursor

        hoy = date.today()
        self.combo_mes = QComboBox()
        for numero, nombre_mes in enumerate(MESES, start=1):
            self.combo_mes.addItem(nombre_mes.capitalize(), numero)
        self.combo_mes.setCurrentIndex(hoy.month - 1)

        self.combo_año = QComboBox()
        for año in range(hoy.year - 1, hoy.year + 3):
            self.combo_año.addItem(str(año), año)
        self.combo_año.setCurrentIndex(1)   # el año actual

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")

        fila = QHBoxLayout()
        fila.addWidget(QLabel("Mes:"))
        fila.addWidget(self.combo_mes)
        fila.addWidget(self.combo_año)
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Alumno", "Tipo", "Importe", "Estado", ""])
        # Importe y estado ocupan lo que necesitan; alumno y tipo reparten el resto
        for columna in (2, 3):
            self.tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        self.layout_pagina.addWidget(self.tabla, 1)

        # Se conectan al final, cuando la tabla ya existe
        self.combo_mes.currentIndexChanged.connect(self.recargar)
        self.combo_año.currentIndexChanged.connect(self.recargar)

    def recargar(self, *args):
        mes = f"{self.combo_año.currentData()}-{self.combo_mes.currentData():02d}-01"
        filas = listar_cuotas_del_mes(self.cursor, mes)

        self.tabla.setRowCount(0)             # vacía la tabla y también los botones anteriores
        self.tabla.setRowCount(len(filas))
        pagadas = 0
        pendientes = 0
        por_cobrar = 0

        for fila_idx, (id_cuota, alumno, tipo, importe, pagada, fecha_pago) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(alumno))
            self.tabla.setItem(fila_idx, 1, celda(tipo))
            self.tabla.setItem(fila_idx, 2, celda(formatear_euros(importe), a_la_derecha=True))

            if pagada:
                pagadas += 1
                estado = celda(f"● Pagada el {formatear_fecha(fecha_pago)}")
                estado.setForeground(COLOR_PAGADA)
                self.tabla.setItem(fila_idx, 3, estado)
            else:
                pendientes += 1
                por_cobrar += importe
                estado = celda("● Pendiente")
                estado.setForeground(COLOR_PENDIENTE)
                self.tabla.setItem(fila_idx, 3, estado)
                poner_botones_fila(self.tabla, fila_idx, 4, id_cuota,
                                ("Cobrar", self.cobrar, "primario"),
                                ("🗑️", self.eliminar, "peligro", "Eliminar cuota"))


        self.etiqueta_resumen.setText(
            f"{pagadas} pagadas · {pendientes} pendientes · {formatear_euros(por_cobrar)} por cobrar")

    def cobrar(self, id_cuota):
        resultado = marcar_cuota_pagada(self.cursor, id_cuota)
        if resultado is not True:
            QMessageBox.warning(self, "Aviso", "No se pudo cobrar la cuota (puede que ya esté pagada).")
        self.recargar()

    def eliminar(self, id_cuota):
        respuesta = QMessageBox.question(
            self, "Eliminar cuota", "¿Seguro que quieres eliminar esta cuota?",
            QMessageBox.Yes | QMessageBox.No)
        if respuesta != QMessageBox.Yes:
            return

        resultado = eliminar_cuota(self.cursor, id_cuota)
        if resultado == "ya pagada":
            QMessageBox.warning(self, "Aviso", "No se puede eliminar una cuota ya pagada.")
        elif resultado == "no existe":
            QMessageBox.warning(self, "Aviso", "La cuota ya no existe.")
        elif resultado is not True:
            QMessageBox.critical(self, "Error", "No se pudo eliminar la cuota.")
        self.recargar()