from datetime import date
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QTableWidget, QVBoxLayout
from gui.componentes import (
    Pagina, celda, configurar_tabla, fecha_larga, formatear_euros, formatear_mes,
)
from gui.estilo_graficos import aplicar_estilo, dibujar_barras, dibujar_barras_horizontales, euros_cortos
from informes.estadisticas import (
    actividad_mas_usada,
    alumnos_activos,
    asistencias_del_mes,
    ingresos_por_tipo_cuota,
    ingresos_por_tipo_cuota,
    numero_pagos_pendientes,
    ingresos_mes_actual,
    alumnos_nuevos_mes_actual,
    nombre_actividad_mas_usada,
    ingresos_ultimos_meses,
    cuotas_pendientes_antiguas,
)


class PanelDashboard(Pagina):
    def __init__(self, cursor, nombre_usuario=None):
        titulo = f"Hola, {nombre_usuario}" if nombre_usuario else "Hola"
        super().__init__(titulo)
        self.cursor = cursor

        # --- Fila de tarjetas con las cifras clave ---
        fila_tarjetas = QHBoxLayout()
        fila_tarjetas.setSpacing(16)
        self.valor_activos = self.crear_tarjeta(fila_tarjetas, "Alumnos activos")
        self.valor_nuevos = self.crear_tarjeta(fila_tarjetas, "Altas este mes")
        self.valor_ingresos = self.crear_tarjeta(fila_tarjetas, "Ingresos del mes")
        self.valor_pendientes = self.crear_tarjeta(fila_tarjetas, "Cuotas pendientes")
        self.valor_asistencias = self.crear_tarjeta(fila_tarjetas, "Asistencias este mes")
        self.layout_pagina.addLayout(fila_tarjetas)

        # --- Gráfico de los últimos meses ---
        tarjeta_grafico, layout_grafico = self.crear_panel("Ingresos de los últimos 6 meses")
        self.figura = Figure(figsize=(6, 3))
        self.ejes = self.figura.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figura)
        layout_grafico.addWidget(self.canvas, 1)       # el 1 hace que ocupe todo el hueco

        # --- Gráfico de Actividades más populares ---
        tarjeta_actividades, layout_actividades = self.crear_panel("Actividades más populares")
        self.figura_actividades = Figure(figsize=(6, 3))
        self.ejes_actividades = self.figura_actividades.add_subplot(111)
        self.canvas_actividades = FigureCanvasQTAgg(self.figura_actividades)
        layout_actividades.addWidget(self.canvas_actividades, 1)

        # --- Tabla con las cuotas sin cobrar más antiguas ---
        tarjeta_tabla, layout_tabla = self.crear_panel("Cuotas pendientes más antiguas")
        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Alumno", "Mes", "Importe"])
        self.tabla.setObjectName("tabla_panel")
        # Mes e importe solo ocupan lo que necesitan; el nombre se queda el resto
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout_tabla.addWidget(self.tabla, 1)

        # --- Tabla ingresos por tipo de cuota ---
        tarjeta_ingresos, layout_ingresos = self.crear_panel("Ingresos por tipo de cuota")
        self.tabla_ingresos = QTableWidget()
        configurar_tabla(self.tabla_ingresos, ["Tipo", "Cuotas", "Importe"])
        self.tabla_ingresos.setObjectName("tabla_panel")
        self.tabla_ingresos.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla_ingresos.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout_ingresos.addWidget(self.tabla_ingresos, 1)

        # --- Cuadrícula 2x2 con los cuatro paneles ---
        cuadricula = QGridLayout()
        cuadricula.setSpacing(16)
        cuadricula.addWidget(tarjeta_grafico, 0, 0)        # fila 0, columna 0
        cuadricula.addWidget(tarjeta_ingresos, 0, 1)
        cuadricula.addWidget(tarjeta_actividades, 1, 0)
        cuadricula.addWidget(tarjeta_tabla, 1, 1)
        cuadricula.setColumnStretch(0, 3)                  # la columna de los gráficos, más ancha
        cuadricula.setColumnStretch(1, 2)
        self.layout_pagina.addLayout(cuadricula, 1)

    def crear_tarjeta(self, layout, titulo):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta_kpi")
        layout_tarjeta = QVBoxLayout(tarjeta)
        layout_tarjeta.setContentsMargins(20, 16, 20, 16)
        layout_tarjeta.setSpacing(2)

        etiqueta_valor = QLabel("—")
        etiqueta_valor.setObjectName("valor_tarjeta")
        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setObjectName("titulo_tarjeta")

        layout_tarjeta.addWidget(etiqueta_valor)
        layout_tarjeta.addWidget(etiqueta_titulo)
        layout.addWidget(tarjeta, 1)
        return etiqueta_valor          # devolvemos la etiqueta para poder actualizarla en recargar()

    def crear_panel(self, titulo):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")
        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(20, 16, 20, 16)
        etiqueta = QLabel(titulo)
        etiqueta.setObjectName("titulo_seccion")
        layout.addWidget(etiqueta)
        return tarjeta, layout

    def recargar(self):
        self.etiqueta_subtitulo.setText(fecha_larga(date.today()))

        self.valor_activos.setText(str(alumnos_activos(self.cursor)))
        self.valor_nuevos.setText(str(alumnos_nuevos_mes_actual(self.cursor)))
        self.valor_ingresos.setText(formatear_euros(ingresos_mes_actual(self.cursor)))
        self.valor_pendientes.setText(str(numero_pagos_pendientes(self.cursor)))
        today = date.today()
        asistencias = asistencias_del_mes(self.cursor, today.year, today.month)
        self.valor_asistencias.setText(str(len(asistencias)))

        meses, importes = ingresos_ultimos_meses(self.cursor)
        self.ejes.clear()
        aplicar_estilo(self.figura, self.ejes)
        dibujar_barras(self.ejes, [formatear_mes(m) for m in meses], importes, formato=euros_cortos)
        self.figura.tight_layout()
        self.canvas.draw_idle()

        filas = cuotas_pendientes_antiguas(self.cursor)
        self.tabla.setRowCount(len(filas))
        for fila_idx, (alumno, mes, importe) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(alumno))
            self.tabla.setItem(fila_idx, 1, celda(formatear_mes(mes)))
            self.tabla.setItem(fila_idx, 2, celda(formatear_euros(importe), a_la_derecha=True))

        # Ingresos del mes por tipo de cuota
        mes_actual = date.today().strftime("%Y-%m-01")
        filas = ingresos_por_tipo_cuota(self.cursor, mes_actual)
        self.tabla_ingresos.setRowCount(len(filas))
        for fila_idx, (tipo, num_cuotas, importe) in enumerate(filas):
            self.tabla_ingresos.setItem(fila_idx, 0, celda(tipo))
            self.tabla_ingresos.setItem(fila_idx, 1, celda(num_cuotas, a_la_derecha=True))
            self.tabla_ingresos.setItem(fila_idx, 2, celda(formatear_euros(importe), a_la_derecha=True))

        # Actividades más populares
        datos = actividad_mas_usada(self.cursor)
        self.ejes_actividades.clear()
        aplicar_estilo(self.figura_actividades, self.ejes_actividades)
        dibujar_barras_horizontales(self.ejes_actividades, datos["nombre"], datos["num_alumnos"])
        self.figura_actividades.tight_layout()
        self.canvas_actividades.draw_idle()
