from PySide6.QtWidgets import QComboBox, QLineEdit, QMessageBox
from db.consultas import datos_usuario, listar_profesores_activos
from gui.componentes import FormularioBase, marcar_error
from logica.usuarios import es_admin_principal, modificar_usuario
from logica.validaciones import LONGITUD_MINIMA_PASSWORD

MENSAJES_ERROR = {
    "email no válido": "Revisa el email del usuario.",
    "duplicado": "Ese email ya es de otro usuario.",
    "contraseña corta": f"La contraseña debe tener al menos {LONGITUD_MINIMA_PASSWORD} caracteres.",
    "propio rol": "No puedes quitarte a ti mismo el rol de administrador.",
    "ultimo admin": "Es el único administrador: tiene que haber al menos uno.",
    "admin principal": "Es la cuenta de administrador principal: siempre tiene que ser administrador.",
    "no existe": "Ese usuario ya no existe.",
}


class VentanaEditarUsuario(FormularioBase):
    """Un administrador cambia los datos de un usuario y, si quiere, le pone una contraseña nueva."""

    def __init__(self, cursor, id_actual):
        super().__init__("Editar usuario", "Cambia los datos y pulsa Guardar.")
        self.cursor = cursor
        self.id_actual = id_actual           # el usuario que ha iniciado sesión
        self.id_usuario = None

        self.campo_nombre = QLineEdit()
        self.campo_email = QLineEdit()
        self.campo_rol = QComboBox()
        self.campo_rol.addItem("Administrador", "admin")
        self.campo_rol.addItem("Operador", "operador")
        self.campo_profesor = QComboBox()
        self.campo_password = QLineEdit()
        self.campo_password.setEchoMode(QLineEdit.Password)
        self.campo_password.setPlaceholderText("Déjala vacía para no cambiarla")

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Email", self.campo_email)
        self.agregar_campo("Rol", self.campo_rol)
        self.agregar_campo("Profesor asociado", self.campo_profesor)
        self.agregar_campo("Contraseña nueva", self.campo_password)
        self.agregar_boton("Guardar cambios", self.guardar_usuario)

    def cargar_usuario(self, id_usuario):
        datos = datos_usuario(self.cursor, id_usuario)
        if datos is None:
            return
        self.id_usuario = id_usuario
        nombre, email, rol, id_profesor, _ = datos
        self.campo_nombre.setText(nombre)
        self.campo_email.setText(email)
        self.campo_rol.setCurrentIndex(self.campo_rol.findData(rol))
        if es_admin_principal(self.cursor, id_usuario):
            self.campo_rol.setEnabled(False)
            self.campo_rol.setToolTip("La cuenta de administrador principal siempre es administrador.")
        self.campo_profesor.clear()
        self.campo_profesor.addItem("Ninguno (no es profesor)", None)
        for id_prof, nombre_prof in listar_profesores_activos(self.cursor):
            self.campo_profesor.addItem(nombre_prof, id_prof)
        self.campo_profesor.setCurrentIndex(max(self.campo_profesor.findData(id_profesor), 0))

    def guardar_usuario(self):
        valores = self.leer_obligatorios([(self.campo_nombre, "Nombre"), (self.campo_email, "Email")])
        if valores is None:
            return
        nombre, email = valores
        resultado = modificar_usuario(
            self.cursor, self.id_usuario, self.id_actual, nombre, email,
            self.campo_rol.currentData(), self.campo_profesor.currentData(), self.campo_password.text())

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente.")
            self.guardado.emit()
            return
        if resultado in ("email no válido", "duplicado"):
            marcar_error(self.campo_email, True)
        elif resultado == "contraseña corta":
            marcar_error(self.campo_password, True)
        QMessageBox.warning(self, "No se puede guardar",
                            MENSAJES_ERROR.get(resultado, "No se pudo actualizar el usuario."))
