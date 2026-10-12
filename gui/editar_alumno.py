from PySide6.QtWidgets import QComboBox, QDateEdit, QLineEdit, QMessageBox
from PySide6.QtCore import QDate
from db.consultas import listar_alumnos_activos, obtener_alumno
from db.db import actualizar_alumno
from gui import alta_alumno
from gui.componentes import FormularioBase, marcar_error
from logica.validaciones import email_valido


class VentanaEditarAlumno(FormularioBase):

    def __init__(self, cursor):
        super().__init__("Edita alumno", "Elige un alumno, cambia sus datos y guarda.")
        self.cursor = cursor
        

        self.combo_alumno = QComboBox()
        self.campo_nombre = QLineEdit()
        self.campo_apellidos = QLineEdit()
        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.campo_email = QLineEdit()
        self.campo_telefono = QLineEdit()
        self.campo_contacto_emergencia = QLineEdit()

        self.agregar_campo("Alumno", self.combo_alumno)
        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Apellidos", self.campo_apellidos)
        self.agregar_campo("Fecha de nacimiento", self.campo_fecha)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Teléfono", self.campo_telefono)
        self.agregar_campo("Contacto de emergencia", self.campo_contacto_emergencia)
        self.agregar_boton("Guardar cambios", self.guardar_alumno)
        self.combo_alumno.currentIndexChanged.connect(self.cargar_datos)
    def recargar(self):
        seleccionado = self.combo_alumno.currentData()
        self.combo_alumno.clear()
        for id_alumno, nombre in listar_alumnos_activos(self.cursor):
            self.combo_alumno.addItem(nombre, id_alumno)
        self.combo_alumno.setCurrentIndex(max(self.combo_alumno.findData(seleccionado), 0))

    def cargar_datos(self):
        id_alumno = self.combo_alumno.currentData()
        if id_alumno is None:
            return 
        datos = obtener_alumno(self.cursor, id_alumno)
        if datos is None:
            return
        nombre, apellidos, fecha_nacimiento, email, telefono, contacto_emergencia = datos
        self.campo_nombre.setText(nombre)
        self.campo_apellidos.setText(apellidos)
        self.campo_fecha.setDate(QDate.fromString(fecha_nacimiento, "yyyy-MM-dd"))
        self.campo_email.setText(email)
        self.campo_telefono.setText(telefono)
        self.campo_contacto_emergencia.setText(contacto_emergencia)

    def guardar_alumno(self):
        id_alumno = self.combo_alumno.currentData()
        if id_alumno is None:
            QMessageBox.warning(self, "Aviso", "No hay alumnos activos.")
            return  
        
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

        if not email_valido(email):
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Email no válido", "Revisa el email del alumno.")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        resultado = actualizar_alumno(self.cursor, id_alumno, nombre, apellidos, fecha, email, telefono, contacto_emergencia)

        if resultado is True:
            QMessageBox.information(self, "Éxito", f"{nombre} {apellidos} se ha editado correctamente.")
            self.recargar()
        elif resultado == 'duplicado':
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Error", "Ya existe un alumno con este email.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo editar al alumno.")
