from PySide6.QtWidgets import QMainWindow, QWidget, QFormLayout, QPushButton, QMessageBox, QComboBox
from db.db import crear_cuota_mensual
from datetime import date

class VentanaCrearCuota(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Crear cuota mensual")

        self.combo_alumno = QComboBox()
        # Cargar los alumnos existentes desde la base de datos
        self.cursor.execute("SELECT id, nombre, apellidos FROM alumno WHERE activo = 1")
        for id_alumno, nombre, apellidos in self.cursor.fetchall():
            self.combo_alumno.addItem(f"{nombre} {apellidos}", id_alumno)

        self.combo_cuota = QComboBox()
        # Cargar los tipos de cuota existentes desde la base de datos
        self.cursor.execute("SELECT id, nombre FROM tipo_cuota")
        for id_cuota, nombre in self.cursor.fetchall():
            self.combo_cuota.addItem(nombre, id_cuota)

        self.combo_mes = QComboBox()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        for numero, nombre_mes in enumerate(meses, start=1):
            self.combo_mes.addItem(nombre_mes, numero)

        self.combo_año = QComboBox()
        año_actual = date.today().year
        for año in range(año_actual - 1, año_actual + 3):
            self.combo_año.addItem(str(año), año)

        self.boton_crear_cuota = QPushButton("Crear cuota")
        self.boton_crear_cuota.clicked.connect(self.crear_cuota)
        
        layout = QFormLayout()
        layout.addRow("Alumno:", self.combo_alumno)
        layout.addRow("Tipo de cuota:", self.combo_cuota)
        layout.addRow("Mes de la cuota:", self.combo_mes)
        layout.addRow("Año de la cuota:", self.combo_año)
        layout.addRow(self.boton_crear_cuota)

        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

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