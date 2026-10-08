from PySide6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem

class VentanaCuotasPendientes(QMainWindow):
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor
        self.setWindowTitle("Cuotas Pendientes")

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["Alumno", "Mes", "Importe (€)"])

        self.cursor.execute("""
                                SELECT alumno.nombre || ' ' || alumno.apellidos, cuotas.mes_cuota, cuotas.importe "
                                FROM cuotas 
                                JOIN alumno ON cuotas.id_alumno = alumno.id 
                                WHERE cuotas.pago_realizado = 0
                                ORDER BY cuotas.mes_cuota
                            """)
        filas = self.cursor.fetchall()
        self.tabla.setRowCount(len(filas))
        for fila_idx, fila in enumerate(filas):
            for columna_idx, valor in enumerate(fila):
                self.tabla.setItem(fila_idx, columna_idx, QTableWidgetItem(str(valor)))

        self.setCentralWidget(self.tabla)