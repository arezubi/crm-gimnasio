from PySide6.QtWidgets import QComboBox, QMessageBox
from db.db import baja_profesor
from gui.componentes import FormularioBase


class VentanaBajaProfesor(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Baja de profesor",
                         "El profesor deja de aparecer en los desplegables, pero se conserva su historial.")
        self.cursor = cursor

        self.campo_profesor = QComboBox()
        self.agregar_campo("Profesor", self.campo_profesor)
        self.agregar_boton("Dar de baja", self.dar_de_baja, tipo="peligro")

    def recargar(self):
        self.campo_profesor.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM profesor WHERE activo = 1 ORDER BY nombre")
        for id_profesor, nombre, apellidos in self.cursor.fetchall():
            self.campo_profesor.addItem(f"{nombre} {apellidos}", id_profesor)

    def dar_de_baja(self):
        profesor_id = self.campo_profesor.currentData()
        if profesor_id is None:
            QMessageBox.warning(self, "Aviso", "No hay profesores activos.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar baja",
            f"¿Seguro que quieres dar de baja a {self.campo_profesor.currentText()}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return   # el usuario canceló, no hacer nada

        resultado = baja_profesor(self.cursor, profesor_id)
        if resultado:
            QMessageBox.information(self, "Éxito", "Profesor dado de baja exitosamente.")
            self.campo_profesor.removeItem(self.campo_profesor.currentIndex())
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al profesor.")
