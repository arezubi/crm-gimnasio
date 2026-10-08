from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import inscribir_alumno_actividad
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaInscribirAlumno(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Inscribir alumno en actividad")

        self.combo_alumno = QComboBox()
        # Cargar los alumnos existentes desde la base de datos
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.combo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

        self.combo_actividad = QComboBox()
        # Cargar las actividades existentes desde la base de datos
        self.cursor.execute("SELECT id, nombre FROM actividades")
        for id_actividad, nombre in self.cursor.fetchall():
            self.combo_actividad.addItem(nombre, id_actividad)

        self.boton_inscribir = QPushButton("Inscribir")
        self.boton_inscribir.clicked.connect(self.inscribir_alumno)
        
        layout = QFormLayout()
        layout.addRow("Alumno:", self.combo_alumno)
        layout.addRow("Actividad:", self.combo_actividad)
        layout.addRow(self.boton_inscribir)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def inscribir_alumno(self):
        id_alumno_seleccionado = self.combo_alumno.currentData()
        id_actividad_seleccionada = self.combo_actividad.currentData()

        resultado = inscribir_alumno_actividad(self.cursor, id_alumno_seleccionado, id_actividad_seleccionada)

        # aquí tienes que llamar a la función de inscripción en la base de datos
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Alumno inscrito en la actividad correctamente.")   # ventana de confirmación
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "El alumno ya está inscrito en esta actividad.")   # ventana de error
        else:
            QMessageBox.warning(self, "Error", "No se pudo inscribir al alumno en la actividad.")   # ventana de error