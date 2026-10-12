from PySide6.QtWidgets import QComboBox, QMessageBox
from logica.facturas import facturar_cuota
from gui.componentes import FormularioBase, abrir_archivo, formatear_euros, formatear_mes
from informes.factura_pdf import crear_pdf_factura
from db.consultas import id_factura_de_cuota, listar_cuotas_facturables


class VentanaGenerarFactura(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Generar factura",
                         "Solo aparecen las cuotas pagadas que aún no tienen factura. Se crea un PDF en la carpeta facturas/.")
        self.cursor = cursor

        self.combo_cuota = QComboBox()
        self.agregar_campo("Cuota", self.combo_cuota)
        self.agregar_boton("Generar factura", self.generar_factura)

    def recargar(self):
        self.combo_cuota.clear()
        filas = listar_cuotas_facturables(self.cursor)
        for id_cuota, nombre, mes_cuota, importe in filas:
            texto = f"{nombre}  ·  {formatear_mes(mes_cuota)}  ·  {formatear_euros(importe)}"
            self.combo_cuota.addItem(texto, id_cuota)

    def generar_factura(self):
        id_cuota_seleccionada = self.combo_cuota.currentData()
        if id_cuota_seleccionada is None:
            QMessageBox.warning(self, "Aviso", "No hay cuotas pagadas pendientes de facturar.")
            return

        resultado = facturar_cuota(self.cursor, id_cuota_seleccionada)

        if resultado is True:
            self.combo_cuota.removeItem(self.combo_cuota.currentIndex())
            self.crear_y_ofrecer_pdf(id_cuota_seleccionada)
        elif resultado == 'duplicado':
            QMessageBox.warning(self, "Error", "Ya existe una factura para esta cuota.")
        elif resultado == 'no pagada':
            QMessageBox.warning(self, "Error", "La cuota no ha sido pagada. No se puede generar la factura.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo generar la factura.")

    def crear_y_ofrecer_pdf(self, id_cuota):
        id_factura = id_factura_de_cuota(self.cursor, id_cuota)

        try:
            ruta = crear_pdf_factura(self.cursor, id_factura)
        except Exception as e:
            QMessageBox.warning(self, "Factura guardada sin PDF",
                                f"La factura se ha guardado, pero no se pudo crear el PDF:\n{e}\n\n"
                                "Puedes intentarlo de nuevo desde «Facturas emitidas».")
            return

        respuesta = QMessageBox.question(
            self, "Factura generada",
            f"Se ha creado la factura {ruta.stem}.\n\n¿Quieres abrir el PDF?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            abrir_archivo(ruta)
