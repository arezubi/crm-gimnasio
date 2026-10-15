
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QTableWidget
from db.db import baja_profesor
from gui.alta_profesor import VentanaAltaProfesor
from gui.componentes import Pagina, abrir_en_dialogo, celda, configurar_tabla, crear_boton, poner_botones_fila
from db.consultas import listar_profesores
from gui.editar_profesor import VentanaEditarProfesor

class VentanaListadoProfesores(Pagina):
    def __init__(self, cursor):
        super().__init__("Profesores", "Profesores activos.")
        self.cursor = cursor
        self.actividades = {}

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
        fila.addWidget(crear_boton("+ Nuevo profesor", self.nuevo_profesor))
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Nombre", "Apellidos", "Email", "Teléfono", "Actividades", ""])
        # Nombre, apellidos, email y teléfono se ajustan a su contenido;
        # las actividades se quedan con todo el espacio que sobra
        for columna in range(0, 4):
            self.tabla.horizontalHeader().setSectionResizeMode(columna, QHeaderView.ResizeToContents)
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        filas = listar_profesores(self.cursor)
        self.actividades = {}
        self.tabla.setRowCount(0)  
        self.tabla.setRowCount(len(filas))
        for fila_idx, (id_profesor, nombre, apellidos, email, telefono, actividades) in enumerate(filas):
            self.actividades[id_profesor] = actividades
            self.tabla.setItem(fila_idx, 0, celda(nombre))
            self.tabla.setItem(fila_idx, 1, celda(apellidos))
            self.tabla.setItem(fila_idx, 2, celda(email))
            self.tabla.setItem(fila_idx, 3, celda(telefono))
            celda_actividades = celda(actividades or "—")
            celda_actividades.setToolTip(actividades or "")     # la lista entera al pasar el ratón
            self.tabla.setItem(fila_idx, 4, celda_actividades)
            poner_botones_fila(self.tabla, fila_idx, 5, id_profesor,
                            ("📝", self.editar_profesor, "secundario", "Editar profesor"),
                            ("🗑️", self.dar_de_baja, "peligro", "Dar de baja"))

            
        self.etiqueta_resumen.setText(f"{len(filas)} profesores activos")
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

    def nuevo_profesor(self):
        pagina = VentanaAltaProfesor(self.cursor)
        if abrir_en_dialogo(self, pagina, "Nuevo profesor"):
            self.recargar()

    def editar_profesor(self, id_profesor):
        pagina = VentanaEditarProfesor(self.cursor)
        pagina.cargar_profesor(id_profesor)
        if abrir_en_dialogo(self, pagina, "Editar profesor"):
            self.recargar()

    def dar_de_baja(self, id_profesor):
        actividades = self.actividades.get(id_profesor)
        pregunta = "¿Seguro que quieres dar de baja a este profesor?"
        if actividades:
            pregunta = f"Este profesor da {actividades}.\n\n" + pregunta
        respuesta = QMessageBox.question(
            self, "Confirmar baja", pregunta,
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return

        if baja_profesor(self.cursor, id_profesor):
            self.recargar()
        else:
            QMessageBox.critical(self, "Error", "Error al dar de baja al profesor.")
