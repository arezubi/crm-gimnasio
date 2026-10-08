from informes.estadisticas import calcular_ingresos_por_anio
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import QMainWindow

class VentanaGraficoIngresosAnual(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.ingresos_por_anio = calcular_ingresos_por_anio(cursor)
        self.setWindowTitle("Ingresos Anuales")

        self.figura = Figure(figsize=(6, 4))
        self.ejes = self.figura.add_subplot(111)
        self.ejes.bar(self.ingresos_por_anio.index.astype(str), self.ingresos_por_anio.values)
        self.ejes.set_title("Ingresos anuales")
        self.ejes.set_ylabel("€")
        self.ejes.set_xlabel("Año")

        self.canvas = FigureCanvasQTAgg(self.figura)
        self.setCentralWidget(self.canvas)