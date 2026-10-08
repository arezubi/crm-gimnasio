from PySide6.QtWidgets import QMainWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from informes.estadisticas import actividad_mas_usada

class VentanaActividadMasUsada(QMainWindow):
    def __init__(self,cursor):
        super().__init__()
        self.actividad_mas_usada = actividad_mas_usada(cursor)
        self.setWindowTitle("Actividad Más Usada")

        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        self.ejes.pie(self.actividad_mas_usada["num_alumnos"], labels=self.actividad_mas_usada["nombre"])
        self.ejes.set_title("Actividad más usada")

        self.canvas = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.canvas)
