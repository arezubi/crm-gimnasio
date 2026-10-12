import sqlite3
from config import RUTA_BD
from logica.autenticacion import crear_usuario

conexion = sqlite3.connect(RUTA_BD)
cursor = conexion.cursor()

crear_usuario(cursor, "Admin", "admin@gimnasio.com", "admin123", "admin", None)

conexion.commit()
conexion.close()
print("Usuario inicial creado: admin@gimnasio.com / admin123")