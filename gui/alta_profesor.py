from PySide6.QtCore import QDate
from PySide6.QtWidgets import QCheckBox, QDateEdit, QLineEdit, QMessageBox
from db.db import alta_profesor
from gui.componentes import FormularioBase, marcar_error


class VentanaAltaProfesor(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Alta de profesor", "Añade un profesor para poder asignarle actividades.")
        self.cursor = cursor

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Ej. Carlos")
        self.campo_apellidos = QLineEdit()
        self.campo_apellidos.setPlaceholderText("Ej. Ruiz Peña")
        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.campo_fecha.setDate(QDate(1990, 1, 1))
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("nombre@email.com")
        self.campo_telefono = QLineEdit()
        self.campo_telefono.setPlaceholderText("600 000 000")
        self.check_activo = QCheckBox("Activo")
        self.check_activo.setChecked(True)

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Apellidos", self.campo_apellidos)
        self.agregar_campo("Fecha de nacimiento", self.campo_fecha)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Teléfono", self.campo_telefono)
        self.agregar_campo("Estado", self.check_activo)
        self.agregar_boton("Guardar profesor", self.guardar_profesor)

    def guardar_profesor(self):
        valores = self.leer_obligatorios([
            (self.campo_nombre, "Nombre"),
            (self.campo_apellidos, "Apellidos"),
            (self.campo_email, "Email"),
            (self.campo_telefono, "Teléfono"),
        ])
        if valores is None:
            return
        nombre, apellidos, email, telefono = valores

        if "@" not in email:
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Email no válido", "Revisa el email del profesor.")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        resultado = alta_profesor(
            self.cursor,
            nombre,
            apellidos,
            fecha,
            email,
            telefono,
            self.check_activo.isChecked()
        )
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Profesor guardado correctamente.")
            self.limpiar_campos([self.campo_nombre, self.campo_apellidos,
                                 self.campo_email, self.campo_telefono])
            self.campo_fecha.setDate(QDate(1990, 1, 1))
            self.check_activo.setChecked(True)
        elif resultado == 'duplicado':
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Error", "Ya existe un profesor con este email.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta al profesor.")
