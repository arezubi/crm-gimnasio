from PySide6.QtWidgets import QComboBox, QLineEdit, QMessageBox
from db.db import registrar_usuario
from gui.componentes import FormularioBase, marcar_error

LONGITUD_MINIMA_PASSWORD = 6


class VentanaRegistrarUsuario(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Nuevo usuario", "Crea un acceso a la aplicación. Solo los administradores ven esta sección.")
        self.cursor = cursor

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Nombre que verá al entrar")
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("nombre@gimnasio.com")
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.Password)  # Ocultar la contraseña
        self.campo_password.setPlaceholderText(f"Mínimo {LONGITUD_MINIMA_PASSWORD} caracteres")
        self.campo_rol = QComboBox()
        self.campo_rol.addItem("Administrador", "admin")
        self.campo_rol.addItem("Operador", "operador")
        self.campo_profesor = QComboBox()

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Contraseña", self.campo_password)
        self.agregar_campo("Rol", self.campo_rol)
        self.agregar_campo("Profesor asociado", self.campo_profesor)
        self.agregar_boton("Limpiar", self.limpiar, tipo="secundario")
        self.agregar_boton("Guardar usuario", self.guardar_usuario)

    def recargar(self):
        self.campo_profesor.clear()
        self.campo_profesor.addItem("Ninguno (no es profesor)", None)
        self.cursor.execute("SELECT id, nombre, apellidos FROM profesor WHERE activo = 1 ORDER BY nombre")
        for id_profesor, nombre, apellidos in self.cursor.fetchall():
            self.campo_profesor.addItem(f"{nombre} {apellidos}", id_profesor)

    def limpiar(self):
        self.limpiar_campos([self.campo_nombre, self.campo_email, self.campo_password])
        self.campo_rol.setCurrentIndex(0)
        self.campo_profesor.setCurrentIndex(0)

    def guardar_usuario(self):
        valores = self.leer_obligatorios([
            (self.campo_nombre, "Nombre"),
            (self.campo_email, "Email"),
            (self.campo_password, "Contraseña"),
        ])
        if valores is None:
            return
        nombre, email, password = valores

        if "@" not in email:
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Email no válido", "Revisa el email del usuario.")
            return
        if len(password) < LONGITUD_MINIMA_PASSWORD:
            marcar_error(self.campo_password, True)
            QMessageBox.warning(self, "Contraseña demasiado corta",
                                f"La contraseña debe tener al menos {LONGITUD_MINIMA_PASSWORD} caracteres.")
            return

        rol = self.campo_rol.currentData()
        id_profesor = self.campo_profesor.currentData()  # None si no es profesor

        resultado = registrar_usuario(self.cursor, nombre, email, password, rol, id_profesor)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")
            self.limpiar()
        elif resultado == 'duplicado':
            marcar_error(self.campo_email, True)
            QMessageBox.warning(self, "Error", "El correo electrónico ya está registrado.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo registrar el usuario.")
