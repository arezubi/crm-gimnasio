from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QVBoxLayout, QWidget
from config import RUTA_LOGO
from db.db import verificar_login
from gui.componentes import crear_boton, marcar_error
from gui.ventana_principal import VentanaPrincipal


class VentanaLogin(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Spartan Team · Iniciar sesión")
        self.setFixedSize(860, 540)

        # --- Mitad izquierda: el logo sobre negro (el mismo negro que el fondo del logo) ---
        panel_marca = QFrame()
        panel_marca.setObjectName("panel_marca")
        layout_marca = QVBoxLayout(panel_marca)
        logo = QLabel()
        logo.setPixmap(QIcon(str(RUTA_LOGO)).pixmap(QSize(220, 330)))
        logo.setAlignment(Qt.AlignCenter)
        subtitulo_marca = QLabel("CRM Gimnasio")
        subtitulo_marca.setObjectName("marca_sub")
        subtitulo_marca.setAlignment(Qt.AlignCenter)
        layout_marca.addStretch()
        layout_marca.addWidget(logo)
        layout_marca.addWidget(subtitulo_marca)
        layout_marca.addStretch()

        # --- Mitad derecha: el formulario ---
        panel_formulario = QWidget()
        layout_formulario = QVBoxLayout(panel_formulario)
        layout_formulario.setContentsMargins(56, 40, 56, 40)
        layout_formulario.setSpacing(8)

        titulo = QLabel("Bienvenido")
        titulo.setObjectName("titulo_pagina")
        subtitulo = QLabel("Inicia sesión para continuar")
        subtitulo.setObjectName("subtitulo_pagina")

        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("tu@email.com")
        self.campo_password = QLineEdit()
        self.campo_password.setPlaceholderText("Contraseña")
        self.campo_password.setEchoMode(QLineEdit.Password)
        # Enter en cualquiera de los dos campos también inicia sesión
        self.campo_email.returnPressed.connect(self.intentar_login)
        self.campo_password.returnPressed.connect(self.intentar_login)

        self.etiqueta_error = QLabel()
        self.etiqueta_error.setObjectName("error")
        self.etiqueta_error.hide()

        layout_formulario.addStretch()
        layout_formulario.addWidget(titulo)
        layout_formulario.addWidget(subtitulo)
        layout_formulario.addSpacing(24)
        layout_formulario.addWidget(self.crear_etiqueta("Email"))
        layout_formulario.addWidget(self.campo_email)
        layout_formulario.addSpacing(8)
        layout_formulario.addWidget(self.crear_etiqueta("Contraseña"))
        layout_formulario.addWidget(self.campo_password)
        layout_formulario.addSpacing(4)
        layout_formulario.addWidget(self.etiqueta_error)
        layout_formulario.addSpacing(16)
        layout_formulario.addWidget(crear_boton("Entrar", self.intentar_login))
        layout_formulario.addStretch()

        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(panel_marca, 1)
        layout.addWidget(panel_formulario, 1)
        self.setCentralWidget(contenedor)

    def crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("etiqueta_campo")
        return etiqueta

    def intentar_login(self):
        email = self.campo_email.text().strip()
        password = self.campo_password.text()

        rol = verificar_login(self.cursor, email, password)

        if rol is None:
            self.etiqueta_error.setText("Email o contraseña incorrectos.")
            self.etiqueta_error.show()
            marcar_error(self.campo_email, True)
            marcar_error(self.campo_password, True)
            self.campo_password.clear()
            self.campo_password.setFocus()
            return

        self.cursor.execute("SELECT nombre FROM usuarios WHERE email = ?", (email,))
        nombre_usuario = self.cursor.fetchone()[0]

        self.ventana_principal = VentanaPrincipal(self.cursor, rol, nombre_usuario)
        self.ventana_principal.show()
        self.close()
