import sys
import sqlite3
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from config import RUTA_BD, RUTA_LOGO, leer_estilo
from gui.login import VentanaLogin

if __name__ == "__main__":
    conexion = sqlite3.connect(RUTA_BD)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")                          # mismo aspecto en Windows, Mac y Linux
    app.setWindowIcon(QIcon(str(RUTA_LOGO)))
    app.setStyleSheet(leer_estilo())

    ventana = VentanaLogin(cursor)
    ventana.show()
    sys.exit(app.exec())
