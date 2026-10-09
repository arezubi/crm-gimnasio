from informes.estadisticas import actividad_mas_usada
from gui.estilo_graficos import PaginaGrafico, dibujar_barras_horizontales


class VentanaActividadMasUsada(PaginaGrafico):
    def __init__(self, cursor):
        super().__init__(cursor, "Actividades más populares", "Alumnos activos inscritos en cada actividad.")

    def dibujar(self):
        datos = actividad_mas_usada(self.cursor)
        dibujar_barras_horizontales(self.ejes, datos["nombre"], datos["num_alumnos"])
