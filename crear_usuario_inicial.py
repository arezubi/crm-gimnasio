import sqlite3
from config import RUTA_BD
import bcrypt

conexion = sqlite3.connect(RUTA_BD)
cursor = conexion.cursor()

password = "admin123"   # cámbialo luego por uno de verdad
hash_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

cursor.execute("""
    INSERT INTO usuarios (nombre, email, password, rol, id_profesor)
    VALUES (?, ?, ?, ?, ?)
""", ("Admin", "admin@gimnasio.com", hash_password, "admin", None))

conexion.commit()
conexion.close()
print("Usuario inicial creado: admin@gimnasio.com / admin123")