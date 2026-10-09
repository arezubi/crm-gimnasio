from informes.estadisticas import alumnos_nuevos_por_mes
from gui.componentes import MESES_CORTOS
from gui.estilo_graficos import PaginaGrafico, dibujar_barras


class VentanaAlumnosNuevos(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Altas por mes",
                         "Alumnos nuevos de cada mes del año seleccionado.", con_selector_anio=True)

    def dibujar(self):
        anio = self.anio_seleccionado()
        altas = alumnos_nuevos_por_mes(self.cursor, anio)
        por_mes = {str(periodo): total for periodo, total in altas.items()}   # {'2026-08': 3, ...}
        valores = [por_mes.get(f"{anio}-{mes:02d}", 0) for mes in range(1, 13)]
        dibujar_barras(self.ejes, MESES_CORTOS, valores)
