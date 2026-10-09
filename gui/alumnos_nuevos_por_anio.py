from informes.estadisticas import alumnos_nuevos_por_anio
from gui.estilo_graficos import PaginaGrafico, dibujar_barras


class VentanaGraficoAlumnosNuevosPorAnio(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Altas por año", "Alumnos nuevos de cada año.")

    def dibujar(self):
        self.alumnos_por_anio = alumnos_nuevos_por_anio(self.cursor)
        dibujar_barras(self.ejes, self.alumnos_por_anio.index.astype(str), self.alumnos_por_anio.values)
