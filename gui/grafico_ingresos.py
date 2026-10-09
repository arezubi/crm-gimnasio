from informes.estadisticas import calcular_ingresos_por_mes
from gui.componentes import MESES_CORTOS
from gui.estilo_graficos import PaginaGrafico, dibujar_barras, euros_cortos


class VentanaGraficoIngresos(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Ingresos por mes",
                         "Cuotas cobradas de cada mes del año seleccionado.", con_selector_anio=True)

    def dibujar(self):
        anio = self.anio_seleccionado()
        ingresos = calcular_ingresos_por_mes(self.cursor, anio)
        # Siempre los 12 meses, aunque alguno no tenga ingresos
        valores = [ingresos.get(f"{anio}-{mes:02d}-01", 0) for mes in range(1, 13)]
        dibujar_barras(self.ejes, MESES_CORTOS, valores, formato=euros_cortos)
