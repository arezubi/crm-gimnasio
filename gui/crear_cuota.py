from datetime import date
from PySide6.QtWidgets import QComboBox, QLabel, QMessageBox
from logica.cuotas import crear_cuota_mensual, generar_cuotas_del_mes
from db.consultas import listar_alumnos_activos, listar_tipos_cuota
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
        self.agregar_boton("Generar cuotas de todos", self.generar_todas, tipo="secundario")


    def recargar(self):
        self.combo_alumno.clear()
        for id_alumno, nombre in listar_alumnos_activos(self.cursor):
            self.combo_alumno.addItem(nombre, id_alumno)

        self.combo_cuota.clear()
        self.precios = {}
    
        for id_cuota, nombre, precio in listar_tipos_cuota(self.cursor):
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

    def generar_todas(self):
        mes_cuota = f"{self.combo_año.currentData()}-{self.combo_mes.currentData():02d}-01"
        nombre_mes = f"{self.combo_mes.currentText()} {self.combo_año.currentText()}"
        respuesta = QMessageBox.question(
            self, "Confirmar generación de cuotas",
            f"¿Seguro que quieres generar las cuotas de todos los alumnos activos para el mes {nombre_mes}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            creadas, ya_existentes, sin_tipo = generar_cuotas_del_mes(self.cursor, mes_cuota)
            mensaje = f"Cuotas creadas: {creadas}\nCuotas ya existentes: {ya_existentes}"
            if sin_tipo:
                mensaje += "\n\nSin cuota anterior (créala a mano):\n• " + "\n• ".join(sin_tipo)
            QMessageBox.information(self, "Cuotas generadas", mensaje)
