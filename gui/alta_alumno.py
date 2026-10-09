from PySide6.QtCore import QDate
from PySide6.QtWidgets import QDateEdit, QLineEdit, QMessageBox
from db.db import alta_alumno
from gui.componentes import FormularioBase, marcar_error


class VentanaAltaAlumno(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Alta de alumno", "Registra un nuevo alumno en el gimnasio.")
        self.cursor = cursor

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Ej. Ana")
        self.campo_apellidos = QLineEdit()
        self.campo_apellidos.setPlaceholderText("Ej. García López")
        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.campo_fecha.setDate(QDate(2000, 1, 1))
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("nombre@email.com")
        self.campo_telefono = QLineEdit()
        self.campo_telefono.setPlaceholderText("600 000 000")
        self.campo_contacto_emergencia = QLineEdit()
        self.campo_contacto_emergencia.setPlaceholderText("Nombre y teléfono")

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Apellidos", self.campo_apellidos)
        self.agregar_campo("Fecha de nacimiento", self.campo_fecha)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Teléfono", self.campo_telefono)
        self.agregar_campo("Contacto de emergencia", self.campo_contacto_emergencia)
        self.agregar_boton("Guardar alumno", self.guardar_alumno)

    def guardar_alumno(self):
        valores = self.leer_obligatorios([
            (self.campo_nombre, "Nombre"),
            (self.campo_apellidos, "Apellidos"),
            (self.campo_email, "Email"),
            (self.campo_telefono, "Teléfono"),
            (self.campo_contacto_emergencia, "Contacto de emergencia"),
        ])
        if valores is None:
            return
        nombre, apellidos, email, telefono, contacto_emergencia = valores

        if "@" not in email:
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Email no válido", "Revisa el email del alumno.")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        resultado = alta_alumno(self.cursor, nombre, apellidos, fecha, email, telefono, contacto_emergencia)

        if resultado is True:
            QMessageBox.information(self, "Éxito", f"{nombre} {apellidos} ya es alumno del gimnasio.")
            self.limpiar_campos([self.campo_nombre, self.campo_apellidos, self.campo_email,
                                 self.campo_telefono, self.campo_contacto_emergencia])
            self.campo_fecha.setDate(QDate(2000, 1, 1))
        elif resultado == 'duplicado':
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Error", "Ya existe un alumno con este email.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta al alumno.")
