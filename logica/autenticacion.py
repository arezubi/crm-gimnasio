from db.consultas import hay_usuarios, obtener_usuario
import bcrypt
from db.db import registrar_usuario
from config import DATOS_GIMNASIO

def iniciar_sesion(cursor, email, password):
    """Devuelve el rol y nombre si el email y la contraseña son correctos, o None si no lo son."""
    usuario = obtener_usuario(cursor, email)
    if usuario is None:
        return None
    password_hash, rol, nombre = usuario
    if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        return rol, nombre
    else:
        return None

def cifrar_password(password):
    """Devuelve la contraseña cifrada usando bcrypt."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def crear_usuario(cursor, nombre, email, password, rol, id_profesor=None):
    """Crea un nuevo usuario en la base de datos con la contraseña cifrada."""
    password_hash = cifrar_password(password)
    
    return registrar_usuario(cursor, nombre, email, password_hash, rol, id_profesor)

def crear_admin_si_no_hay_usuarios(cursor):
    """Crea un usuario administrador por defecto si no hay ningún usuario en la base de datos."""
    if not hay_usuarios(cursor):
        crear_usuario(cursor, "Admin", "admin@gimnasio.com", "admin123", "admin")