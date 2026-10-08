from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QPushButton, QComboBox, QMessageBox
from db.db import marcar_cuota_pagada

class VentanaMarcarCuotaPagada(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Marcar cuota como pagada")

        self.combo_cuota = QComboBox()
        self.cursor.execute("""
            SELECT cuotas.id, alumno.nombre, alumno.apellidos, cuotas.mes_cuota
            FROM cuotas
            JOIN alumno ON cuotas.id_alumno = alumno.id
            WHERE cuotas.pago_realizado = 0
        """)
        for id_cuota, nombre, apellidos, mes_cuota in self.cursor.fetchall():
            self.combo_cuota.addItem(f"{nombre} {apellidos} - {mes_cuota}", id_cuota)

        self.boton_marcar = QPushButton("Marcar como pagada")
        self.boton_marcar.clicked.connect(self.marcar_pagada)

        layout = QFormLayout()
        layout.addRow("Cuota:", self.combo_cuota)
        layout.addRow(self.boton_marcar)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def marcar_pagada(self):
        id_cuota = self.combo_cuota.currentData()

        if id_cuota is None:
            QMessageBox.warning(self, "Aviso", "No hay cuotas pendientes.")
            return

        resultado = marcar_cuota_pagada(self.cursor, id_cuota)   

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Cuota marcada como pagada correctamente.")
            self.combo_cuota.removeItem(self.combo_cuota.currentIndex())
        elif resultado == "ya pagada":
            QMessageBox.warning(self, "Aviso", "Esta cuota ya estaba marcada como pagada.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo marcar la cuota como pagada.")