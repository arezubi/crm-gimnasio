from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QMessageBox, QTableWidget
from db.consultas import listar_usuarios
from gui.componentes import (
    Pagina, abrir_en_dialogo, celda, configurar_tabla, crear_boton, plural, poner_botones_fila,
)
from gui.editar_usuario import VentanaEditarUsuario
from gui.registrar_usuario import VentanaRegistrarUsuario
from logica.usuarios import eliminar_usuario

NOMBRES_ROL = {"admin": "Administrador", "operador": "Operador"}


class VentanaListadoUsuarios(Pagina):
    def __init__(self, cursor, id_actual):
        super().__init__("Usuarios", "Personas con acceso a la aplicación. Solo los administradores ven esta sección.")
        self.cursor = cursor
        self.id_actual = id_actual           # el usuario que ha iniciado sesión

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")
        fila = QHBoxLayout()
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        fila.addWidget(crear_boton("+ Nuevo usuario", self.nuevo_usuario))
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Nombre", "Email", "Rol", "Profesor asociado", ""])
        for columna in (1, 2):
            self.tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        usuarios = listar_usuarios(self.cursor)
        self.tabla.setRowCount(0)
        self.tabla.setRowCount(len(usuarios))
        for fila, (id_usuario, nombre, email, rol, profesor) in enumerate(usuarios):
            if id_usuario == self.id_actual:
                nombre += "  (tú)"
            self.tabla.setItem(fila, 0, celda(nombre))
            self.tabla.setItem(fila, 1, celda(email))
            self.tabla.setItem(fila, 2, celda(NOMBRES_ROL.get(rol, rol)))
            self.tabla.setItem(fila, 3, celda(profesor or "—"))
            poner_botones_fila(self.tabla, fila, 4, id_usuario,
                               ("📝", self.editar_usuario, "secundario", "Editar usuario"),
                               ("🗑️", self.borrar_usuario, "peligro", "Eliminar usuario"))
        self.etiqueta_resumen.setText(plural(len(usuarios), "usuario", "usuarios"))

    def nuevo_usuario(self):
        pagina = VentanaRegistrarUsuario(self.cursor)
        pagina.recargar()                    # rellena el desplegable de profesores
        if abrir_en_dialogo(self, pagina, "Nuevo usuario"):
            self.recargar()

    def editar_usuario(self, id_usuario):
        pagina = VentanaEditarUsuario(self.cursor, self.id_actual)
        pagina.cargar_usuario(id_usuario)
        if abrir_en_dialogo(self, pagina, "Editar usuario"):
            self.recargar()

    def borrar_usuario(self, id_usuario):
        respuesta = QMessageBox.question(
            self, "Eliminar usuario",
            "¿Seguro que quieres eliminar este usuario?\n\nYa no podrá entrar en la aplicación.",
            QMessageBox.Yes | QMessageBox.No)
        if respuesta != QMessageBox.Yes:
            return
        resultado = eliminar_usuario(self.cursor, id_usuario, self.id_actual)
        if resultado == "propio":
            QMessageBox.warning(self, "No se puede eliminar", "No puedes eliminar tu propio usuario.")
        elif resultado == "ultimo admin":
            QMessageBox.warning(self, "No se puede eliminar",
                                "Es el único administrador: tiene que haber al menos uno.")
        elif resultado is not True:
            QMessageBox.critical(self, "Error", "No se pudo eliminar el usuario.")
        self.recargar()
