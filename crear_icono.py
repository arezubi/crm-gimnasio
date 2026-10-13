"""Genera assets/icono.ico a partir del logo SVG. Solo hace falta ejecutarlo una vez."""
import sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication
from config import CARPETA_RECURSOS, RUTA_LOGO

app = QApplication(sys.argv)                     # Qt necesita una aplicación para dibujar

TAMANO = 256                                     # el tamaño máximo de un icono de Windows
logo = QIcon(str(RUTA_LOGO)).pixmap(QSize(TAMANO, TAMANO))   # cabe en 256x256 sin deformarse

icono = QPixmap(TAMANO, TAMANO)                  # lienzo cuadrado...
icono.fill(Qt.black)                             # ...con el mismo negro que el fondo del logo
pintor = QPainter(icono)
pintor.drawPixmap((TAMANO - logo.width()) // 2, (TAMANO - logo.height()) // 2, logo)   # centrado
pintor.end()

ruta = CARPETA_RECURSOS / "assets" / "icono.ico"
print("Guardado" if icono.save(str(ruta), "ICO") else "ERROR al guardar", ruta)
