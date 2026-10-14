from datetime import date
from PySide6.QtWidgets import QComboBox, QMessageBox
from informes.estadisticas import anios_con_datos
from gui.componentes import MESES, FormularioBase, abrir_archivo
from informes.informe_html import generar_informe


class VentanaInformes(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Informes", "Genera un informe anual o mensual y ábrelo en el navegador.")
        self.cursor = cursor

        hoy = date.today()

        self.combo_anio = QComboBox()

        self.combo_mes = QComboBox()
        for numero, nombre_mes in enumerate(MESES, start=1):
            self.combo_mes.addItem(nombre_mes.capitalize(), numero)
        self.combo_mes.setCurrentIndex(hoy.month - 1)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItem("Anual")
        self.combo_tipo.addItem("Mensual")
        self.combo_tipo.currentIndexChanged.connect(self.actualizar_mes)

        self.agregar_campo("Tipo", self.combo_tipo)
        self.agregar_campo("Año", self.combo_anio)
        self.agregar_campo("Mes", self.combo_mes)
        self.agregar_boton("Generar informe", self.generar)

        self.actualizar_mes()

    def recargar(self):
        self.combo_anio.clear()
        for anio in anios_con_datos(self.cursor):
            self.combo_anio.addItem(str(anio), anio)
        if self.combo_anio.count() == 0:                    # sin datos todavía: ofrece el año actual
            self.combo_anio.addItem(str(date.today().year), date.today().year)

    def actualizar_mes(self):
        """El mes solo aparece en el informe mensual."""
        es_mensual = self.combo_tipo.currentIndex() == 1
        self.formulario.setRowVisible(self.combo_mes, es_mensual)

    def generar(self):
        anio = self.combo_anio.currentData()
        mes = self.combo_mes.currentData() if self.combo_tipo.currentIndex() == 1 else None

        try:
            ruta = generar_informe(self.cursor, anio, mes)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el informe:\n{e}")
            return

        abrir_archivo(ruta)