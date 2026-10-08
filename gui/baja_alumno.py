from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import baja_alumno
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaBajaAlumno(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Baja de Alumno")

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QFormLayout()
        self.widget.setLayout(self.layout)

        self.campo_alumno = QComboBox()
        self.cursor.execute("SELECT id, nombre FROM alumno WHERE activo = 1")
        alumnos = self.cursor.fetchall()
        for alumno in alumnos:
            self.campo_alumno.addItem(f"{alumno[1]} (ID: {alumno[0]})", alumno[0])
        self.layout.addRow("Alumno:", self.campo_alumno)

        self.baja_button = QPushButton("Dar de Baja")
        self.baja_button.clicked.connect(self.dar_de_baja)
        self.layout.addRow(self.baja_button)

    def dar_de_baja(self):
        alumno_id = self.campo_alumno.currentData()
        if not alumno_id:
            QMessageBox.warning(self, "Error", "Debe seleccionar un alumno.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar baja",
            f"¿Seguro que quieres dar de baja al alumno {self.campo_alumno.currentText()}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return   # el usuario canceló, no hacer nada

        resultado = baja_alumno(self.cursor, alumno_id)
        if resultado:
            QMessageBox.information(self, "Éxito", "Alumno dado de baja exitosamente.")
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al alumno.")