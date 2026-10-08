import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import alta_profesor
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QCheckBox
from datetime import datetime

class VentanaAltaProfesor(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Alta de profesor")

        self.campo_nombre = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_fecha = QLineEdit()
        self.campo_email = QLineEdit()
        self.campo_telefono = QLineEdit()
        self.check_activo = QCheckBox("Activo")
        self.check_activo.setChecked(True)

        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.guardar_profesor)
        
        layout = QFormLayout()
        layout.addRow("Nombre:", self.campo_nombre)
        layout.addRow("Apellidos:", self.campo_apellidos)
        layout.addRow("Fecha de cumpleaños:", self.campo_fecha)
        layout.addRow("Email:", self.campo_email)
        layout.addRow("Teléfono:", self.campo_telefono)
        layout.addRow("Activo:", self.check_activo)
        layout.addRow(self.boton_guardar)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def guardar_profesor(self):
        
        if(campo_nombre := self.campo_nombre.text()) == "":
            QMessageBox.warning(self, "Error", "El campo nombre no puede estar vacío.")
            return
        if(campo_apellidos := self.campo_apellidos.text()) == "":
            QMessageBox.warning(self, "Error", "El campo apellidos no puede estar vacío.")
            return
        if(campo_fecha := self.campo_fecha.text()) == "":
            QMessageBox.warning(self, "Error", "El campo fecha no puede estar vacío.")
            return
        if(campo_email := self.campo_email.text()) == "":
            QMessageBox.warning(self, "Error", "El campo email no puede estar vacío.")
            return
        if(campo_telefono := self.campo_telefono.text()) == "":
            QMessageBox.warning(self, "Error", "El campo teléfono no puede estar vacío.")
            return

        try:
            fecha_convertida = datetime.strptime(self.campo_fecha.text(), "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Error", "La fecha debe tener el formato DD-MM-AAAA.")
            return
        
        resultado = alta_profesor(
            self.cursor,
            self.campo_nombre.text().strip(),
            self.campo_apellidos.text().strip(),
            fecha_convertida,
            self.campo_email.text().strip(),
            self.campo_telefono.text().strip(),
            self.check_activo.isChecked().strip() 
        )
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Profesor guardado correctamente.")
            self.campo_nombre.clear()
            self.campo_apellidos.clear()
            self.campo_fecha.clear()
            self.campo_email.clear()
            self.campo_telefono.clear()
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe un profesor con este email.")   
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta al profesor.")   
        
