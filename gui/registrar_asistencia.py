from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QFormLayout, QPushButton, QComboBox, QDateEdit
from db.db import registrar_asistencia
from PySide6.QtCore import QDate

class VentanaRegistrarAsistencia(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Registrar asistencia")

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

        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDate(QDate.currentDate())
        self.campo_fecha.setCalendarPopup(True)  

        self.boton_registrar = QPushButton("Registrar asistencia")
        self.boton_registrar.clicked.connect(self.guardar_asistencia)
        layout = QFormLayout()
        layout.addRow("Alumno:", self.combo_alumno)
        layout.addRow("Actividad:", self.combo_actividad)
        layout.addRow("Fecha:", self.campo_fecha)
        layout.addRow(self.boton_registrar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def guardar_asistencia(self):
        id_alumno = self.combo_alumno.currentData()
        id_actividad = self.combo_actividad.currentData()
        fecha_texto = self.campo_fecha.date().toString("yyyy-MM-dd")
        resultado = registrar_asistencia(self.cursor, id_alumno, id_actividad, fecha_texto)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Asistencia registrada correctamente.")
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe un registro de asistencia para ese alumno, esa actividad y esa fecha.")
        elif resultado == "no inscrito":
            QMessageBox.warning(self, "Aviso", "Ese alumno no está inscrito en esa actividad.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo registrar la asistencia.")
            