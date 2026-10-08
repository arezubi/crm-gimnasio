from informes.estadisticas import alumnos_nuevos_por_anio
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QMainWindow

class VentanaGraficoAlumnosNuevosPorAnio(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.alumnos_por_anio = alumnos_nuevos_por_anio(cursor)
        self.setWindowTitle("Alumnos nuevos por año")

        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        self.ejes.bar(self.alumnos_por_anio.index.astype(str), self.alumnos_por_anio)
        self.ejes.set_title("Alumnos nuevos por año")
        self.ejes.set_ylabel("Nº alumnos")
        self.ejes.set_xlabel("Año")

        self.canvas = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.canvas)