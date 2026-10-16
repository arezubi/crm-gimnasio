from informes.estadisticas import calcular_ingresos_por_mes
from gui.componentes import MESES_CORTOS
from gui.estilo_graficos import PaginaGrafico, dibujar_barras, dibujar_total, euros_cortos


class VentanaGraficoIngresos(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Ingresos",
                         "Cuotas cobradas de cada mes del año seleccionado y total del año.",
                         con_selector_anio=True, con_total=True)

    def dibujar(self):
        anio = self.anio_seleccionado()
        ingresos = calcular_ingresos_por_mes(self.cursor, anio)
        # Siempre los 12 meses, aunque alguno no tenga ingresos
        valores = [ingresos.get(f"{anio}-{mes:02d}-01", 0) for mes in range(1, 13)]
        dibujar_barras(self.ejes, MESES_CORTOS, valores, formato=euros_cortos)
        dibujar_total(self.ejes_total, f"Total {anio}", sum(valores), formato=euros_cortos)
