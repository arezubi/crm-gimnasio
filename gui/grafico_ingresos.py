from informes.estadisticas import calcular_ingresos_por_mes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QMainWindow

class VentanaGraficoIngresos(QMainWindow):
    def __init__(self,cursor):
        super().__init__()
        self.ingresos_por_mes = calcular_ingresos_por_mes(cursor)
        self.setWindowTitle("Ingresos Mensuales")

        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        self.ejes.bar(self.ingresos_por_mes.index, self.ingresos_por_mes.values)
        self.ejes.set_title("Ingresos mensuales")
        self.ejes.set_ylabel("€")

        self.canvas = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.canvas)