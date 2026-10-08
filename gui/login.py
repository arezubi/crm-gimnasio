from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QMainWindow, QPushButton, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
from gui.ventana_principal import VentanaPrincipal
from PySide6.QtWidgets import QMessageBox
from db.db import verificar_login

class VentanaLogin(QMainWindow):
    def __init__(self,cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Login")
        self.resize(400, 500)

        self.logo = QLabel()
        pixmap = QIcon("assets/logo.svg").pixmap(QSize(150, 150))
        self.logo.setPixmap(pixmap)
        self.logo.setAlignment(Qt.AlignCenter)

        self.campo_email = QLineEdit()
        self.campo_password = QLineEdit()
        self.campo_email.setMinimumWidth(250)
        self.campo_password.setMinimumWidth(250)
        self.campo_password.setEchoMode(QLineEdit.Password)

        self.boton_login = QPushButton("Login")
        self.boton_login.clicked.connect(self.intentar_login)

        layout = QFormLayout()
        layout.addRow(self.logo)
        layout.addRow("Email:", self.campo_email)
        layout.addRow("Password:", self.campo_password)

        contenedor = QWidget()
        layout.addRow(self.boton_login)
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)
        

    def intentar_login(self):
        email = self.campo_email.text().strip()
        password = self.campo_password.text()

        rol = verificar_login(self.cursor, email, password)

        if rol is None:
            QMessageBox.warning(self, "Error de login", "Email o contraseña incorrectos")
            return

        self.ventana_principal = VentanaPrincipal(self.cursor, rol)  
        self.ventana_principal.show()
        self.close()
        