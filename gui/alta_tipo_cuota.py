import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import alta_tipo_cuota
from PySide6.QtWidgets import QMessageBox

class VentanaAltaTipoCuota(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Alta de tipo de cuota")

        self.campo_nombre = QLineEdit()
        self.campo_precio = QLineEdit()

        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.guardar_tipo_cuota)
        
        layout = QFormLayout()
        layout.addRow("Nombre:", self.campo_nombre)
        layout.addRow("Precio:", self.campo_precio)
        layout.addRow(self.boton_guardar)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def guardar_tipo_cuota(self):
        try: 
            if(campo_nombre := self.campo_nombre.text()) == "":
                QMessageBox.warning(self, "Error", "El campo nombre no puede estar vacío.")
                return
            if(campo_precio := self.campo_precio.text()) == "":
                QMessageBox.warning(self, "Error", "El campo precio no puede estar vacío.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
            return
        try:
            precio = int(campo_precio)
        except ValueError:
            QMessageBox.warning(self, "Error", "El campo precio debe ser un número entero.")
            return

        resultado = alta_tipo_cuota(
            self.cursor,
            campo_nombre,
            precio
        )
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Tipo de cuota guardado correctamente.")
            self.campo_nombre.clear()
            self.campo_precio.clear()
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe una cuota con este nombre.")   
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta la cuota.")   
        