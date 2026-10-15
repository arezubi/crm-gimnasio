from PySide6.QtCore import QDate
from PySide6.QtWidgets import QComboBox, QDateEdit, QDoubleSpinBox, QLineEdit, QMessageBox
from gui.componentes import FormularioBase
from logica.gastos import CATEGORIAS_GASTOS, registrar_gasto

class VentanaGenerarGasto(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Registrar Gastos", "Registrar nuevos gastos.")
        self.cursor = cursor

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
    
    def guardar_gasto(self):
        valores = self.leer_obligatorios([(self.campo_concepto, "Concepto")])
        if valores is None:
            return
        concepto = valores[0]
        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")

        resultado = registrar_gasto(self.cursor, fecha, concepto, self.combo_categoria.currentText(), self.campo_importe.value())
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Gasto guardado correctamente.")
            self.limpiar_campos([self.campo_concepto])
            self.campo_importe.setValue(0)
        elif resultado == 'importe no válido':
            QMessageBox.warning(self, "Error", "El gasto debe ser mayor que 0.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo dar de alta el gasto.")
    