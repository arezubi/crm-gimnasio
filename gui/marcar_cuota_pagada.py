from PySide6.QtWidgets import QComboBox, QMessageBox
from db.db import marcar_cuota_pagada
from gui.componentes import FormularioBase, formatear_euros, formatear_mes


class VentanaMarcarCuotaPagada(FormularioBase):
    def __init__(self, cursor):
        super().__init__("Cobrar cuota", "Marca como pagada una cuota pendiente.")
        self.cursor = cursor

        self.combo_cuota = QComboBox()
        self.agregar_campo("Cuota pendiente", self.combo_cuota)
        self.agregar_boton("Marcar como pagada", self.marcar_pagada)

    def recargar(self):
        self.combo_cuota.clear()
        self.cursor.execute("""
            SELECT cuotas.id, alumno.nombre, alumno.apellidos, cuotas.mes_cuota, cuotas.importe
            FROM cuotas
            JOIN alumno ON cuotas.id_alumno = alumno.id
            WHERE cuotas.pago_realizado = 0
            ORDER BY cuotas.mes_cuota, alumno.nombre
        """)
        for id_cuota, nombre, apellidos, mes_cuota, importe in self.cursor.fetchall():
            texto = f"{nombre} {apellidos}  ·  {formatear_mes(mes_cuota)}  ·  {formatear_euros(importe)}"
            self.combo_cuota.addItem(texto, id_cuota)

    def marcar_pagada(self):
        id_cuota = self.combo_cuota.currentData()

        if id_cuota is None:
            QMessageBox.warning(self, "Aviso", "No hay cuotas pendientes.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar pago",
            f"¿Marcar como pagada esta cuota?\n\n{self.combo_cuota.currentText()}",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta != QMessageBox.Yes:
            return

        resultado = marcar_cuota_pagada(self.cursor, id_cuota)

        if resultado is True:
            QMessageBox.information(self, "Éxito", "Cuota marcada como pagada correctamente.")
            self.combo_cuota.removeItem(self.combo_cuota.currentIndex())
        elif resultado == "ya pagada":
            QMessageBox.warning(self, "Aviso", "Esta cuota ya estaba marcada como pagada.")
        else:
            QMessageBox.warning(self, "Error", "No se pudo marcar la cuota como pagada.")
