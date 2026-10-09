from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QTableWidget
from config import CARPETA_FACTURAS
from gui.componentes import (
    Pagina, abrir_archivo, celda, configurar_tabla, crear_boton,
    formatear_euros, formatear_fecha, formatear_mes, plural,
)
from informes.factura_pdf import numero_factura, ruta_pdf_existente


class VentanaListadoFacturas(Pagina):
    def __init__(self, cursor):
        super().__init__("Facturas emitidas", "Haz doble clic en una factura para abrir su PDF.")
        self.cursor = cursor

        self.etiqueta_resumen = QLabel()
        self.etiqueta_resumen.setObjectName("resumen")
        fila = QHBoxLayout()
        fila.addWidget(self.etiqueta_resumen)
        fila.addStretch()
        fila.addWidget(crear_boton("Abrir carpeta", self.abrir_carpeta, tipo="secundario"))
        fila.addWidget(crear_boton("Abrir PDF", self.abrir_pdf))
        self.layout_pagina.addLayout(fila)

        self.tabla = QTableWidget()
        configurar_tabla(self.tabla, ["Nº factura", "Fecha", "Alumno", "Concepto", "Importe"])
        self.tabla.cellDoubleClicked.connect(self.abrir_pdf)
        self.layout_pagina.addWidget(self.tabla, 1)

    def recargar(self):
        self.cursor.execute("""
            SELECT factura.id, factura.fecha_factura, alumno.nombre || ' ' || alumno.apellidos,
                   tipo_cuota.nombre, cuotas.mes_cuota, cuotas.importe
            FROM factura
            JOIN cuotas ON factura.id_cuota = cuotas.id
            JOIN alumno ON factura.id_alumno = alumno.id
            JOIN tipo_cuota ON cuotas.id_tipo_cuota = tipo_cuota.id
            ORDER BY factura.id DESC
        """)
        filas = self.cursor.fetchall()

        self.tabla.setRowCount(len(filas))
        total = 0
        for fila_idx, (id_factura, fecha, alumno, tipo, mes, importe) in enumerate(filas):
            numero = celda(numero_factura(id_factura, fecha))
            numero.setData(Qt.UserRole, id_factura)       # guardamos el id para saber qué PDF abrir
            self.tabla.setItem(fila_idx, 0, numero)
            self.tabla.setItem(fila_idx, 1, celda(formatear_fecha(fecha)))
            self.tabla.setItem(fila_idx, 2, celda(alumno))
            self.tabla.setItem(fila_idx, 3, celda(f"Cuota {tipo} · {formatear_mes(mes)}"))
            self.tabla.setItem(fila_idx, 4, celda(formatear_euros(importe), a_la_derecha=True))
            total += importe

        self.etiqueta_resumen.setText(f"{plural(len(filas), 'factura', 'facturas')} · {formatear_euros(total)} facturado")

    def abrir_pdf(self, *args):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona una factura de la tabla.")
            return
        id_factura = self.tabla.item(fila, 0).data(Qt.UserRole)
        try:
            abrir_archivo(ruta_pdf_existente(self.cursor, id_factura))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo crear el PDF:\n{e}")

    def abrir_carpeta(self):
        """Antes de abrir la carpeta, crea los PDF que falten (por ejemplo, los de las
        facturas de datos_prueba.py), para que la carpeta tenga todas las facturas de la tabla."""
        CARPETA_FACTURAS.mkdir(exist_ok=True)
        try:
            for fila in range(self.tabla.rowCount()):
                ruta_pdf_existente(self.cursor, self.tabla.item(fila, 0).data(Qt.UserRole))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron crear algunos PDF:\n{e}")
        abrir_archivo(CARPETA_FACTURAS)
