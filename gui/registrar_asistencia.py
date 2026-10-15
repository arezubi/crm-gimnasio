from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import QComboBox, QDateEdit, QHBoxLayout, QLabel, QMessageBox, QTableWidget
from logica.asistencia import registrar_asistencia
from db.consultas import asistentes_del_dia, listar_actividades, listar_inscritos
from gui.componentes import Pagina, celda, configurar_tabla, crear_boton


class VentanaRegistrarAsistencia(Pagina):
    def __init__(self, cursor):
        super().__init__("Pasar lista", "Marca los alumnos que han venido a clase y pulsa Guardar.")
        self.cursor = cursor
        self.asistentes = set()          # ids que ya tenían asistencia ese día

        self.combo_actividad = QComboBox()
        self.combo_actividad.setMinimumWidth(220)
        self.campo_fecha = QDateEdit(QDate.currentDate())
        self.campo_fecha.setDisplayFormat("dd/MM/yyyy")
        self.campo_fecha.setCalendarPopup(True)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")

        fila = QHBoxLayout()
        fila.addWidget(QLabel("Actividad:"))
        fila.addWidget(self.combo_actividad)
        fila.addSpacing(16)
        fila.addWidget(QLabel("Fecha:"))
        fila.addWidget(self.campo_fecha)
        fila.addStretch()
        fila.addWidget(self.etiqueta_resumen)
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Alumno"])
        self.layout_pagina.addWidget(self.tabla, 1)

        botonera = QHBoxLayout()
        botonera.addStretch()
        botonera.addWidget(crear_boton("Marcar todos", self.marcar_todos, tipo="secundario"))
        botonera.addWidget(crear_boton("Guardar", self.guardar))
        self.layout_pagina.addLayout(botonera)

        # Se conectan al final, cuando la tabla ya existe
        self.combo_actividad.currentIndexChanged.connect(self.cargar_alumnos)
        self.campo_fecha.dateChanged.connect(self.cargar_alumnos)

    def recargar(self):
        actividad_anterior = self.combo_actividad.currentData()
        self.combo_actividad.blockSignals(True)      # que no cargue la lista con cada addItem
        self.combo_actividad.clear()
        for id_actividad, nombre in listar_actividades(self.cursor):
            self.combo_actividad.addItem(nombre, id_actividad)
        indice = self.combo_actividad.findData(actividad_anterior)
        self.combo_actividad.setCurrentIndex(max(indice, 0))
        self.combo_actividad.blockSignals(False)
        self.campo_fecha.setMaximumDate(QDate.currentDate())
        self.cargar_alumnos()

    def cargar_alumnos(self, *args):
        id_actividad = self.combo_actividad.currentData()
        if id_actividad is None:
            self.tabla.setRowCount(0)
            self.etiqueta_resumen.setText("")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        self.asistentes = asistentes_del_dia(self.cursor, id_actividad, fecha)
        inscritos = listar_inscritos(self.cursor, id_actividad)

        self.tabla.setRowCount(len(inscritos))
        for fila, (id_alumno, nombre) in enumerate(inscritos):
            item = celda(nombre)
            item.setData(Qt.UserRole, id_alumno)                      # el id va escondido en la celda
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)      # que tenga casilla
            if id_alumno in self.asistentes:
                item.setCheckState(Qt.Checked)
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)       # en gris: ya guardado
            else:
                item.setCheckState(Qt.Unchecked)
            self.tabla.setItem(fila, 0, item)

        ya_vinieron = sum(1 for id_alumno, _ in inscritos if id_alumno in self.asistentes)
        self.etiqueta_resumen.setText(f"{ya_vinieron} de {len(inscritos)} han venido")

    def marcar_todos(self):
        for fila in range(self.tabla.rowCount()):
            self.tabla.item(fila, 0).setCheckState(Qt.Checked)

    def guardar(self):
        id_actividad = self.combo_actividad.currentData()
        if id_actividad is None:
            QMessageBox.warning(self, "Aviso", "No hay ninguna actividad seleccionada.")
            return

        fecha = self.campo_fecha.date().toString("yyyy-MM-dd")
        guardadas = 0
        fallidas = 0
        for fila in range(self.tabla.rowCount()):
            item = self.tabla.item(fila, 0)
            id_alumno = item.data(Qt.UserRole)
            if item.checkState() == Qt.Checked and id_alumno not in self.asistentes:
                resultado = registrar_asistencia(self.cursor, id_alumno, id_actividad, fecha)
                if resultado is True:
                    guardadas += 1
                else:
                    fallidas += 1

        if guardadas == 0 and fallidas == 0:
            QMessageBox.information(self, "Sin cambios", "No hay asistencias nuevas que guardar.")
            return

        mensaje = f"Asistencias guardadas: {guardadas}"
        if fallidas:
            mensaje += f"\nNo se pudieron guardar: {fallidas}"
        QMessageBox.information(self, "Asistencia", mensaje)
        self.cargar_alumnos()      # los recién guardados pasan a gris