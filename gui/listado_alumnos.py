from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem

class VentanaListadoAlumnos(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.resize(700, 500)
        self.setWindowTitle("Listado de Alumnos")

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Apellidos", "Email", "Teléfono"])

        self.cursor.execute("SELECT nombre, apellidos, email, telefono FROM alumno WHERE activo = 1")
        filas = self.cursor.fetchall()
        self.tabla.setRowCount(len(filas))
        for fila_idx, fila in enumerate(filas):
            for columna_idx, valor in enumerate(fila):
                self.tabla.setItem(fila_idx, columna_idx, QTableWidgetItem(str(valor)))

        self.setCentralWidget(self.tabla)