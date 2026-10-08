import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import alta_actividad
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaAltaActividad(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Alta de actividad")

        self.combo_profesor = QComboBox()
        # Cargar los profesores existentes desde la base de datos
        self.cursor.execute("SELECT id, nombre, apellidos FROM profesor WHERE activo = 1")
        for id_profesor, nombre, apellidos in self.cursor.fetchall():
            self.combo_profesor.addItem(f"{nombre} {apellidos}", id_profesor)

        self.campo_nombre = QLineEdit()
        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.guardar_actividad)
        
        layout = QFormLayout()
        layout.addRow("Nombre:", self.campo_nombre)
        layout.addRow("Profesor:", self.combo_profesor)
        layout.addRow(self.boton_guardar)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def guardar_actividad(self):
        try: 
            if(campo_nombre := self.campo_nombre.text()) == "":
                QMessageBox.warning(self, "Error", "El campo nombre no puede estar vacío.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
            return
        id_profesor_seleccionado = self.combo_profesor.currentData()
        
        resultado = alta_actividad(
            self.cursor,
            campo_nombre,
            self.combo_profesor.currentData()
        )
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Actividad guardada correctamente.")
            self.campo_nombre.clear()
            self.combo_profesor.setCurrentIndex(0)
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe un alumno con este email.")   
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta al alumno.")   
