from PySide6.QtWidgets import QComboBox, QLineEdit, QMessageBox
from db.db import alta_actividad
from gui.componentes import FormularioBase


class VentanaAltaActividad(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Nueva actividad", "Crea una actividad y asígnale un profesor.")
        self.cursor = cursor

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Ej. Boxeo")
        self.combo_profesor = QComboBox()

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Profesor", self.combo_profesor)
        self.agregar_boton("Guardar actividad", self.guardar_actividad)

    def recargar(self):
        self.combo_profesor.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM profesor WHERE activo = 1 ORDER BY nombre")
        for id_profesor, nombre, apellidos in self.cursor.fetchall():
            self.combo_profesor.addItem(f"{nombre} {apellidos}", id_profesor)

    def guardar_actividad(self):
        valores = self.leer_obligatorios([(self.campo_nombre, "Nombre")])
        if valores is None:
            return
        campo_nombre = valores[0]

        id_profesor = self.combo_profesor.currentData()
        if id_profesor is None:
            QMessageBox.warning(self, "Aviso", "Primero da de alta un profesor activo.")
            return

        resultado = alta_actividad(self.cursor, campo_nombre, id_profesor)
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Actividad guardada correctamente.")
            self.limpiar_campos([self.campo_nombre])
            self.combo_profesor.setCurrentIndex(0)
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe una actividad con este nombre.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta la actividad.")
