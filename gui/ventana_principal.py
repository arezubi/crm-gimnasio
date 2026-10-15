from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QStackedWidget, QTabWidget, QVBoxLayout, QWidget,
)
from config import RUTA_LOGO
from gui.componentes import MarcoClicable, crear_boton
from gui.dashboard import PanelDashboard
from gui.informes import VentanaInformes
from gui.listado_alumnos import VentanaListadoAlumnos
from gui.alta_profesor import VentanaAltaProfesor
from gui.baja_profesor import VentanaBajaProfesor
from gui.alta_actividad import VentanaAltaActividad
from gui.inscribir_alumno import VentanaInscribirAlumno
from gui.listado_gastos import VentanaListadoGastos
from gui.nuevo_gasto import VentanaGenerarGasto
from gui.registrar_asistencia import VentanaRegistrarAsistencia
from gui.calendario_asistencia import VentanaCalendarioAsistencia
from gui.cuotas_pendientes import VentanaCuotasPendientes
from gui.crear_cuota import VentanaCrearCuota
from gui.alta_tipo_cuota import VentanaAltaTipoCuota
from gui.generar_factura import VentanaGenerarFactura
from gui.listado_facturas import VentanaListadoFacturas
from gui.grafico_ingresos import VentanaGraficoIngresos
from gui.grafico_ingresos_anual import VentanaGraficoIngresosAnual
from gui.alumnos_nuevos import VentanaAlumnosNuevos
from gui.alumnos_nuevos_por_anio import VentanaGraficoAlumnosNuevosPorAnio
from gui.actividad_mas_usada import VentanaActividadMasUsada
from gui.registrar_usuario import VentanaRegistrarUsuario

NOMBRES_ROL = {"admin": "Administrador", "operador": "Operador"}


class VentanaPrincipal(QMainWindow):
    """Una sola ventana: barra lateral con las secciones a la izquierda
    y, a la derecha, un QStackedWidget que muestra la sección elegida."""

    def __init__(self, cursor, rol, nombre_usuario="Usuario"):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Spartan Team · CRM Gimnasio")
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)

        # --- Barra lateral ---
        barra_lateral = QFrame()
        barra_lateral.setObjectName("barra_lateral")
        barra_lateral.setFixedWidth(230)
        self.layout_menu = QVBoxLayout(barra_lateral)
        self.layout_menu.setContentsMargins(16, 24, 16, 16)
        self.layout_menu.setSpacing(4)

        # Logo y nombre: al pulsarlos se vuelve al inicio
        bloque_marca = MarcoClicable()
        bloque_marca.setToolTip("Ir al inicio")
        layout_marca = QVBoxLayout(bloque_marca)
        layout_marca.setContentsMargins(0, 0, 0, 0)
        layout_marca.setSpacing(4)
        logo = QLabel()
        logo.setPixmap(QIcon(str(RUTA_LOGO)).pixmap(QSize(80, 120)))
        logo.setAlignment(Qt.AlignCenter)
        marca = QLabel("SPARTAN TEAM")
        marca.setObjectName("marca")
        marca.setAlignment(Qt.AlignCenter)
        marca_sub = QLabel("CRM Gimnasio")
        marca_sub.setObjectName("marca_sub")
        marca_sub.setAlignment(Qt.AlignCenter)
        layout_marca.addWidget(logo)
        layout_marca.addWidget(marca)
        layout_marca.addWidget(marca_sub)
        self.layout_menu.addWidget(bloque_marca)
        self.layout_menu.addSpacing(24)

        # --- Zona central ---
        self.paginas = QStackedWidget()
        self.grupo_botones = QButtonGroup(self)   # solo un botón marcado a la vez
        self.secciones = {}                       # nombre -> (botón, contenedor)

        # --- Secciones: (texto de la pestaña, página) ---
        dashboard = PanelDashboard(cursor, nombre_usuario)
        dashboard.ir_a.connect(self.ir_a)
        boton_inicio = self.agregar_seccion("Inicio", [
            ("Inicio", dashboard),
        ])
        self.agregar_seccion("Alumnos", [
            ("Listado", VentanaListadoAlumnos(cursor))
        ])
        self.agregar_seccion("Profesores", [
            ("Alta", VentanaAltaProfesor(cursor)),
            ("Baja", VentanaBajaProfesor(cursor)),
        ])
        self.agregar_seccion("Actividades", [
            ("Nueva actividad", VentanaAltaActividad(cursor)),
            ("Inscripciones", VentanaInscribirAlumno(cursor)),
            ("Pasar lista", VentanaRegistrarAsistencia(cursor)),
            ("Calendario de asistencia", VentanaCalendarioAsistencia(cursor)),
        ])
        self.agregar_seccion("Cuotas", [
            ("Cuotas del mes", VentanaCuotasPendientes(cursor)),
            ("Nueva cuota", VentanaCrearCuota(cursor)),
            ("Tipos de cuota", VentanaAltaTipoCuota(cursor)),
        ])
        self.agregar_seccion("Facturas", [
            ("Generar factura", VentanaGenerarFactura(cursor)),
            ("Facturas emitidas", VentanaListadoFacturas(cursor)),
        ])
        self.agregar_seccion("Estadísticas", [
            ("Ingresos por mes", VentanaGraficoIngresos(cursor)),
            ("Ingresos por año", VentanaGraficoIngresosAnual(cursor)),
            ("Altas por mes", VentanaAlumnosNuevos(cursor)),
            ("Altas por año", VentanaGraficoAlumnosNuevosPorAnio(cursor)),
            ("Actividades", VentanaActividadMasUsada(cursor)),
            ("Informes", VentanaInformes(cursor)),
        ])
        if rol == "admin":
            self.agregar_seccion("Usuarios", [
                ("Nuevo usuario", VentanaRegistrarUsuario(cursor)),
            ])
            self.agregar_seccion("Gastos", [
                ("Nuevo gasto", VentanaGenerarGasto(cursor)),
                ("Listado", VentanaListadoGastos(cursor)),
            ])

        # --- Pie de la barra lateral: usuario y cerrar sesión ---
        self.layout_menu.addStretch()
        separador = QFrame()
        separador.setObjectName("separador")
        self.layout_menu.addWidget(separador)
        self.layout_menu.addSpacing(8)
        etiqueta_nombre = QLabel(nombre_usuario)
        etiqueta_nombre.setObjectName("pie_nombre")
        etiqueta_rol = QLabel(NOMBRES_ROL.get(rol, rol))
        etiqueta_rol.setObjectName("pie_rol")
        self.layout_menu.addWidget(etiqueta_nombre)
        self.layout_menu.addWidget(etiqueta_rol)
        self.layout_menu.addSpacing(8)
        self.layout_menu.addWidget(crear_boton("Cerrar sesión", self.cerrar_sesion, tipo="secundario"))

        contenedor = QWidget()
        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(barra_lateral)
        layout.addWidget(self.paginas, 1)
        self.setCentralWidget(contenedor)

        bloque_marca.clicked.connect(boton_inicio.click)
        boton_inicio.click()

    def agregar_seccion(self, nombre, paginas):
        """Crea el botón de la barra lateral y su página.
        Si la sección tiene varias páginas, las pone en pestañas."""
        if len(paginas) == 1:
            contenedor = paginas[0][1]
        else:
            contenedor = QTabWidget()
            for titulo, pagina in paginas:
                contenedor.addTab(pagina, titulo)
            contenedor.currentChanged.connect(self.recargar_pagina_actual)
        self.paginas.addWidget(contenedor)

        boton = QPushButton(nombre)
        boton.setObjectName("boton_menu")
        boton.setCheckable(True)
        boton.setCursor(Qt.PointingHandCursor)
        boton.clicked.connect(lambda: self.mostrar_seccion(contenedor))
        self.grupo_botones.addButton(boton)
        self.layout_menu.addWidget(boton)
        self.secciones[nombre] = (boton, contenedor)
        return boton

    def ir_a(self, seccion, pestana):
        """Abre una sección y, si tiene pestañas, la pestaña con ese título."""
        if seccion not in self.secciones:      # p. ej. una sección solo para admin
            return
        boton, contenedor = self.secciones[seccion]
        if isinstance(contenedor, QTabWidget):
            for indice in range(contenedor.count()):
                if contenedor.tabText(indice) == pestana:
                    contenedor.blockSignals(True)      # que no recargue ahora: lo hace el click de abajo
                    contenedor.setCurrentIndex(indice)
                    contenedor.blockSignals(False)
                    break
        boton.click()

    def mostrar_seccion(self, contenedor):
        self.paginas.setCurrentWidget(contenedor)
        self.recargar_pagina_actual()

    def recargar_pagina_actual(self, *args):
        """Cada vez que se muestra una página, vuelve a leer la base de datos.
        Así los datos nunca se quedan desactualizados."""
        pagina = self.paginas.currentWidget()
        if isinstance(pagina, QTabWidget):
            pagina = pagina.currentWidget()
        try:
            pagina.recargar()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar esta pantalla:\n\n{e}")

    def cerrar_sesion(self):
        from gui.login import VentanaLogin   # import aquí dentro: login.py ya importa este fichero
        self.ventana_login = VentanaLogin(self.cursor)
        self.ventana_login.show()
        self.close()
