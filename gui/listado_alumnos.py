from datetime import date
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QTableWidget
from gui.componentes import MESES, Pagina, celda, configurar_tabla, formatear_fecha
from db.consultas import listar_alumnos_con_cuotas

COLOR_PAGADA = QColor("#3fb950")
COLOR_PENDIENTE = QColor("#e5484d")
COLOR_SIN_CUOTA = QColor("#9a9a9a")


class VentanaListadoAlumnos(Pagina):
    def __init__(self, cursor):
        super().__init__("Alumnos", "Alumnos activos y estado de su cuota de este mes.")
        self.cursor = cursor

        self.campo_buscar = QLineEdit()
        self.campo_buscar.setPlaceholderText("Buscar por nombre, email o teléfono…")
        self.campo_buscar.setClearButtonEnabled(True)
        self.campo_buscar.setMaximumWidth(360)
        self.campo_buscar.textChanged.connect(self.filtrar)

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")

        fila = QHBoxLayout()
        fila.addWidget(self.campo_buscar)
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        self.columna_cuota = 5
        configurar_tabla(self.tabla, ["Nombre", "Apellidos", "Email", "Teléfono", "Alta", "Cuota del mes"])
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        hoy = date.today()
        mes_actual = hoy.strftime("%Y-%m-01")
        self.tabla.horizontalHeaderItem(self.columna_cuota).setText(
            f"Cuota de {MESES[hoy.month - 1]}")

        filas = listar_alumnos_con_cuotas(self.cursor, mes_actual)

        pagadas = 0
        self.tabla.setRowCount(len(filas))
        for fila_idx, (nombre, apellidos, email, telefono, fecha_alta, pagada) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(nombre))
            self.tabla.setItem(fila_idx, 1, celda(apellidos))
            self.tabla.setItem(fila_idx, 2, celda(email))
            self.tabla.setItem(fila_idx, 3, celda(telefono))
            self.tabla.setItem(fila_idx, 4, celda(formatear_fecha(fecha_alta)))

            if pagada is None:
                estado = celda("—  Sin cuota")
                estado.setForeground(COLOR_SIN_CUOTA)
            elif pagada:
                estado = celda("●  Pagada")
                estado.setForeground(COLOR_PAGADA)
                pagadas += 1
            else:
                estado = celda("●  Pendiente")
                estado.setForeground(COLOR_PENDIENTE)
            self.tabla.setItem(fila_idx, self.columna_cuota, estado)

        self.etiqueta_resumen.setText(f"{len(filas)} alumnos activos · {pagadas} al día este mes")
        self.filtrar(self.campo_buscar.text())

    def filtrar(self, texto):
        """Oculta las filas que no contienen el texto buscado en ninguna columna."""
        texto = texto.strip().lower()
        for fila in range(self.tabla.rowCount()):
            contenido = " ".join(
                self.tabla.item(fila, columna).text().lower()
                for columna in range(self.tabla.columnCount())
            )
            self.tabla.setRowHidden(fila, texto not in contenido)
