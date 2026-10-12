from PySide6.QtWidgets import QLabel, QTableWidget
from gui.componentes import Pagina, celda, configurar_tabla, formatear_euros, formatear_mes
from db.consultas import listar_cuotas_pendientes

class VentanaCuotasPendientes(Pagina):
    def __init__(self, cursor):
        super().__init__("Cuotas pendientes", "Cuotas generadas que todavía no se han cobrado.")
        self.cursor = cursor

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")
        self.layout_pagina.addWidget(self.etiqueta_resumen)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Alumno", "Mes", "Importe"])
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        filas = listar_cuotas_pendientes(self.cursor)
        self.tabla.setRowCount(len(filas))
        total = 0
        for fila_idx, (_, alumno, mes, importe) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(alumno))
            self.tabla.setItem(fila_idx, 1, celda(formatear_mes(mes)))
            self.tabla.setItem(fila_idx, 2, celda(formatear_euros(importe), a_la_derecha=True))
            total += importe

        if filas:
            self.etiqueta_resumen.setText(f"{len(filas)} cuotas pendientes · {formatear_euros(total)} por cobrar")
        else:
            self.etiqueta_resumen.setText("No hay cuotas pendientes. ¡Todo cobrado!")
