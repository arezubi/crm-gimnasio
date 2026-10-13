import sqlite3
from config import RUTA_BD
from db.esquema import crear_tablas

conexion = sqlite3.connect(RUTA_BD)
crear_tablas(conexion)
conexion.close()