import sqlite3
from config import RUTA_BD
from logica.autenticacion import crear_admin_si_no_hay_usuarios

conexion = sqlite3.connect(RUTA_BD)
cursor = conexion.cursor()

crear_admin_si_no_hay_usuarios(cursor)
conexion.commit()
conexion.close()
print("Usuario inicial creado: admin@gimnasio.com / admin123")