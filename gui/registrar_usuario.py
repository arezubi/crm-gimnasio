from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QLineEdit, QPushButton
from db.db import registrar_usuario
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QComboBox

class VentanaRegistrarUsuario(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Registrar usuario")

        self.campo_nombre = QLineEdit()
        self.campo_email = QLineEdit()
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.Password)  # Ocultar la contraseña
        self.campo_rol = QComboBox()
        self.campo_rol.addItem("Administrador", "admin")
        self.campo_rol.addItem("Operador", "operador")

        self.campo_profesor = QComboBox()
        self.campo_profesor.addItem("Ninguno (no es profesor)", None)
        self.cursor.execute("SELECT id, nombre, apellidos FROM profesor WHERE activo = 1")
        for id_profesor, nombre, apellidos in self.cursor.fetchall():
            self.campo_profesor.addItem(f"{nombre} {apellidos}", id_profesor)
        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.guardar_usuario)
        self.boton_cancelar = QPushButton("Cancelar")
        self.boton_cancelar.clicked.connect(self.close)
        layout = QFormLayout()
        layout.addRow("Nombre:", self.campo_nombre)
        layout.addRow("Email:", self.campo_email)
        layout.addRow("Contraseña:", self.campo_password)
        layout.addRow("Rol:", self.campo_rol)
        layout.addRow("Profesor:", self.campo_profesor)
        layout.addRow(self.boton_guardar, self.boton_cancelar)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def guardar_usuario(self):
        try:
            if(campo_nombre := self.campo_nombre.text()) == "":
                QMessageBox.warning(self, "Error", "El campo nombre no puede estar vacío.")
                return
            if(campo_email := self.campo_email.text()) == "":
                QMessageBox.warning(self, "Error", "El campo email no puede estar vacío.")
                return
            if(campo_password := self.campo_password.text()) == "":
                QMessageBox.warning(self, "Error", "El campo contraseña no puede estar vacío.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Ocurrió un error: {e}")
            return
        
        nombre = self.campo_nombre.text()
        email = self.campo_email.text()
        password = self.campo_password.text()
        rol = self.campo_rol.currentData()
        id_profesor = self.campo_profesor.currentData()  # Obtiene el ID del profesor seleccionado, o None si no es profesor

        resultado = registrar_usuario(self.cursor, nombre, email, password, rol, id_profesor)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")   # ventana de confirmación
            # limpiar los campos después de guardar
            self.campo_nombre.clear()
            self.campo_email.clear()
            self.campo_password.clear()
            self.campo_rol.setCurrentIndex(0)
            self.campo_profesor.setCurrentIndex(0)
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "El correo electrónico ya está registrado.")   # ventana de error
        else:
            QMessageBox.warning(self, "Error", "No se pudo registrar el usuario.")   # ventana de error
