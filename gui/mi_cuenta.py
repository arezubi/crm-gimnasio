from PySide6.QtWidgets import QLineEdit, QMessageBox
from db.consultas import datos_usuario
from gui.componentes import FormularioBase, marcar_error
from logica.usuarios import cambiar_mi_cuenta
from logica.validaciones import LONGITUD_MINIMA_PASSWORD


class VentanaMiCuenta(FormularioBase):
    """El usuario que ha iniciado sesión cambia su nombre y su contraseña."""

    def __init__(self, cursor, id_usuario):
        super().__init__("Mi cuenta", "")
        self.cursor = cursor
        self.id_usuario = id_usuario
        self.nombre_guardado = None          # el nombre nuevo, para que la ventana principal lo muestre

        self.campo_nombre = QLineEdit()
        self.campo_actual = QLineEdit()
        self.campo_nueva = QLineEdit()
        self.campo_repetir = QLineEdit()
        for campo in (self.campo_actual, self.campo_nueva, self.campo_repetir):
            campo.setEchoMode(QLineEdit.Password)
        self.campo_actual.setPlaceholderText("Solo si vas a cambiar la contraseña")
        self.campo_nueva.setPlaceholderText(f"Mínimo {LONGITUD_MINIMA_PASSWORD} caracteres")

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Contraseña actual", self.campo_actual)
        self.agregar_campo("Contraseña nueva", self.campo_nueva)
        self.agregar_campo("Repite la contraseña nueva", self.campo_repetir)
        self.agregar_boton("Guardar cambios", self.guardar)

        datos = datos_usuario(cursor, id_usuario)
        if datos is not None:
            nombre, email = datos[0], datos[1]
            self.campo_nombre.setText(nombre)
            self.etiqueta_subtitulo.setText(f"Has iniciado sesión como {email}.")

    def guardar(self):
        valores = self.leer_obligatorios([(self.campo_nombre, "Nombre")])
        if valores is None:
            return
        nombre = valores[0]
        nueva = self.campo_nueva.text()
        if nueva != self.campo_repetir.text():
            marcar_error(self.campo_repetir, True)
            QMessageBox.warning(self, "No coinciden", "La contraseña nueva y la repetida no son iguales.")
            return

        resultado = cambiar_mi_cuenta(self.cursor, self.id_usuario, nombre, self.campo_actual.text(), nueva)
        if resultado is True:
            self.nombre_guardado = nombre
            QMessageBox.information(self, "Éxito", "Tus datos se han guardado.")
            self.guardado.emit()
        elif resultado == "contraseña incorrecta":
            marcar_error(self.campo_actual, True)
            QMessageBox.warning(self, "Contraseña incorrecta", "La contraseña actual no es correcta.")
        elif resultado == "contraseña corta":
            marcar_error(self.campo_nueva, True)
            QMessageBox.warning(self, "Contraseña demasiado corta",
                                f"La contraseña debe tener al menos {LONGITUD_MINIMA_PASSWORD} caracteres.")
        else:
            QMessageBox.warning(self, "Error", "No se pudieron guardar los cambios.")
