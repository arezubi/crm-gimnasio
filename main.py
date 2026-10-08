import sys
import sqlite3
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.login import VentanaLogin

if __name__ == "__main__":
    conexion = sqlite3.connect("gimnasio.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    app = QApplication(sys.argv)

    ruta_qss = Path(__file__).parent / "resources" / "estilo.qss"
    app.setStyleSheet(ruta_qss.read_text(encoding="utf-8"))

    ventana = VentanaLogin(cursor)
    ventana.show()
    sys.exit(app.exec())