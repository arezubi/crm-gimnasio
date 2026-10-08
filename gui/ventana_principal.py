from PySide6.QtWidgets import QMainWindow
from gui.actividad_mas_usada import VentanaActividadMasUsada
from gui.alumnos_nuevos import VentanaAlumnosNuevos
from gui.cuotas_pendientes import VentanaCuotasPendientes
from gui.inscribir_alumno import VentanaInscribirAlumno
from gui.registrar_asistencia import VentanaRegistrarAsistencia
from gui.registrar_usuario import VentanaRegistrarUsuario
from gui.alta_actividad import VentanaAltaActividad
from gui.alta_alumno import VentanaAltaAlumno
from gui.alta_profesor import VentanaAltaProfesor
from gui.alta_tipo_cuota import VentanaAltaTipoCuota
from gui.baja_alumno import VentanaBajaAlumno
from gui.baja_profesor import VentanaBajaProfesor
from gui.crear_cuota import VentanaCrearCuota
from gui.generar_factura import VentanaGenerarFactura
from gui.listado_alumnos import VentanaListadoAlumnos
from gui.grafico_ingresos import VentanaGraficoIngresos
from gui.marcar_cuota_pagada import VentanaMarcarCuotaPagada
from gui.grafico_ingresos_anual import VentanaGraficoIngresosAnual
from gui.alumnos_nuevos_por_anio import VentanaGraficoAlumnosNuevosPorAnio
from gui.dashboard import PanelDashboard 


class VentanaPrincipal(QMainWindow):
    def __init__(self, cursor, rol):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Ventana Principal")
        self.resize(1000, 700)
        self.ventanas_abiertas = []

        self.barra_menu = self.menuBar()

        menu_alumnos = self.barra_menu.addMenu("Alumnos")
        menu_profesor = self.barra_menu.addMenu("Profesor")
        menu_actividades = self.barra_menu.addMenu("Actividades")
        menu_cuotas = self.barra_menu.addMenu("Cuotas")
        menu_facturas = self.barra_menu.addMenu("Facturas")
        menu_usuario = self.barra_menu.addMenu("Usuario")
        menu_estadisticas = self.barra_menu.addMenu("Estadísticas")

        accion_alta = menu_alumnos.addAction("Alta de alumno")
        accion_alta.triggered.connect(lambda: self.abrir_ventana(VentanaAltaAlumno))

        accion_baja = menu_alumnos.addAction("Baja de alumno")
        accion_baja.triggered.connect(lambda: self.abrir_ventana(VentanaBajaAlumno))

        accion_listado_alumnos = menu_alumnos.addAction("Listado de alumnos")
        accion_listado_alumnos.triggered.connect(lambda: self.abrir_ventana(VentanaListadoAlumnos))

        accion_alta_profesor = menu_profesor.addAction("Alta de profesor")
        accion_alta_profesor.triggered.connect(lambda: self.abrir_ventana(VentanaAltaProfesor))

        accion_baja_profesor = menu_profesor.addAction("Baja de profesor")
        accion_baja_profesor.triggered.connect(lambda: self.abrir_ventana(VentanaBajaProfesor))

        accion_alta_actividad = menu_actividades.addAction("Alta de actividad")
        accion_alta_actividad.triggered.connect(lambda: self.abrir_ventana(VentanaAltaActividad))

        accion_inscribir_alumnos = menu_actividades.addAction("Inscribir alumnos")
        accion_inscribir_alumnos.triggered.connect(lambda: self.abrir_ventana(VentanaInscribirAlumno))

        accion_alta_tipo_cuota = menu_cuotas.addAction("Alta de tipo de cuota")
        accion_alta_tipo_cuota.triggered.connect(lambda: self.abrir_ventana(VentanaAltaTipoCuota))

        accion_alta_cuota = menu_cuotas.addAction("Alta de cuota")
        accion_alta_cuota.triggered.connect(lambda: self.abrir_ventana(VentanaCrearCuota))

        accion_registrar_asistencia = menu_actividades.addAction("Registrar asistencia")
        accion_registrar_asistencia.triggered.connect(lambda: self.abrir_ventana(VentanaRegistrarAsistencia))

        accion_generar_factura = menu_facturas.addAction("Generar factura")
        accion_generar_factura.triggered.connect(lambda: self.abrir_ventana(VentanaGenerarFactura))

        accion_registrar_usuario = menu_usuario.addAction("Registrar usuario")
        accion_registrar_usuario.triggered.connect(lambda: self.abrir_ventana(VentanaRegistrarUsuario))    

        accion_cuotas_pendientes = menu_cuotas.addAction("Cuotas pendientes")
        accion_cuotas_pendientes.triggered.connect(lambda: self.abrir_ventana(VentanaCuotasPendientes))

        accion_marcar_pagadas = menu_cuotas.addAction("Marcar cuota pagada")
        accion_marcar_pagadas.triggered.connect(lambda: self.abrir_ventana(VentanaMarcarCuotaPagada))

        accion_actividad_mas_usada = menu_estadisticas.addAction("Actividad más usada")
        accion_actividad_mas_usada.triggered.connect(lambda: self.abrir_ventana(VentanaActividadMasUsada))

        accion_alumnos_nuevos_mes = menu_estadisticas.addAction("Alumnos nuevos por mes")
        accion_alumnos_nuevos_mes.triggered.connect(lambda: self.abrir_ventana(VentanaAlumnosNuevos))

        accion_alumnos_nuevos_anio = menu_estadisticas.addAction("Alumnos nuevos por año")
        accion_alumnos_nuevos_anio.triggered.connect(lambda: self.abrir_ventana(VentanaGraficoAlumnosNuevosPorAnio))

        accion_grafico_ingresos = menu_estadisticas.addAction("Ingresos por mes")
        accion_grafico_ingresos.triggered.connect(lambda: self.abrir_ventana(VentanaGraficoIngresos))

        accion_grafico_ingresos_anual = menu_estadisticas.addAction("Ingresos por año")
        accion_grafico_ingresos_anual.triggered.connect(lambda: self.abrir_ventana(VentanaGraficoIngresosAnual)) 

        self.setCentralWidget(PanelDashboard(cursor))
        if rol != "admin":
            menu_usuario.menuAction().setVisible(False)

    def abrir_ventana(self, ClaseVentana):
        ventana = ClaseVentana(self.cursor)
        ventana.show()
        self.ventanas_abiertas.append(ventana)