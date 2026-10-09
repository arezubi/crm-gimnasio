from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QMessageBox
from db.db import registrar_asistencia
from gui.componentes import FormularioBase


class VentanaRegistrarAsistencia(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Asistencia", "Registra que un alumno ha asistido a una clase.")
        self.cursor = cursor

        self.combo_alumno = QComboBox()
        self.combo_actividad = QComboBox()
        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setDate(QDate.currentDate())
        self.campo_fecha.setMaximumDate(QDate.currentDate())   # no se puede asistir en el futuro

        self.agregar_campo("Alumno", self.combo_alumno)
        self.agregar_campo("Actividad", self.combo_actividad)
        self.agregar_campo("Fecha", self.campo_fecha)
        self.agregar_boton("Registrar asistencia", self.guardar_asistencia)

    def recargar(self):
        self.combo_alumno.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1 ORDER BY nombre")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.combo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

        self.combo_actividad.clear()
        self.cursor.execute("SELECT id, nombre FROM actividades ORDER BY nombre")
        for id_actividad, nombre in self.cursor.fetchall():
            self.combo_actividad.addItem(nombre, id_actividad)

        self.campo_fecha.setMaximumDate(QDate.currentDate())

    def guardar_asistencia(self):
        id_alumno = self.combo_alumno.currentData()
        id_actividad = self.combo_actividad.currentData()

        if id_alumno is None or id_actividad is None:
            QMessageBox.warning(self, "Aviso", "Necesitas al menos un alumno activo y una actividad.")
            return

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
