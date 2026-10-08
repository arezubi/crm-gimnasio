from informes.estadisticas import alumnos_nuevos_por_mes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QMainWindow

class VentanaAlumnosNuevos(QMainWindow):
    def __init__(self,cursor):
        super().__init__()
        self.alumnos_nuevos = alumnos_nuevos_por_mes(cursor)
        self.setWindowTitle("Alumnos Nuevos")

        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        self.ejes.bar(self.alumnos_nuevos.index.astype(str), self.alumnos_nuevos.values)
        self.ejes.set_title("Alumnos nuevos por mes")
        self.ejes.set_ylabel("Número de alumnos")

        self.canvas = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.canvas)