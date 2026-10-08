from PySide6.QtWidgets import QWidget, QGridLayout, QFrame, QLabel, QVBoxLayout
from PySide6.QtCore import Qt
from informes.estadisticas import (
    alumnos_activos,
    numero_pagos_pendientes,
    ingresos_mes_actual,
    alumnos_nuevos_mes_actual,
    nombre_actividad_mas_usada,
)


class PanelDashboard(QWidget):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor

        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.crear_tarjeta("Alumnos activos", alumnos_activos(cursor)), 0, 0)
        layout.addWidget(self.crear_tarjeta("Pagos pendientes", numero_pagos_pendientes(cursor)), 0, 1)
        layout.addWidget(self.crear_tarjeta("Ingresos mes actual", f"{ingresos_mes_actual(cursor)} €"), 1, 0)
        layout.addWidget(self.crear_tarjeta("Alumnos nuevos", alumnos_nuevos_mes_actual(cursor)), 1, 1)
        layout.addWidget(self.crear_tarjeta("Actividad más usada", nombre_actividad_mas_usada(cursor)), 2, 0, 1, 2)

    def crear_tarjeta(self, titulo, valor):
        tarjeta = QFrame()
        tarjeta.setObjectName("tarjeta")

        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setObjectName("titulo_tarjeta")
        etiqueta_titulo.setAlignment(Qt.AlignCenter)

        etiqueta_valor = QLabel(str(valor))
        etiqueta_valor.setObjectName("valor_tarjeta")
        etiqueta_valor.setAlignment(Qt.AlignCenter)

        layout_tarjeta = QVBoxLayout()
        layout_tarjeta.addWidget(etiqueta_titulo)
        layout_tarjeta.addWidget(etiqueta_valor)
        tarjeta.setLayout(layout_tarjeta)

        return tarjeta