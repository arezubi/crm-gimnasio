from datetime import date
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QTableWidget
from db.db import baja_alumno
from gui.alta_alumno import VentanaAltaAlumno
from gui.componentes import MESES, Pagina, abrir_en_dialogo, celda, configurar_tabla, crear_boton, formatear_fecha, poner_botones_fila
from db.consultas import listar_alumnos_con_cuotas
from gui.editar_alumno import VentanaEditarAlumno

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
        fila.addWidget(crear_boton("+ Nuevo alumno", self.nuevo_alumno))
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        self.columna_cuota = 5
        configurar_tabla(self.tabla, ["Nombre", "Apellidos", "Email", "Teléfono", "Alta", "Cuota del mes", ""])
        # Email, teléfono, alta y cuota se ajustan a su contenido; nombre y apellidos reparten el resto
        for columna in range(2, 6):
            self.tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        hoy = date.today()
        mes_actual = hoy.strftime("%Y-%m-01")
        self.tabla.horizontalHeaderItem(self.columna_cuota).setText(
            f"Cuota de {MESES[hoy.month - 1]}")

        filas = listar_alumnos_con_cuotas(self.cursor, mes_actual)

        pagadas = 0
        self.tabla.setRowCount(0)  
        self.tabla.setRowCount(len(filas))
        for fila_idx, (id_alumno, nombre, apellidos, email, telefono, fecha_alta, pagada) in enumerate(filas):
            self.tabla.setItem(fila_idx, 0, celda(nombre))
            self.tabla.setItem(fila_idx, 1, celda(apellidos))
            self.tabla.setItem(fila_idx, 2, celda(email))
            self.tabla.setItem(fila_idx, 3, celda(telefono))
            self.tabla.setItem(fila_idx, 4, celda(formatear_fecha(fecha_alta)))
            poner_botones_fila(self.tabla, fila_idx, 6, id_alumno,
                               ("📝", self.editar_alumno, "secundario", "Editar alumno"),
                               ("🗑️", self.dar_de_baja, "peligro", "Dar de baja"))

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
                for columna in range(self.tabla.columnCount() -1)
            )
            self.tabla.setRowHidden(fila, texto not in contenido)

    def nuevo_alumno(self):
        pagina = VentanaAltaAlumno(self.cursor)
        if abrir_en_dialogo(self, pagina, "Nuevo alumno"):
            self.recargar()

    def editar_alumno(self, id_alumno):
        pagina = VentanaEditarAlumno(self.cursor)
        pagina.cargar_alumno(id_alumno)
        if abrir_en_dialogo(self, pagina, "Editar alumno"):
            self.recargar()

    def dar_de_baja(self, id_alumno):
        respuesta = QMessageBox.question(
            self, "Confirmar baja", "¿Seguro que quieres dar de baja a este alumno?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return

        if baja_alumno(self.cursor, id_alumno):
            self.recargar()
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al alumno.")
