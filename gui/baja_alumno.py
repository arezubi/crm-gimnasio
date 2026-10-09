from PySide6.QtWidgets import QComboBox, QMessageBox
from db.db import baja_alumno
from gui.componentes import FormularioBase


class VentanaBajaAlumno(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Baja de alumno",
                         "El alumno deja de aparecer en listados y desplegables, pero se conserva su historial.")
        self.cursor = cursor

        self.campo_alumno = QComboBox()
        self.agregar_campo("Alumno", self.campo_alumno)
        self.agregar_boton("Dar de baja", self.dar_de_baja, tipo="peligro")

    def recargar(self):
        self.campo_alumno.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1 ORDER BY nombre")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.campo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

    def dar_de_baja(self):
        alumno_id = self.campo_alumno.currentData()
        if alumno_id is None:
            QMessageBox.warning(self, "Aviso", "No hay alumnos activos.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar baja",
            f"¿Seguro que quieres dar de baja a {self.campo_alumno.currentText()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return   # el usuario canceló, no hacer nada

        resultado = baja_alumno(self.cursor, alumno_id)
        if resultado:
            QMessageBox.information(self, "Éxito", "Alumno dado de baja exitosamente.")
            self.campo_alumno.removeItem(self.campo_alumno.currentIndex())
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al alumno.")
