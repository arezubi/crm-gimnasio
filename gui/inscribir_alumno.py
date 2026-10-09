from PySide6.QtWidgets import QComboBox, QMessageBox
from db.db import inscribir_alumno_actividad
from gui.componentes import FormularioBase


class VentanaInscribirAlumno(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Inscripciones", "Apunta a un alumno a una actividad.")
        self.cursor = cursor

        self.combo_alumno = QComboBox()
        self.combo_actividad = QComboBox()
        self.agregar_campo("Alumno", self.combo_alumno)
        self.agregar_campo("Actividad", self.combo_actividad)
        self.agregar_boton("Inscribir", self.inscribir_alumno)

    def recargar(self):
        self.combo_alumno.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1 ORDER BY nombre")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.combo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

        self.combo_actividad.clear()
        self.cursor.execute("SELECT id, nombre FROM actividades ORDER BY nombre")
        for id_actividad, nombre in self.cursor.fetchall():
            self.combo_actividad.addItem(nombre, id_actividad)

    def inscribir_alumno(self):
        id_alumno_seleccionado = self.combo_alumno.currentData()
        id_actividad_seleccionada = self.combo_actividad.currentData()

        if id_alumno_seleccionado is None or id_actividad_seleccionada is None:
            QMessageBox.warning(self, "Aviso", "Necesitas al menos un alumno activo y una actividad.")
            return

        resultado = inscribir_alumno_actividad(self.cursor, id_alumno_seleccionado, id_actividad_seleccionada)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Alumno inscrito en la actividad correctamente.")
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "El alumno ya está inscrito en esta actividad.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo inscribir al alumno en la actividad.")
