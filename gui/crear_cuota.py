from datetime import date
from PySide6.QtWidgets import QComboBox, QLabel, QMessageBox
from db.db import crear_cuota_mensual
from gui.componentes import MESES, FormularioBase, formatear_euros


class VentanaCrearCuota(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Nueva cuota", "Genera la cuota mensual de un alumno.")
        self.cursor = cursor
        self.precios = {}   # id_tipo_cuota -> precio, para mostrar el importe

        self.combo_alumno = QComboBox()
        self.combo_cuota = QComboBox()
        self.combo_cuota.currentIndexChanged.connect(self.actualizar_importe)
        self.etiqueta_importe = QLabel()
        self.etiqueta_importe.setObjectName("ayuda")

        hoy = date.today()
        self.combo_mes = QComboBox()
        for numero, nombre_mes in enumerate(MESES, start=1):
            self.combo_mes.addItem(nombre_mes.capitalize(), numero)
        self.combo_mes.setCurrentIndex(hoy.month - 1)

        self.combo_año = QComboBox()
        for año in range(hoy.year - 1, hoy.year + 3):
            self.combo_año.addItem(str(año), año)
        self.combo_año.setCurrentIndex(1)   # el año actual

        self.agregar_campo("Alumno", self.combo_alumno)
        self.agregar_campo("Tipo de cuota", self.combo_cuota)
        self.formulario.addRow(self.etiqueta_importe)
        self.agregar_campo("Mes", self.combo_mes)
        self.agregar_campo("Año", self.combo_año)
        self.agregar_boton("Crear cuota", self.crear_cuota)

    def recargar(self):
        self.combo_alumno.clear()
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1 ORDER BY nombre")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.combo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

        self.combo_cuota.clear()
        self.precios = {}
        self.cursor.execute("SELECT id, nombre, precio FROM tipo_cuota ORDER BY nombre")
        for id_cuota, nombre, precio in self.cursor.fetchall():
            self.precios[id_cuota] = precio
            self.combo_cuota.addItem(nombre, id_cuota)
        self.actualizar_importe()

    def actualizar_importe(self):
        precio = self.precios.get(self.combo_cuota.currentData())
        self.etiqueta_importe.setText(f"Importe: {formatear_euros(precio)}" if precio is not None else "")

    def crear_cuota(self):
        mes_cuota = f"{self.combo_año.currentData()}-{self.combo_mes.currentData():02d}-01"
        id_alumno = self.combo_alumno.currentData()
        tipo_cuota = self.combo_cuota.currentData()

        if id_alumno is None or tipo_cuota is None:
            QMessageBox.warning(self, "Aviso", "Necesitas al menos un alumno activo y un tipo de cuota.")
            return

        resultado = crear_cuota_mensual(self.cursor, id_alumno, tipo_cuota, mes_cuota)
        if resultado is True:
            QMessageBox.information(self, "Éxito", "Cuota creada exitosamente.")
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ese alumno ya tiene una cuota para ese mes.")
        else:
            QMessageBox.warning(self, "Error", "Error al crear la cuota.")
