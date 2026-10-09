import calendar
from collections import defaultdict
from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QSizePolicy, QTableWidget, QVBoxLayout,
)
from gui.componentes import (
    MESES, Pagina, celda, configurar_tabla, crear_boton, formatear_fecha, plural, refrescar_estilo,
)
from informes.estadisticas import asistencia_por_alumno, asistencias_del_mes

# Un color por actividad (se asigna según su id). Texto oscuro encima para que se lea bien.
COLORES_ACTIVIDAD = ["#1fb6e8", "#ff8a7a", "#3fb950", "#c39bff", "#f2c94c", "#ff9f43"]
DIAS_CORTOS = ["L", "M", "X", "J", "V", "S", "D"]
COLOR_SIN_ASISTENCIA = QColor("#9a9a9a")


def color_actividad(id_actividad):
    return COLORES_ACTIVIDAD[id_actividad % len(COLORES_ACTIVIDAD)]


class CeldaDia(QFrame):
    """Un día del calendario: el número y debajo una etiqueta por cada actividad."""
    MAXIMO_ETIQUETAS = 3

    def __init__(self):
        super().__init__()
        self.setObjectName("celda_dia")
        self.setMinimumHeight(86)
        self.setMinimumWidth(0)

        # Si la celda se oculta (días de otro mes), que siga ocupando su hueco en la cuadrícula
        politica = self.sizePolicy()
        politica.setRetainSizeWhenHidden(True)
        self.setSizePolicy(politica)

        self.layout_celda = QVBoxLayout(self)
        self.layout_celda.setContentsMargins(8, 6, 8, 6)
        self.layout_celda.setSpacing(3)
        self.etiqueta_dia = QLabel()
        self.etiqueta_dia.setObjectName("numero_dia")
        self.layout_celda.addWidget(self.etiqueta_dia)
        self.layout_celda.addStretch()
        self.etiquetas = []

    def mostrar(self, dia, eventos, es_hoy):
        """eventos: lista de (texto, color, texto_de_ayuda)."""
        for etiqueta in self.etiquetas:
            # deleteLater() no la borra al momento: la ocultamos y la sacamos del layout ya
            etiqueta.hide()
            self.layout_celda.removeWidget(etiqueta)
            etiqueta.deleteLater()
        self.etiquetas = []

        self.etiqueta_dia.setText(str(dia))
        visibles = eventos[:self.MAXIMO_ETIQUETAS]
        for texto, color, ayuda in visibles:
            self.agregar_etiqueta(texto, color, ayuda)
        if len(eventos) > len(visibles):
            ocultos = eventos[len(visibles):]
            self.agregar_etiqueta(f"+{len(ocultos)} más", "#3a3a3a",
                                  "\n".join(ayuda for _, _, ayuda in ocultos), texto_claro=True)

        self.setProperty("hoy", es_hoy)
        refrescar_estilo(self)

    def agregar_etiqueta(self, texto, color, ayuda, texto_claro=False):
        etiqueta = QLabel(texto)
        etiqueta.setObjectName("chip")
        color_texto = "#f2f2f2" if texto_claro else "#111111"
        etiqueta.setStyleSheet(f"background-color: {color}; color: {color_texto};")
        etiqueta.setToolTip(ayuda)
        # Ignored: un texto largo no ensancha la columna (todas miden lo mismo);
        # si no cabe, pasa a la línea siguiente
        etiqueta.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        etiqueta.setWordWrap(True)
        self.layout_celda.insertWidget(self.layout_celda.count() - 1, etiqueta)   # antes del stretch
        self.etiquetas.append(etiqueta)


class VentanaCalendarioAsistencia(Pagina):
    def __init__(self, cursor):
        super().__init__("Calendario de asistencia",
                         "Quién ha venido cada día. Pasa el ratón por una etiqueta para ver los nombres.")
        self.cursor = cursor
        hoy = date.today()
        self.anio, self.mes = hoy.year, hoy.month

        # --- Filtros y navegación entre meses ---
        self.combo_alumno = QComboBox()
        self.combo_alumno.setMinimumWidth(220)
        self.combo_actividad = QComboBox()
        self.combo_actividad.setMinimumWidth(160)
        self.combo_alumno.currentIndexChanged.connect(self.refrescar)
        self.combo_actividad.currentIndexChanged.connect(self.refrescar)

        self.etiqueta_mes = QLabel()
        self.etiqueta_mes.setObjectName("titulo_seccion")
        self.etiqueta_mes.setMinimumWidth(130)
        self.etiqueta_mes.setAlignment(Qt.AlignCenter)

        barra = QHBoxLayout()
        barra.addWidget(self.combo_alumno)
        barra.addWidget(self.combo_actividad)
        barra.addStretch()
        barra.addWidget(crear_boton("Hoy", self.ir_a_hoy, tipo="secundario"))
        barra.addWidget(crear_boton("‹", lambda: self.cambiar_mes(-1), tipo="secundario"))
        barra.addWidget(self.etiqueta_mes)
        barra.addWidget(crear_boton("›", lambda: self.cambiar_mes(1), tipo="secundario"))
        self.layout_pagina.addLayout(barra)

        # --- Cuadrícula del mes: 7 columnas x 6 semanas ---
        cuadricula = QGridLayout()
        cuadricula.setSpacing(6)
        for columna, letra in enumerate(DIAS_CORTOS):
            cabecera = QLabel(letra)
            cabecera.setObjectName("cabecera_dia")
            cuadricula.addWidget(cabecera, 0, columna)
            cuadricula.setColumnStretch(columna, 1)
        self.celdas = []
        for semana in range(6):
            fila_celdas = []
            for columna in range(7):
                celda_dia = CeldaDia()
                cuadricula.addWidget(celda_dia, semana + 1, columna)
                fila_celdas.append(celda_dia)
            self.celdas.append(fila_celdas)

        # --- Resumen del mes a la derecha ---
        panel = QFrame()
        panel.setObjectName("tarjeta")
        panel.setFixedWidth(360)
        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(20, 16, 20, 16)
        self.titulo_resumen = QLabel()
        self.titulo_resumen.setObjectName("titulo_seccion")
        self.etiqueta_totales = QLabel()
        self.etiqueta_totales.setObjectName("ayuda")
        self.etiqueta_totales.setWordWrap(True)
        self.tabla = QTableWidget()
        self.tabla.setObjectName("tabla_panel")
        configurar_tabla(self.tabla, ["Alumno", "Clases", "Última"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.cellClicked.connect(self.seleccionar_alumno_de_tabla)
        layout_panel.addWidget(self.titulo_resumen)
        layout_panel.addWidget(self.etiqueta_totales)
        layout_panel.addWidget(self.tabla, 1)

        contenido = QHBoxLayout()
        contenido.setSpacing(16)
        contenido.addLayout(cuadricula, 1)
        contenido.addWidget(panel)
        self.layout_pagina.addLayout(contenido, 1)

    # ---------- Carga de datos ----------

    def recargar(self):
        """Recarga los desplegables (manteniendo lo elegido) y vuelve a pintar el mes."""
        self.rellenar_combo(self.combo_alumno, "Todos los alumnos",
                            "SELECT id, nombre || ' ' || apellidos FROM alumno WHERE activo = 1 ORDER BY nombre")
        self.rellenar_combo(self.combo_actividad, "Todas las actividades",
                            "SELECT id, nombre FROM actividades ORDER BY nombre")
        self.refrescar()

    def rellenar_combo(self, combo, texto_todos, consulta):
        seleccionado = combo.currentData()
        combo.blockSignals(True)        # que no se repinte el calendario con cada addItem
        combo.clear()
        combo.addItem(texto_todos, None)
        self.cursor.execute(consulta)
        for id_elemento, nombre in self.cursor.fetchall():
            combo.addItem(nombre, id_elemento)
        combo.setCurrentIndex(max(combo.findData(seleccionado), 0))
        combo.blockSignals(False)

    def refrescar(self, *args):
        nombre_mes = f"{MESES[self.mes - 1].capitalize()} {self.anio}"
        self.etiqueta_mes.setText(nombre_mes)
        id_alumno = self.combo_alumno.currentData()
        id_actividad = self.combo_actividad.currentData()

        asistencias = asistencias_del_mes(self.cursor, self.anio, self.mes, id_alumno, id_actividad)
        self.pintar_calendario(asistencias, un_solo_alumno=id_alumno is not None)
        self.pintar_resumen(nombre_mes, asistencias, id_actividad)

    def pintar_calendario(self, asistencias, un_solo_alumno):
        # por_dia[día][id_actividad] = (nombre de la actividad, [alumnos])
        por_dia = defaultdict(dict)
        for fecha, id_act, actividad, _, alumno in asistencias:
            dia = int(fecha[8:10])
            por_dia[dia].setdefault(id_act, (actividad, []))[1].append(alumno)

        hoy = date.today()
        semanas = calendar.Calendar(firstweekday=0).monthdayscalendar(self.anio, self.mes)
        for indice_semana, fila_celdas in enumerate(self.celdas):
            semana = semanas[indice_semana] if indice_semana < len(semanas) else [0] * 7
            for columna, celda_dia in enumerate(fila_celdas):
                dia = semana[columna]
                if dia == 0:                       # el día pertenece a otro mes
                    celda_dia.hide()
                    continue
                eventos = []
                for id_act, (actividad, alumnos) in por_dia[dia].items():
                    texto = actividad if un_solo_alumno else f"{actividad} · {len(alumnos)}"
                    eventos.append((texto, color_actividad(id_act), f"{actividad}: " + ", ".join(alumnos)))
                es_hoy = (self.anio, self.mes, dia) == (hoy.year, hoy.month, hoy.day)
                celda_dia.mostrar(dia, eventos, es_hoy)
                celda_dia.show()

    def pintar_resumen(self, nombre_mes, asistencias, id_actividad):
        self.titulo_resumen.setText(f"Resumen de {nombre_mes.lower()}")

        filas = asistencia_por_alumno(self.cursor, self.anio, self.mes, id_actividad)
        if self.combo_alumno.currentData() is not None:
            self.etiqueta_totales.setText(
                f"{self.combo_alumno.currentText()}: {plural(len(asistencias), 'asistencia', 'asistencias')} este mes")
        else:
            sin_venir = sum(1 for fila in filas if fila[2] == 0)
            alumnos_distintos = len({fila[3] for fila in asistencias})
            self.etiqueta_totales.setText(
                f"{plural(len(asistencias), 'asistencia', 'asistencias')} · "
                f"{plural(alumnos_distintos, 'alumno ha venido', 'alumnos han venido')} · "
                f"{sin_venir} sin ninguna asistencia")

        self.tabla.setRowCount(len(filas))
        for fila_idx, (id_alumno, alumno, total, ultima) in enumerate(filas):
            item_alumno = celda(alumno)
            item_alumno.setData(Qt.UserRole, id_alumno)
            item_total = celda(total, a_la_derecha=True)
            item_ultima = celda(formatear_fecha(ultima) if ultima else "—")
            if total == 0:                          # en gris los que no han venido
                for item in (item_alumno, item_total, item_ultima):
                    item.setForeground(COLOR_SIN_ASISTENCIA)
            self.tabla.setItem(fila_idx, 0, item_alumno)
            self.tabla.setItem(fila_idx, 1, item_total)
            self.tabla.setItem(fila_idx, 2, item_ultima)

    # ---------- Acciones ----------

    def cambiar_mes(self, salto):
        self.mes += salto
        if self.mes == 0:
            self.anio, self.mes = self.anio - 1, 12
        elif self.mes == 13:
            self.anio, self.mes = self.anio + 1, 1
        self.refrescar()

    def ir_a_hoy(self):
        hoy = date.today()
        self.anio, self.mes = hoy.year, hoy.month
        self.refrescar()

    def seleccionar_alumno_de_tabla(self, fila, columna):
        """Al pulsar un alumno en la tabla, el calendario muestra solo sus asistencias."""
        id_alumno = self.tabla.item(fila, 0).data(Qt.UserRole)
        self.combo_alumno.setCurrentIndex(self.combo_alumno.findData(id_alumno))
