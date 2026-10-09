from PySide6.QtWidgets import QLineEdit, QMessageBox, QSpinBox
from db.db import alta_tipo_cuota
from gui.componentes import FormularioBase


class VentanaAltaTipoCuota(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Tipos de cuota", "Define las tarifas que luego asignarás a cada alumno.")
        self.cursor = cursor

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("Ej. Adulto 2 actividades")
        # Con un QSpinBox el usuario solo puede escribir números: no hace falta validar.
        self.campo_precio = QSpinBox()
        self.campo_precio.setRange(1, 1000)
        self.campo_precio.setValue(40)
        self.campo_precio.setSuffix(" €")

        self.agregar_campo("Nombre", self.campo_nombre)
        self.agregar_campo("Precio mensual", self.campo_precio)
        self.agregar_boton("Guardar tipo de cuota", self.guardar_tipo_cuota)

    def guardar_tipo_cuota(self):
        valores = self.leer_obligatorios([(self.campo_nombre, "Nombre")])
        if valores is None:
            return
        nombre = valores[0]

        resultado = alta_tipo_cuota(self.cursor, nombre, self.campo_precio.value())
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Tipo de cuota guardado correctamente.")
            self.limpiar_campos([self.campo_nombre])
            self.campo_precio.setValue(40)
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe una cuota con este nombre.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta la cuota.")
