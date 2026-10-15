import sys
import sqlite3
from PySide6.QtCore import QLocale
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from config import RUTA_BD, RUTA_LOGO, leer_estilo
from db.esquema import crear_tablas
from gui.login import VentanaLogin
from logica.autenticacion import crear_admin_si_no_hay_usuarios

if __name__ == "__main__":
    conexion = sqlite3.connect(RUTA_BD)
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()
    crear_tablas(conexion)
    crear_admin_si_no_hay_usuarios(cursor)

    app = QApplication(sys.argv)
    # Formato español en los campos numéricos (coma decimal, punto de miles),
    # aunque Windows esté configurado en otro idioma
    QLocale.setDefault(QLocale(QLocale.Spanish, QLocale.Spain))
    app.setStyle("Fusion")                          # mismo aspecto en Windows, Mac y Linux
    app.setWindowIcon(QIcon(str(RUTA_LOGO)))
    app.setStyleSheet(leer_estilo())

    ventana = VentanaLogin(cursor)
    ventana.show()
    sys.exit(app.exec())
