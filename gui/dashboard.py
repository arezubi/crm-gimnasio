from datetime import date
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QFrame, QHBoxLayout, QHeaderView, QLabel, QTableWidget, QVBoxLayout
from gui.componentes import (
    Pagina, celda, configurar_tabla, fecha_larga, formatear_euros, formatear_mes,
)
from gui.estilo_graficos import aplicar_estilo, dibujar_barras, euros_cortos
from informes.estadisticas import (
    alumnos_activos,
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
        self.valor_actividad = self.crear_tarjeta(fila_tarjetas, "Actividad más popular")
        self.layout_pagina.addLayout(fila_tarjetas)

        # --- Gráfico de los últimos meses ---
        tarjeta_grafico, layout_grafico = self.crear_panel("Ingresos de los últimos 6 meses")
        self.figura = Figure(figsize=(6, 3))
        self.ejes = self.figura.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figura)
        layout_grafico.addWidget(self.canvas, 1)       # el 1 hace que ocupe todo el hueco

        # --- Tabla con las cuotas sin cobrar más antiguas ---
        tarjeta_tabla, layout_tabla = self.crear_panel("Cuotas pendientes más antiguas")
        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Alumno", "Mes", "Importe"])
        self.tabla.setObjectName("tabla_panel")
        # Mes e importe solo ocupan lo que necesitan; el nombre se queda el resto
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout_tabla.addWidget(self.tabla, 1)

        fila_inferior = QHBoxLayout()
        fila_inferior.setSpacing(16)
        fila_inferior.addWidget(tarjeta_grafico, 3)
        fila_inferior.addWidget(tarjeta_tabla, 2)
        self.layout_pagina.addLayout(fila_inferior, 1)

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
        self.valor_actividad.setText(nombre_actividad_mas_usada(self.cursor))

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
