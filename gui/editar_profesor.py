from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QLineEdit, QMessageBox
from db.consultas import obtener_profesor
from db.db import actualizar_profesor
from gui.componentes import FormularioBase, marcar_error
from logica.validaciones import email_valido


class VentanaEditarProfesor(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Edita profesor", "Cambia los datos y pulsa Guardar.")
        self.cursor = cursor
        self.id_profesor = None


        self.campo_nombre = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.campo_email = QLineEdit()
        self.campo_telefono = QLineEdit()

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Apellidos", self.campo_apellidos)
        self.agregar_campo("Fecha de nacimiento", self.campo_fecha)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Teléfono", self.campo_telefono)
        self.agregar_boton("Guardar profesor", self.guardar_profesor)

    def cargar_profesor(self, id_profesor):
        self.id_profesor = id_profesor
        datos = obtener_profesor(self.cursor, id_profesor)
        if datos is None:
            QMessageBox.warning(self, "Aviso", "El profesor ya no existe.")
            return
        nombre, apellidos, fecha, email, telefono = datos
        self.campo_nombre.setText(nombre)
        self.campo_apellidos.setText(apellidos)
        self.campo_fecha.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
        self.campo_email.setText(email)
        self.campo_telefono.setText(telefono)
        
    def guardar_profesor(self):
        if self.id_profesor is None:
            return

        valores = self.leer_obligatorios([
            (self.campo_nombre, "Nombre"),
            (self.campo_apellidos, "Apellidos"),
            (self.campo_email, "Email"),
            (self.campo_telefono, "Teléfono"),
        ])
        if valores is None:
            return
        nombre, apellidos, email, telefono = valores

        if not email_valido(email):
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Email no válido", "Revisa el email del profesor.")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        resultado = actualizar_profesor(self.cursor, self.id_profesor,
                                        nombre, apellidos, fecha, email, telefono)
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Profesor actualizado correctamente.")
            self.guardado.emit()
        elif resultado == "duplicado":
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Error", "Ya existe otro profesor con este email.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo actualizar al profesor.")