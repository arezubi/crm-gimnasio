from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QDoubleSpinBox, QLineEdit, QMessageBox
from db.consultas import obtener_gasto
from gui.componentes import FormularioBase
from logica.gastos import CATEGORIAS_GASTOS, modificar_gasto, registrar_gasto

class VentanaGenerarGasto(FormularioBase):
    """Formulario de gasto. Sirve para crear uno nuevo o, con cargar_gasto(), para editarlo."""

    def __init__(self, cursor):
        super().__init__("Nuevo gasto", "Registra un gasto del gimnasio.")
        self.cursor = cursor
        self.id_gasto = None             # None: gasto nuevo; un id: se está editando ese gasto

        self.campo_fecha = QDateEdit()
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setDate(QDate.currentDate())
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.campo_concepto = QLineEdit()
        self.campo_concepto.setPlaceholderText("Ej. Factura Luz")
        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(CATEGORIAS_GASTOS)
        self.campo_importe = QDoubleSpinBox()
        self.campo_importe.setDecimals(2)
        self.campo_importe.setRange(0, 100000)
        self.campo_importe.setSuffix(" €")
        self.campo_importe.setGroupSeparatorShown(True)    # 1.250,00 €

        self.agregar_campo("Fecha", self.campo_fecha)
        self.agregar_campo("Concepto", self.campo_concepto)
        self.agregar_campo("Categoría", self.combo_categoria)
        self.agregar_campo("Importe", self.campo_importe)
        self.agregar_boton("Guardar gasto", self.guardar_gasto)

    def cargar_gasto(self, id_gasto):
        """Rellena el formulario con un gasto existente para editarlo."""
        datos = obtener_gasto(self.cursor, id_gasto)
        if datos is None:
            return
        self.id_gasto = id_gasto
        fecha, concepto, categoria, importe = datos
        self.etiqueta_titulo.setText("Editar gasto")
        self.etiqueta_subtitulo.setText("Cambia los datos y pulsa Guardar.")
        self.campo_fecha.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
        self.campo_concepto.setText(concepto)
        self.combo_categoria.setCurrentText(categoria)
        self.campo_importe.setValue(importe)

    def guardar_gasto(self):
        valores = self.leer_obligatorios([(self.campo_concepto, "Concepto")])
        if valores is None:
            return
        concepto = valores[0]
        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        categoria = self.combo_categoria.currentText()
        importe = self.campo_importe.value()

        if self.id_gasto is None:
            resultado = registrar_gasto(self.cursor, fecha, concepto, categoria, importe)
        else:
            resultado = modificar_gasto(self.cursor, self.id_gasto, fecha, concepto, categoria, importe)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Gasto guardado correctamente.")
            self.guardado.emit()
            if self.id_gasto is None:
                self.limpiar_campos([self.campo_concepto])
                self.campo_importe.setValue(0)
        elif resultado == "importe no válido":
            QMessageBox.warning(self, "Error", "El gasto debe ser mayor que 0.")
        elif resultado == "no existe":
            QMessageBox.warning(self, "Error", "Ese gasto ya no existe.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar el gasto.")
