from informes.estadisticas import calcular_ingresos_por_anio
from gui.estilo_graficos import PaginaGrafico, dibujar_barras, euros_cortos


class VentanaGraficoIngresosAnual(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Ingresos por año", "Total de cuotas cobradas cada año.")

    def dibujar(self):
        self.ingresos_por_anio = calcular_ingresos_por_anio(self.cursor)
        dibujar_barras(self.ejes, self.ingresos_por_anio.index, self.ingresos_por_anio.values,
                       formato=euros_cortos)
