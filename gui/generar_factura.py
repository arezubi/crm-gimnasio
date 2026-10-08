from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import generar_facturas
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaGenerarFactura(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Generar factura")

        self.combo_cuota = QComboBox()
        # Cargar los tipos de cuota existentes desde la base de datos
        self.cursor.execute("""
            SELECT cuotas.id, alumno.nombre, alumno.apellidos, cuotas.mes_cuota
            FROM cuotas
            JOIN alumno ON cuotas.id_alumno = alumno.id
            WHERE cuotas.pago_realizado = 1
            AND cuotas.id NOT IN (SELECT id_cuota FROM factura)
        """)
        for id_cuota, nombre, apellidos, mes_cuota in self.cursor.fetchall():
            self.combo_cuota.addItem(f"{nombre} {apellidos} - {mes_cuota}", id_cuota)

        self.boton_generar_factura = QPushButton("Generar factura")
        self.boton_generar_factura.clicked.connect(self.generar_factura)
        layout = QFormLayout()
        layout.addRow("Cuota:", self.combo_cuota)
        layout.addRow(self.boton_generar_factura)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)    

    def generar_factura(self):
        id_cuota_seleccionada = self.combo_cuota.currentData()
        resultado = generar_facturas(self.cursor, id_cuota_seleccionada)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Factura generada correctamente.")
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe una factura para esta cuota.")
        elif resultado == 'no pagada':
            QMessageBox.warning(self, "Error", "La cuota no ha sido pagada. No se puede generar la factura.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo generar la factura.")
