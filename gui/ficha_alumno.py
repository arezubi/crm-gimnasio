from datetime import date
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QMessageBox, QTableWidget,
    QVBoxLayout,
)
from db.consultas import (
    actividades_de_alumno, asistencias_de_alumno, cuotas_de_alumno, datos_ficha_alumno,
    listar_actividades,
)
from db.db import desinscribir_alumno, inscribir_alumno_actividad
from gui.componentes import (
    Pagina, celda, configurar_tabla, crear_boton, formatear_euros, formatear_fecha, formatear_mes,
    plural, poner_botones_fila,
)

COLOR_PAGADA = QColor("#3fb950")
COLOR_PENDIENTE = QColor("#e5484d")


def crear_panel(titulo):
    """Tarjeta con un título; devuelve la tarjeta, su layout y la etiqueta de resumen de la derecha."""
    tarjeta = QFrame()
    tarjeta.setObjectName("tarjeta")
    layout = QVBoxLayout(tarjeta)
    layout.setContentsMargins(20, 16, 20, 16)
    cabecera = QHBoxLayout()
    etiqueta = QLabel(titulo)
    etiqueta.setObjectName("titulo_seccion")
    resumen = QLabel()
    resumen.setObjectName("resumen")
    cabecera.addWidget(etiqueta)
    cabecera.addStretch()
    cabecera.addWidget(resumen)
    layout.addLayout(cabecera)
    return tarjeta, layout, resumen


class VentanaFichaAlumno(Pagina):
    """Todo sobre un alumno: sus datos, actividades (inscribir y desinscribir), cuotas y asistencias."""

    def __init__(self, cursor, id_alumno):
        super().__init__("Ficha del alumno")
        self.cursor = cursor
        self.id_alumno = id_alumno
        self.setMinimumSize(1120, 700)

        self.etiqueta_datos = QLabel()
        self.etiqueta_datos.setObjectName("ayuda")
        self.layout_pagina.addWidget(self.etiqueta_datos)

        # --- Actividades: las suyas con 🗑️ y, debajo, un desplegable para apuntarle a otra ---
        tarjeta_actividades, layout_actividades, self.resumen_actividades = crear_panel("Actividades")
        self.tabla_actividades = QTableWidget()
        configurar_tabla(self.tabla_actividades, ["Actividad", ""])
        layout_actividades.addWidget(self.tabla_actividades, 1)
        self.combo_actividad = QComboBox()
        fila_inscribir = QHBoxLayout()
        fila_inscribir.addWidget(self.combo_actividad, 1)
        fila_inscribir.addWidget(crear_boton("Inscribir", self.inscribir, tipo="secundario"))
        layout_actividades.addLayout(fila_inscribir)

        # --- Asistencias ---
        tarjeta_asistencias, layout_asistencias, self.resumen_asistencias = crear_panel("Asistencias")
        self.tabla_asistencias = QTableWidget()
        configurar_tabla(self.tabla_asistencias, ["Fecha", "Actividad"])
        layout_asistencias.addWidget(self.tabla_asistencias, 1)

        # --- Cuotas ---
        tarjeta_cuotas, layout_cuotas, self.resumen_cuotas = crear_panel("Cuotas")
        self.tabla_cuotas = QTableWidget()
        configurar_tabla(self.tabla_cuotas, ["Mes", "Tipo", "Importe", "Estado"])
        for columna in (0, 2, 3):       # el tipo se queda con el espacio que sobra
            self.tabla_cuotas.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        layout_cuotas.addWidget(self.tabla_cuotas, 1)

        # Actividades y asistencias a la izquierda, una encima de otra; cuotas a la derecha
        cuadricula = QGridLayout()
        cuadricula.setSpacing(16)
        cuadricula.addWidget(tarjeta_actividades, 0, 0)
        cuadricula.addWidget(tarjeta_asistencias, 1, 0)
        cuadricula.addWidget(tarjeta_cuotas, 0, 1, 2, 1)       # ocupa las dos filas
        cuadricula.setColumnStretch(0, 4)
        cuadricula.setColumnStretch(1, 5)     # las cuotas tienen más columnas
        self.layout_pagina.addLayout(cuadricula, 1)

        self.recargar()

    def recargar(self):
        datos = datos_ficha_alumno(self.cursor, self.id_alumno)
        if datos is None:
            return
        nombre, apellidos, nacimiento, email, telefono, emergencia, fecha_alta = datos
        self.etiqueta_titulo.setText(f"{nombre} {apellidos}")
        self.etiqueta_subtitulo.setText(f"Alumno desde el {formatear_fecha(fecha_alta)} · {email} · {telefono}")
        self.etiqueta_datos.setText(
            f"Fecha de nacimiento: {formatear_fecha(nacimiento)}   ·   Contacto de emergencia: {emergencia}")

        self.cargar_actividades()
        self.cargar_asistencias()
        self.cargar_cuotas()

    def cargar_actividades(self):
        actividades = actividades_de_alumno(self.cursor, self.id_alumno)
        self.tabla_actividades.setRowCount(0)
        self.tabla_actividades.setRowCount(len(actividades))
        for fila, (id_actividad, nombre) in enumerate(actividades):
            self.tabla_actividades.setItem(fila, 0, celda(nombre))
            poner_botones_fila(self.tabla_actividades, fila, 1, id_actividad,
                               ("🗑️", self.desinscribir, "peligro", "Quitar de esta actividad"))
        self.resumen_actividades.setText(plural(len(actividades), "actividad", "actividades"))

        # En el desplegable, solo las actividades en las que todavía no está
        inscritas = {id_actividad for id_actividad, _ in actividades}
        self.combo_actividad.clear()
        for id_actividad, nombre in listar_actividades(self.cursor):
            if id_actividad not in inscritas:
                self.combo_actividad.addItem(nombre, id_actividad)

    def cargar_asistencias(self):
        asistencias = asistencias_de_alumno(self.cursor, self.id_alumno)
        este_mes = date.today().strftime("%Y-%m")
        del_mes = sum(1 for fecha, _ in asistencias if fecha.startswith(este_mes))
        self.tabla_asistencias.setRowCount(len(asistencias))
        for fila, (fecha, actividad) in enumerate(asistencias):
            self.tabla_asistencias.setItem(fila, 0, celda(formatear_fecha(fecha)))
            self.tabla_asistencias.setItem(fila, 1, celda(actividad))
        self.resumen_asistencias.setText(f"{del_mes} este mes · {len(asistencias)} en total")

    def cargar_cuotas(self):
        cuotas = cuotas_de_alumno(self.cursor, self.id_alumno)
        pendientes = 0
        self.tabla_cuotas.setRowCount(len(cuotas))
        for fila, (mes, tipo, importe, pagada, fecha_pago) in enumerate(cuotas):
            self.tabla_cuotas.setItem(fila, 0, celda(formatear_mes(mes)))
            self.tabla_cuotas.setItem(fila, 1, celda(tipo))
            self.tabla_cuotas.setItem(fila, 2, celda(formatear_euros(importe), a_la_derecha=True))
            if pagada:
                estado = celda(f"● Pagada el {formatear_fecha(fecha_pago)}")
                estado.setForeground(COLOR_PAGADA)
            else:
                estado = celda("● Pendiente")
                estado.setForeground(COLOR_PENDIENTE)
                pendientes += 1
            self.tabla_cuotas.setItem(fila, 3, estado)
        if pendientes:
            self.resumen_cuotas.setText(plural(pendientes, "pendiente", "pendientes"))
        else:
            self.resumen_cuotas.setText("Todo pagado" if cuotas else "Sin cuotas")

    def inscribir(self):
        id_actividad = self.combo_actividad.currentData()
        if id_actividad is None:
            QMessageBox.information(self, "Inscribir", "Ya está inscrito en todas las actividades.")
            return
        if inscribir_alumno_actividad(self.cursor, self.id_alumno, id_actividad) is not True:
            QMessageBox.warning(self, "Error", "No se pudo inscribir al alumno.")
        self.cargar_actividades()

    def desinscribir(self, id_actividad):
        respuesta = QMessageBox.question(
            self, "Quitar de la actividad",
            "¿Quitar al alumno de esta actividad?\n\nSus asistencias anteriores se conservan.",
            QMessageBox.Yes | QMessageBox.No)
        if respuesta != QMessageBox.Yes:
            return
        if desinscribir_alumno(self.cursor, self.id_alumno, id_actividad) is not True:
            QMessageBox.warning(self, "Error", "No se pudo quitar al alumno de la actividad.")
        self.cargar_actividades()
