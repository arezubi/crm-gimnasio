from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import baja_profesor
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaBajaProfesor(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Baja de Profesor")

        self.widget = QWidget()
        self.setCentralWidget(self.widget)

        self.layout = QFormLayout()
        self.widget.setLayout(self.layout)

        self.campo_profesor = QComboBox()
        self.cursor.execute("SELECT id, nombre FROM profesor WHERE activo = 1")
        profesores = self.cursor.fetchall()
        for profesor in profesores:
            self.campo_profesor.addItem(f"{profesor[1]} (ID: {profesor[0]})", profesor[0])
        self.layout.addRow("Profesor:", self.campo_profesor)

        self.baja_button = QPushButton("Dar de Baja")
        self.baja_button.clicked.connect(self.dar_de_baja)
        self.layout.addRow(self.baja_button)

    def dar_de_baja(self):
        profesor_id = self.campo_profesor.currentData()
        if not profesor_id:
            QMessageBox.warning(self, "Error", "Debe seleccionar un profesor.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar baja",
            f"¿Seguro que quieres dar de baja al profesor {self.campo_profesor.currentText()}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if respuesta != QMessageBox.Yes:
            return   # el usuario canceló, no hacer nada

        resultado = baja_profesor(self.cursor, profesor_id)
        if resultado:
            QMessageBox.information(self, "Éxito", "Profesor dado de baja exitosamente.")
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al profesor.")